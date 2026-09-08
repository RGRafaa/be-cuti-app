from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USERNAME_FIELD = "email" #buat nentuin fieled mana yang dipakai buat identitas login
    REQUIRED_FIELDS = ["username"] #menentukan field apa aja yang wajib pas ada yang bikin akun lewat command createsuperuser
    
    class Role(models.TextChoices):
        EMPLOYEE = "employee", "Karyawan"
        MANAGER = "manager", "Manager Departemen"
        BOD = "bod", "BOD"
        HR = "hr", "HR"
        ADMIN = "admin", "Admin"
        
    email = models.EmailField(unique=True) #email yang sebelumnya ga wajib jadi wajib dan harus unik biar 2 user ga punya 2 sistem yang sama
    employee = models.OneToOneField(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="user",
        null = True, 
        blank=True
    
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYEE)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"