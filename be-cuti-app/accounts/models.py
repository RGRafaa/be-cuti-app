from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        EMPLOYEE = "employee", "Karyawan"
        MANAGER = "manager", "Manager Departemen"
        BOD = "bod", "BOD"
        HR = "hr", "HR"
        ADMIN = "admin", "Admin"

    employee = models.OneToOneField(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="user",
        null=True,
        blank=True,
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYEE)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"