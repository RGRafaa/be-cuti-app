from django.db.models import Q
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import HRReview, LeaveApproval, LeaveRequest
from .permissions import HasEmployeeProfile
from .serializers import LeaveRequestSerializer


class DashboardView(APIView):
    """
    GET /api/leaves/dashboard/
    Ringkasan buat halaman Dashboard: pengajuan aktif milik user, dan
    jumlah item yang perlu direspon (beda-beda tergantung role).
    """

    permission_classes = [permissions.IsAuthenticated, HasEmployeeProfile]

    def get(self, request):
        user = request.user
        employee = user.employee

        pengajuan_aktif = LeaveRequest.objects.filter(employee=employee).exclude(
            status__in=[LeaveRequest.Status.SELESAI, LeaveRequest.Status.DITOLAK]
        ) #semua LeaveRequest milik user yang login kecuali statusnya yang udah final/ditolak

        menunggu_konfirmasi_saya = LeaveRequest.objects.filter(
            pengalihan_kepada=employee,
            pengalihan_status=LeaveRequest.PengalihanStatus.PENDING,
        ).count()

        menunggu_approval_saya = 0
        if user.role in ("manager", "bod", "admin"):
            menunggu_approval_saya = LeaveApproval.objects.filter(
                Q(required_approver=employee)
                | (
                    Q(required_role=LeaveApproval.RequiredRole.BOD)
                    & ~Q(leave_request__employee=employee)
                ),
                status=LeaveApproval.Status.PENDING,
            ).count()

        menunggu_hr_review = 0
        if user.role in ("hr", "admin"):
            menunggu_hr_review = LeaveRequest.objects.filter(
                status=LeaveRequest.Status.DISETUJUI, hr_review__isnull=True
            ).count() #nyari pengajuan yang udah disetujui hr tapi belum sempet isi reviewnya

        return Response({
            "pengajuan_aktif": LeaveRequestSerializer(pengajuan_aktif, many=True).data,
            "menunggu_konfirmasi_pengalihan_saya": menunggu_konfirmasi_saya,
            "menunggu_approval_saya": menunggu_approval_saya,
            "menunggu_hr_review": menunggu_hr_review,
        })