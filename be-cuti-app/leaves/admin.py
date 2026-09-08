from django.contrib import admin
from .models import LeaveRequest, LeaveApproval, HRReview, LeaveBalance

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'jenis_cuti', 'status', 'pengalihan_status', 'tanggal_pengajuan']
    list_filter = ['jenis_cuti', 'status']
    search_fields = ['employee__nama']
    
@admin.register(LeaveApproval)
class LeaveApprovalAdmin(admin.ModelAdmin):
    list_display = ['leave_request', 'required_approver', 'required_role', 'status']
    
@admin.register(HRReview)
class HRReviewAdmin(admin.ModelAdmin):
    list_display = ['leave_request', 'sisa_saldo_cuti', 'hr_pic']
    
@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ["employee", "tahun", "jenis_cuti", "terpakai"]
    list_filter = ["tahun", "jenis_cuti"]
    