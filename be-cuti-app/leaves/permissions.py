from rest_framework import permissions

class IsHR(permissions.BasePermission):
    message = "Hanya HR yang boleh mengakses resource ini"
    
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ("hr", "admin")
        )
        
class IsManagerOrBOD(permissions.BasePermission):
    message = "Hanya Manager atau BOD yang boleh mengakses resources ini"
    
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ("manager", "bod", "admin")
        )

class HasEmployeeProfile(permissions.BasePermission): #Fungsi yang hanya boleh diakses karyawan
    message = "Akun ini belum terhubung ke data karyawan (Employee)"
    
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.employee_id is not None or request.user.role == "admin")
        )