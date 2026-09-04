from django.db import transaction
from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import HRReview, LeaveApproval, LeaveRequest
from .permissions import HasEmployeeProfile, IsHR, IsManagerOrBOD
from .serializers import (
    HRReviewSerializer,
    LeaveApprovalActionSerializer,
    LeaveApprovalSerializer,
    LeaveRequestSerializer,
    PengalihanResponseSerializer,
)
from .services import konfirmasi_pengalihan, proses_approval, resubmit_setelah_revisi, route_approval


class LeaveRequestViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated, HasEmployeeProfile]

    def get_queryset(self):
        qs = LeaveRequest.objects.select_related("employee", "pengalihan_kepada").all()
        user = self.request.user
        if user.role in ("hr", "admin"):
            return qs
        # Milik sendiri, ATAU dia yang ditunjuk buat pengalihan kerjaan
        return qs.filter(Q(employee=user.employee) | Q(pengalihan_kepada=user.employee))

    def perform_create(self, serializer):
        employee = self.request.user.employee
        leave_request = serializer.save(employee=employee)
        if leave_request.pengalihan_kepada_id:
            leave_request.status = LeaveRequest.Status.MENUNGGU_KONFIRMASI_PENGALIHAN
            leave_request.save(update_fields=["status"])
        else:
            route_approval(leave_request)

    def perform_update(self, serializer):
        instance = serializer.instance
        if instance.status != LeaveRequest.Status.DRAFT:
            raise ValidationError(
                "Pengajuan cuma bisa diedit selagi status 'draft' (habis pengalihan ditolak rekan)."
            )
        pengalihan_lama_id = instance.pengalihan_kepada_id
        updated = serializer.save()
        if updated.pengalihan_kepada_id != pengalihan_lama_id:
            resubmit_setelah_revisi(updated)

    @action(detail=True, methods=["post"], url_path="konfirmasi-pengalihan")
    def konfirmasi_pengalihan(self, request, pk=None):
        leave_request = self.get_object()
        user = request.user

        if leave_request.pengalihan_kepada_id != getattr(user, "employee_id", None):
            return Response(
                {"detail": "Cuma rekan yang ditunjuk pengalihan yang boleh konfirmasi ini."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if leave_request.pengalihan_status != LeaveRequest.PengalihanStatus.PENDING:
            return Response(
                {"detail": "Pengalihan ini sudah direspon sebelumnya."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payload = PengalihanResponseSerializer(data=request.data)
        payload.is_valid(raise_exception=True)

        with transaction.atomic():
            leave_request = konfirmasi_pengalihan(
                leave_request,
                setuju=payload.validated_data["setuju"],
                catatan=payload.validated_data.get("catatan", ""),
            )
        return Response(LeaveRequestSerializer(leave_request).data)


class LeaveApprovalViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LeaveApprovalSerializer
    permission_classes = [permissions.IsAuthenticated, IsManagerOrBOD, HasEmployeeProfile]

    def get_queryset(self):
        user = self.request.user
        qs = LeaveApproval.objects.select_related(
            "leave_request", "leave_request__employee", "required_approver", "approver"
        )
        if user.role == "admin":
            return qs
        employee_id = user.employee_id
        return qs.filter(
            Q(required_approver_id=employee_id)
            | (
                Q(required_role=LeaveApproval.RequiredRole.BOD)
                & ~Q(leave_request__employee_id=employee_id)
            )
        )

    @action(detail=True, methods=["post"])
    def proses(self, request, pk=None):
        payload = LeaveApprovalActionSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        approver_employee = request.user.employee

        with transaction.atomic():
            approval = LeaveApproval.objects.select_for_update().get(pk=pk)

            if approval.status != LeaveApproval.Status.PENDING:
                return Response(
                    {"detail": "Approval ini sudah diproses (mungkin oleh orang lain)."},
                    status=status.HTTP_409_CONFLICT,
                )

            is_direct_target = approval.required_approver_id == approver_employee.id
            is_open_pool_bod = (
                approval.required_role == LeaveApproval.RequiredRole.BOD
                and approval.leave_request.employee_id != approver_employee.id
                and request.user.role == "bod"
            )
            if not (is_direct_target or is_open_pool_bod):
                return Response(
                    {"detail": "Lo bukan approver yang berwenang untuk pengajuan ini."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            approval = proses_approval(
                approval,
                approver_employee=approver_employee,
                setuju=payload.validated_data["setuju"],
                catatan=payload.validated_data.get("catatan", ""),
            )
        return Response(LeaveApprovalSerializer(approval).data)


class HRReviewViewSet(viewsets.ModelViewSet):
    queryset = HRReview.objects.select_related("leave_request", "hr_pic").all()
    serializer_class = HRReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsHR, HasEmployeeProfile]

    def perform_create(self, serializer):
        from django.utils import timezone

        hr_review = serializer.save(hr_pic=self.request.user.employee, tanggal_review=timezone.now())
        leave_request = hr_review.leave_request
        leave_request.status = LeaveRequest.Status.SELESAI
        leave_request.save(update_fields=["status", "updated_at"])