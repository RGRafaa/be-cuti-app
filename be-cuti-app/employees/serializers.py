from rest_framework import serializers
from .models import Employee

class EmployeeMiniSerializer(serializers.ModelSerializer):
    """Versi ringkas, dipakai buat nested represntation di serializer lain"""
    
    class Meta:
        model = Employee
        fields = ["id", "nip", "nama", "jabatan", "departemen_divisi"]
        
class EmployeeSerializer(serializers.ModelSerializer):
    nama_atasan_detail = EmployeeMiniSerializer(source="nama_atasan", read_only=True)
    
    class Meta:
        model = Employee
        fields = ["id", "nip", "nama", "tanggal_masuk", "jabatan", "departemen_divisi",
            "nama_atasan", "nama_atasan_detail", "created_at", "updated_at",]
        read_only_fields = ["created_at", "updated_at"]