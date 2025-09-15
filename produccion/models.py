# produccion/models.py
from django.db import models
from cuentas.models import Mipyme  # Importamos el modelo Mipyme
import decimal  # Importamos para usar Decimal


# Modelo para las unidades de medida (kg, litro, metro, unidad, etc.)
class UnidadMedida(models.Model):
    nombre = models.CharField(max_length=50, unique=True)  # Ej: "Kilogramo"
    abreviatura = models.CharField(max_length=10)  # Ej: "kg"

    def __str__(self):
        return f"{self.nombre} ({self.abreviatura})"


# Modelo para la materia prima o insumos
class Insumo(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    unidad = models.ForeignKey(UnidadMedida, on_delete=models.PROTECT)
    mipyme = models.ForeignKey(Mipyme, on_delete=models.CASCADE)
    # NUEVOS CAMPOS:
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Costo por unidad de medida
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Cantidad en inventario

    def __str__(self):
        return f"{self.nombre} ({self.unidad.abreviatura})"


# Modelo para el producto final que crea la Mipyme
class Producto(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    mipyme = models.ForeignKey(Mipyme, on_delete=models.CASCADE, related_name="productos")
    # NUEVOS CAMPOS:
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Precio al público
    stock_actual = models.IntegerField(default=0)  # Unidades de producto terminado en inventario

    def __str__(self):
        return self.nombre

    # NUEVO MÉTODO: Para calcular el costo de producción
    @property
    def costo_de_produccion(self):
        costo_total = decimal.Decimal(0)
        # Recorremos cada insumo en la formulación del producto
        for item in self.formulacion.all():
            costo_total += item.cantidad * item.insumo.costo_unitario
        return costo_total


# Modelo que representa la "receta" o "formulación"
class Formulacion(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="formulacion")
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        # Aseguramos que un insumo solo pueda aparecer una vez por producto
        unique_together = ('producto', 'insumo')

    def __str__(self):
        return f"{self.cantidad} {self.insumo.unidad.abreviatura} de {self.insumo.nombre} para {self.producto.nombre}"