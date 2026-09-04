from symtable import Class

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
        DRAFT = 'draft', "Draft (revisi pengalihan)"
        MENUNGGU_KONFIRMASI_PENGALIHAN = ( "menunggu_konfirmasi_pengalihan", "Menunggu Konfirmasi Pengalihan" )
        DITOLAK_PENGALIHAN = 'ditolak_pengalihan', "Ditolak Pengalihan"
        DISETUJUI = 'disetujui', "Disetujui"
        DITOLAK = 'ditolak', "Ditolak"
        SELESAI = 'selesai', "Selesai"
        
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="leave_requests"
    )
    jenis_cuti = models.CharField(max_length=20, choices=JenisCuti.choices)
    keterangan_cuti_khusus = models.CharField(max_length=255, blank=True, null=True)
    tanggal_cuti = models.CharField (max_length=255)  
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
    kontak_selama_cuti = models.CharField(max_length=20)
    tanggal_pengajuan = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=30, choices=Status.choices, default=Status.MENUNGGU_KONFIRMASI_PENGALIHAN
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
        
    leave_request = models.ForeignKey(
        LeaveRequest, on_delete=models.CASCADE, related_name="approvals"
    )
    required_approver = models.ForeignKey(
        Employee, on_delete=models.CASCADE, 
        null=True, blank=True, related_name="approval_tugas"
    )
    required_role = models.CharField(max_length=20, choices=RequiredRole.choices, blank=True, null=True)
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
    hak_saldo_cuti = models.PositiveIntegerField()
    pengajuan_total_cuti = models.PositiveIntegerField()
    sisa_saldo_cuti = models.PositiveIntegerField()
    hr_pic = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="hr_reviews_dibuat"
    )