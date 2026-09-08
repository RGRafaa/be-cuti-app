from datetime import date

from rest_framework import permissions
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import KUOTA_PER_JENIS, LeaveBalance
from .permissions import HasEmployeeProfile


class SaldoCutiView(APIView):
    """
    GET /api/leaves/saldo/?tahun=2026&employee=4

    - Karyawan biasa cuma bisa lihat saldo dirinya sendiri (parameter
      `employee` diabaikan kalau bukan HR/admin).
    - HR/admin bisa lihat saldo karyawan manapun lewat parameter `employee`.
    - `tahun` opsional, default tahun sekarang.
    """

    permission_classes = [permissions.IsAuthenticated, HasEmployeeProfile]

    def get(self, request):
        tahun = int(request.query_params.get("tahun", date.today().year)) #kenapa int? karena query params itun selalu ebrbentuk string. Kita butuh int biar bisa di filter ke databse.

        employee = request.user.employee #cuma kepanggil kalo misalkan yang manggil role nya admin/hr
        employee_param = request.query_params.get("employee") #endpoint yang dimana cuma bisa liat saldo cuti dia doang
        if employee_param and request.user.role in ("hr", "admin"):
            from employees.models import Employee

            try:
                employee = Employee.objects.get(pk=employee_param)
            except Employee.DoesNotExist:
                raise NotFound("Karyawan tidak ditemukan.")

        terpakai_per_jenis = {
            b.jenis_cuti: b.terpakai
            for b in LeaveBalance.objects.filter(employee=employee, tahun=tahun) #dict_compression, ini cara ringkas buat bikin dictionary hasil query, sebenenrya sma aja kayak nulis loop manual
        }

        rincian = {}
        for jenis, kuota in KUOTA_PER_JENIS.items(): 
            terpakai = terpakai_per_jenis.get(jenis, 0)
            rincian[jenis] = {
                "kuota": kuota,
                "terpakai": terpakai,
                "sisa": max(kuota - terpakai, 0), #jaga jaga biar sisa gak pernah nunjukin angka negatif
            } #melakukan loop 3 jenis cuti dari const yang sebelumnya dibuat di models, karena kalau karyawan belum pernah ngajuin salah satu jenis cuti maka maka gak akan ada row leave balance buat jenis itu. Jadi kita masih bia ngeliatin "Cuti Sakit: 0/10"

        return Response({
            "tahun": tahun,
            "employee": employee.id,
            "rincian": rincian,
        })