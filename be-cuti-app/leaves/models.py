from django.db import models

from employees.models import Employee


class LeaveRequest(models.Model):
    class JenisCuti(models.TextChoices):
        TAHUNAN = "tahunan", "Cuti Tahunan"
        SAKIT = "sakit", "Cuti Sakit"
        KHUSUS = "khusus", "Cuti Khusus"

    class PengalihanStatus(models.TextChoices):
        PENDING = "pending", "Menunggu Konfirmasi"
        DISETUJUI = "disetujui", "Disetujui"
        DITOLAK = "ditolak", "Ditolak"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft (revisi pengalihan)"
        MENUNGGU_KONFIRMASI_PENGALIHAN = (
            "menunggu_konfirmasi_pengalihan",
            "Menunggu Konfirmasi Pengalihan",
        )
        DIAJUKAN = "diajukan", "Diajukan"
        DISETUJUI = "disetujui", "Disetujui"
        DITOLAK = "ditolak", "Ditolak"
        SELESAI = "selesai", "Selesai"

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="leave_requests"
    )
    jenis_cuti = models.CharField(max_length=20, choices=JenisCuti.choices)
    keterangan_cuti_khusus = models.CharField(max_length=255, blank=True, null=True)
    tanggal_cuti = models.CharField(max_length=255)
    jumlah_hari = models.PositiveIntegerField()
    pengalihan_kepada = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pekerjaan_dialihkan",
    )
    pengalihan_status = models.CharField(
        max_length=20, choices=PengalihanStatus.choices, default=PengalihanStatus.PENDING
    )
    pengalihan_catatan = models.TextField(blank=True, null=True)
    pengalihan_tanggal_respon = models.DateTimeField(blank=True, null=True)
    masuk_kerja_pada_tanggal = models.DateField()
    kontak_selama_cuti = models.CharField(max_length=255)
    keperluan_cuti = models.TextField()
    tanggal_pengajuan = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=40, choices=Status.choices, default=Status.MENUNGGU_KONFIRMASI_PENGALIHAN
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cuti {self.employee.nama} - {self.get_jenis_cuti_display()}"


class LeaveApproval(models.Model):
    class RequiredRole(models.TextChoices):
        BOD = "bod", "BOD"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        DISETUJUI = "disetujui", "Disetujui"
        DITOLAK = "ditolak", "Ditolak"

    leave_request = models.OneToOneField(
        LeaveRequest, on_delete=models.CASCADE, related_name="approval"
    )
    required_approver = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approval_tugas",
    )
    required_role = models.CharField(
        max_length=20, choices=RequiredRole.choices, blank=True, null=True
    )
    approver = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="approval_dilakukan"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    catatan = models.TextField(blank=True, null=True)
    tanggal_approval = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Approval #{self.pk} untuk {self.leave_request} - {self.status}"


class HRReview(models.Model):
    leave_request = models.OneToOneField(
        LeaveRequest, on_delete=models.CASCADE, related_name="hr_review"
    )
    hak_saldo_cuti_saat_ini = models.PositiveIntegerField()
    pengajuan_total_cuti = models.PositiveIntegerField()
    sisa_saldo_cuti = models.PositiveIntegerField()
    hr_pic = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="hr_reviews_dibuat"
    )
    tanggal_review = models.DateTimeField(blank=True, null=True)
    catatan = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"HR Review - {self.leave_request}"
    
class LeaveBalance(models.Model):
    """
    Nge-track berapa hari yang udah kepake per karyawan, per tahun, per
    jenis cuti. Kuota totalnya (12/10/5) sengaja TIDAK disimpan di sini --
    itu konstanta tetap (lihat KUOTA_PER_JENIS di bawah), karena sama buat
    semua karyawan.
    """

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="leave_balances"
    )
    tahun = models.PositiveIntegerField()
    jenis_cuti = models.CharField(max_length=20, choices=LeaveRequest.JenisCuti.choices)
    terpakai = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint( #
                fields=["employee", "tahun", "jenis_cuti"], name="unique_saldo_per_tahun_jenis"
            ) #gak boleh ada row LeaveBalance yang memiliki 2 row dengan employee, tahun dan jenis cuti yang sama persis
        ]

    def __str__(self):
        return f"{self.employee.nama} - {self.tahun} - {self.get_jenis_cuti_display()}: {self.terpakai} hari"


KUOTA_PER_JENIS = {
    LeaveRequest.JenisCuti.TAHUNAN: 12,
    LeaveRequest.JenisCuti.SAKIT: 10,
    LeaveRequest.JenisCuti.KHUSUS: 5,
}