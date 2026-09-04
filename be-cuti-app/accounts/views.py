from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer, UserSerializer

User = get_user_model()

class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self,request):
        return Response(UserSerializer(request.user).data)
    
    
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    
    def get_permissions(self):
        if not User.objects.exists():
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), _IsHRorAdmin()]
    
class _IsHRorAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated and request.user.role in ("hr", "admin")
        )
