from django.db import models


class Employee(models.Model):
    nip = models.CharField("NIP", max_length=10, unique=True)
    nama = models.CharField(max_length=255)
    tanggal_masuk = models.DateField()
    jabatan = models.CharField(max_length=100)
    departemen_divisi = models.CharField("Departemen/Divisi", max_length=100)
    nama_atasan = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bawahan",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.nama} - ({self.nip})"