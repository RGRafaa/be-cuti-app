from django.contrib import admin
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['nip', 'nama', 'jabatan', 'departemen_divisi', 'nama_atasan']
    search_fields = ['nip', 'nama']
    