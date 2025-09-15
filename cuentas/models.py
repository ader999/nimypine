# cuentas/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser


class TipoEmpresa(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    # Esto es importante para que se vea bien en el admin de Django
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Tipo de Empresa"
        verbose_name_plural = "Tipos de Empresa"

class Mipyme(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    numero_telefono = models.CharField(max_length=20, null=True, blank=True)
    correo = models.EmailField(max_length=50, null=True, blank=True)
    tipo = models.ForeignKey(TipoEmpresa, on_delete=models.SET_NULL, null=True, verbose_name="Tipo de Empresa")
    identificador_fiscal = models.CharField(
        max_length=80,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Identificador Fiscal (RFC, RUT, etc.)"
    )

    def __str__(self):
        return f"{self.nombre} (ID: {self.id})"


class Usuario(AbstractUser):
    # --- 1. DEFINIMOS LOS ROLES DISPONIBLES ---
    class Roles(models.TextChoices):
        LECTURA = 'LECTURA', 'Solo Lectura'
        EDITOR = 'EDITOR', 'Editor'
        ADMIN = 'ADMIN', 'Administrador'
        ADDP = 'AGREGARPRODUCTO', 'Agregar Producto'

    mipyme = models.ForeignKey(Mipyme, on_delete=models.CASCADE, related_name='usuarios', null=True, blank=True)
    es_admin_mipyme = models.BooleanField(default=False)  # Este es el "super-admin" de la Mipyme

    # --- 2. AÑADIMOS EL NUEVO CAMPO DE ROL ---
    rol = models.CharField(
        max_length=50,
        choices=Roles.choices,
        default=Roles.LECTURA  # Por defecto, un nuevo usuario solo puede ver
    )

    def __str__(self):
        return self.username

    def __str__(self):
        return self.username