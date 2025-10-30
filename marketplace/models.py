# marketplace/models.py
from django.db import models
# Importamos el modelo de usuario de la app cuentas
from cuentas.models import Usuario
from produccion.models import Producto

class PlantillaExcel(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    archivo_plantilla = models.FileField(upload_to='plantillas_excel/', blank=True, null=True, verbose_name="Archivo de Plantilla")
    imagen_vista_previa = models.ImageField(upload_to='imagenes_plantillas/', blank=True, null=True, verbose_name="Imagen de Vista Previa")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    creador = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='plantillas_creadas')

    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Precio")
    downloads = models.PositiveIntegerField(default=0, verbose_name="Descargas")

    def __str__(self):
        return self.nombre

class Purchase(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='purchases')
    plantilla = models.ForeignKey(PlantillaExcel, on_delete=models.CASCADE, related_name='purchases')
    paypal_payment_id = models.CharField(max_length=100, unique=True)
    paypal_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_compra = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.plantilla.nombre}"

    class Meta:
        unique_together = ('usuario', 'plantilla')
        verbose_name = "Compra"
        verbose_name_plural = "Compras"

    class Meta:
        verbose_name = "Plantilla de Excel"
        verbose_name_plural = "Plantillas de Excel"


class ProductoMarketplace(models.Model):
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE, related_name='marketplace_producto')
    activo = models.BooleanField(default=True, verbose_name="Activo en Marketplace")
    fecha_publicacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Publicación")

    def __str__(self):
        return f"{self.producto.nombre} - Marketplace"

    class Meta:
        verbose_name = "Producto en Marketplace"
        verbose_name_plural = "Productos en Marketplace"