from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Employee
from .serializers import EmployeeSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related("nama_atasan").all()
    serializer_class = EmployeeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["nama", "nip", "jabatan"]
    
    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), _IsHRorAdmin()]
        return [permissions.IsAuthenticated()]
    
    @action(detail=False, methods=["get"], url_path="kandidat-pengalihan")
    def kandidat_pengalihan(self, request):
        """
        Dropdown 'pengalihan kepada' employee -> sesama departemen
        Mangager -> bawahannya sendiri.
        """
        employee = request.user.employee
        if request.user.role == "manager":
            qs = Employee.objects.filter(nama_atasan=employee)
        else:
            qs = Employee.objects.filter(
                departemen_divisi=employee.departemen_divisi
            ).exclude(id=employee.id)
        return Response(EmployeeSerializer(qs, many=True).data)
    
class _IsHRorAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ("hr", "admin")
        )