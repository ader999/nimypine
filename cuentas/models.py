# cuentas/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser


class SectorEconomico(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Sector Económico"
        verbose_name_plural = "Sectores Económicos"


class TipoEmpresa(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    # Esto es importante para que se vea bien en el admin de Django
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Tipo de Empresa"
        verbose_name_plural = "Tipos de Empresa"

class Mipyme(models.Model):
    # --- CONFIGURACIÓN DE PRODUCCIÓN ---
    UNIDADES_MEDIDA_CHOICES = [
        ('kg', 'Kilogramos'),
        ('g', 'Gramos'),
        ('l', 'Litros'),
        ('ml', 'Mililitros'),
        ('un', 'Unidades'),
        ('m', 'Metros'),
        ('cm', 'Centímetros'),
        ('m2', 'Metros cuadrados'),
        ('m3', 'Metros cúbicos'),
    ]

    MONEDA_CHOICES = [
        ('USD', 'Dólar estadounidense'),
        ('NIO', 'Córdoba nicaragüense'),
        ('HNL', 'Lempira hondureño'),
        ('CRC', 'Colón costarricense'),
    ]

    nombre = models.CharField(max_length=255, unique=True)
    numero_telefono = models.CharField(max_length=20, null=True, blank=True)
    correo = models.EmailField(max_length=50, null=True, blank=True)
    propietario = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='mipymes_propias', null=True)
    tipo = models.ForeignKey(TipoEmpresa, on_delete=models.SET_NULL, null=True, verbose_name="Tipo de Empresa")
    sector = models.ForeignKey(SectorEconomico, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Sector Económico")
    identificador_fiscal = models.CharField(
        max_length=80,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Identificador Fiscal (RFC, RUT, etc.)"
    )
    descripcion = models.CharField(max_length=250, null=True, blank=True, verbose_name="Descripción de la Empresa")
    direccion = models.CharField(max_length=150, null=True, blank=True, verbose_name="Dirección")
    coordenadas = models.CharField(max_length=500, null=True, blank=True, verbose_name="Coordenadas (Google Maps)")
    logo = models.ImageField(upload_to='logos/', null=True, blank=True, verbose_name="Logo de la Empresa")
    portada = models.ImageField(upload_to='portadas/', null=True, blank=True, verbose_name="Portada de la Empresa")

    # Configuración de producción
    unidad_medida_predeterminada = models.JSONField(
        default=list,
        verbose_name="Unidades de medida predeterminadas",
        help_text="Selecciona las unidades de medida que utilizará la empresa"
    )
    porcentaje_ganancia_predeterminado = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Porcentaje de ganancia por defecto (%)"
    )
    margen_desperdicio_predeterminado = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Margen de desperdicio por defecto (%)"
    )
    moneda_predeterminada = models.CharField(
        max_length=3,
        choices=MONEDA_CHOICES,
        default='USD',
        verbose_name="Moneda predeterminada"
    )

    # --- CONFIGURACIÓN DE TIENDA ---
    tienda_visible = models.BooleanField(
        default=False,
        verbose_name="Visible en Tienda",
        help_text="Activa esta opción para mostrar tus productos en la tienda pública."
    )
    mostrar_productos_en_marketplace = models.BooleanField(default=False)

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
    es_creador_contenido = models.BooleanField(default=False)

    # --- 2. AÑADIMOS EL NUEVO CAMPO DE ROL ---
    rol = models.CharField(
        max_length=50,
        choices=Roles.choices,
        default=Roles.LECTURA  # Por defecto, un nuevo usuario solo puede ver
    )

    # Campo para avatar
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="Avatar")

    # Campos para confirmación de email
    email_confirmado = models.BooleanField(default=False, verbose_name="Email confirmado")
    codigo_confirmacion = models.CharField(max_length=6, null=True, blank=True, verbose_name="Código de confirmación")

    def __str__(self):
        return self.username
