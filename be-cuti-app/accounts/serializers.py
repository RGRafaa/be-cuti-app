from django.contrib.auth import get_user_model
from rest_framework import serializers

from employees.serializers import EmployeeMiniSerializer

User = get_user_model() #cara aman buat ambil model user tanpa nulis from accounts.models import User karena AUTH_USER_MODEL = "accounts.User" udah di set dan get_user_model() akan selalu ngambil setting itu

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
        fields = ["id", "email", "password", "role", "employee"]
        
        def create(self, validated_data):
            password = validated_data.pop("password")
            validated_data["username"] = validated_data["email"] #username udah gada di fields hr jadi hr gaperlu isi manual 
            user = User(**validated_data) #bikin instance user dulu (sebelum disimpen ke db) soalnya perlu proses password dulu sebelum .save() dipanggil
            user.set_password(password)
            user.save()
            return user    