from django.utils import timezone
from .models import LeaveApproval, LeaveRequest

def route_approval(leave_request: LeaveRequest) -> LeaveApproval:
    """
    Tentukan approver berdasaarkan role user pemilik employee yang mengajukan cuti, lalu set status leave_request jadi 'diajukan'. 
    """
    employee = leave_request.employee
    user = getattr(employee, 'user', None) #cara aman buat ambil user dari employee, karena employee bisa saja tidak punya user terkait
    role = user.role if user else "employee"
    
    approval, _ = LeaveApproval.objects.get_or_create(
        leave_request=leave_request
    )
    
    if role == "bod":
        approval.required_approver = None
        approval.required_role = LeaveApproval.RequiredRole.BOD
    else:
        approval.required_approver = employee.nama_atasan
        approval.required_role = None
        
    approval.status = LeaveApproval.Status.PENDING
    approval.save()
    
    leave_request.status = LeaveRequest.Status.DIAJUKAN
    leave_request.save(update_fields=['status', "updated_at"]) #kalo save biasa bakal update semua field, termasuk updated_at, tapi kalo pake update_fields, cuma field yang disebut aja yang diupdate, tapi updated_at tetep diupdate karena auto_now=True
    return approval

def konfirmasi_pengalihan(leave_request:LeaveRequest, setuju:bool, catatan:str=None):
    """
    Dipanggil saat rekan kerja yang ditunjuk merespon
    setuju = true -> lanjut ke route_approval() (aproval mulai jalan)
    setuju = false -> status jadi 'draft', karyawan bisa edit &pilih rekan yang lain
    """
    leave_request.pengalihan_tanggal_respon = timezone.now()
    leave_request.pengalihan_catatan = catatan
    
    if setuju:
        leave_request.pengalihan_status = LeaveRequest.PengalihanStatus.DISETUJUI
        leave_request.save(update_fields=['pengalihan_status', 'pengalihan_tanggal_respon', 'pengalihan_catatan', "updated_at"])
        route_approval(leave_request)
    else:
        leave_request.pengalihan_status = LeaveRequest.PengalihanStatus.DITOLAK
        leave_request.status = LeaveRequest.Status.DRAFT
        leave_request.save(update_fields=['pengalihan_status', 'status', 'pengalihan_tanggal_respon', 'pengalihan_catatan', "updated_at"])
    return leave_request

def resubmit_setelah_revisi(leave_request:LeaveRequest):
    """
    Dipanggil otomatis saat karyawan ganti `pengalihan_kepada` selagi status
    masih 'draft'. Rest pengalihan_status balik ke pending & kirim ulang konfirmasi ke rekan yang baru dipilih
    """
    leave_request.pengalihan_status = LeaveRequest.PengalihanStatus.PENDING
    leave_request.pengalihan_catatan = None
    leave_request.pengalihan_tanggal_respon = LeaveRequest.Status.MENUNGGU_KONFIRMASI_PENGALIHAN
    leave_request.save(update_fields=["pengalihan_status", "pengalihan_catatan", "pengalihan_tanggal_respon", "status", "updated_at"])
    return leave_request

def proses_approval(approval: LeaveApproval, approver_employee, setuju:bool, catatan:str=""):
    """
    Eksekusi approve/tolak oleh manager/bod. Ini final - gaada jalan balik kayak di pengalihan (beda dari konfirmasi_pengalihan di atas)
    """
    approval.approver = approver_employee
    approval.catatan = catatan
    approval.tanggal_approval = timezone.now()
    approval.status = LeaveApproval.Status.DISETUJUI if setuju else LeaveApproval.Status.DITOLAK
    approval.save()
    
    leave_request = approval.leave_request
    leave_request.status = (
        LeaveRequest.Status.DISETUJUI if setuju else LeaveRequest.Status.DITOLAK
    )
    leave_request.save(update_fields=["status", "updated_at"])
    return approval
    
    