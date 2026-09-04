from rest_framework import serializers

from employees.serializers import EmployeeMiniSerializer

from .models import HRReview, LeaveApproval, LeaveRequest


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_detail = EmployeeMiniSerializer(source="employee", read_only=True)
    pengalihan_kepada_detail = EmployeeMiniSerializer(source="pengalihan_kepada", read_only=True)

    class Meta:
        model = LeaveRequest
        fields = [
            "id", "employee", "employee_detail",
            "jenis_cuti", "keterangan_cuti_khusus",
            "tanggal_cuti", "jumlah_hari",
            "pengalihan_kepada", "pengalihan_kepada_detail", "pengalihan_status",
            "pengalihan_catatan", "pengalihan_tanggal_respon",
            "masuk_kerja_pada_tanggal", "kontak_selama_cuti", "keperluan_cuti",
            "tanggal_pengajuan", "status", "created_at", "updated_at",
        ]
        read_only_fields = [
            "employee", "pengalihan_status", "pengalihan_catatan",
            "pengalihan_tanggal_respon", "tanggal_pengajuan", "status",
            "created_at", "updated_at",
        ]

    def validate(self, attrs):
        jenis_cuti = attrs.get("jenis_cuti", getattr(self.instance, "jenis_cuti", None))
        keterangan = attrs.get(
            "keterangan_cuti_khusus", getattr(self.instance, "keterangan_cuti_khusus", None)
        )
        if jenis_cuti == LeaveRequest.JenisCuti.KHUSUS and not keterangan:
            raise serializers.ValidationError(
                {"keterangan_cuti_khusus": "Wajib diisi kalau jenis cuti = Cuti Khusus."}
            )
        return attrs


class PengalihanResponseSerializer(serializers.Serializer):
    setuju = serializers.BooleanField()
    catatan = serializers.CharField(required=False, allow_blank=True, default="")


class LeaveApprovalActionSerializer(serializers.Serializer):
    setuju = serializers.BooleanField()
    catatan = serializers.CharField(required=False, allow_blank=True, default="")


class LeaveApprovalSerializer(serializers.ModelSerializer):
    leave_request_detail = LeaveRequestSerializer(source="leave_request", read_only=True)
    required_approver_detail = EmployeeMiniSerializer(source="required_approver", read_only=True)
    approver_detail = EmployeeMiniSerializer(source="approver", read_only=True)

    class Meta:
        model = LeaveApproval
        fields = [
            "id", "leave_request", "leave_request_detail",
            "required_approver", "required_approver_detail", "required_role",
            "approver", "approver_detail", "status", "catatan", "tanggal_approval",
        ]
        read_only_fields = fields


class HRReviewSerializer(serializers.ModelSerializer):
    leave_request_detail = LeaveRequestSerializer(source="leave_request", read_only=True)

    class Meta:
        model = HRReview
        fields = [
            "id", "leave_request", "leave_request_detail",
            "hak_saldo_cuti_saat_ini", "pengajuan_total_cuti", "sisa_saldo_cuti",
            "hr_pic", "tanggal_review", "catatan",
        ]
        read_only_fields = ["hr_pic", "tanggal_review", "leave_request_detail"]