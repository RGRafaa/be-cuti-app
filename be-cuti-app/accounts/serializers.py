from django.contrib.auth import get_user_model
from rest_framework import serializers

from employees.serializers import EmployeeMiniSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    employee_detail = EmployeeMiniSerializer(source="employee", read_only=True)
    
class Meta:
    model = User
    fields = ["id", "username", "email", "role", "employee", "employee_detail"]
    read_only_fields = ["id", "role", "employee"]
    
class RegisterSerializer(serializers.ModelSerializer):
    """
    Dipakai HR/Admin nbuat bikin akun baru + hubugin ke employee
    password di hash lewat set_password bukan disimpan di plain text
    """
    
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta: 
        model = User
        fields = ["id", "username", "email", "password", "role", "employee"]
        
        def create(self, validated_data):
            password = validated_data.pop("password")
            user = User(**validated_data) #bikin instance user dulu (sebelum disimpen ke db) soalnya perlu proses password dulu sebelum .save() dipanggil
            user.set_password(password)
            user.save()
            return user    