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
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Costo por unidad de medida
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Cantidad en inventario

    def __str__(self):
        return f"{self.nombre} ({self.unidad.abreviatura})"

# --- NUEVO MODELO ---
# Modelo para representar un proceso de producción (ej: cortar, ensamblar, pintar)
class Proceso(models.Model):
    nombre = models.CharField(max_length=100)
    costo_por_hora = models.DecimalField(max_digits=10, decimal_places=2, help_text="Costo de mano de obra o máquina por hora")
    mipyme = models.ForeignKey(Mipyme, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre


# Modelo para el producto final que crea la Mipyme
class Producto(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    mipyme = models.ForeignKey(Mipyme, on_delete=models.CASCADE, related_name="productos")
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Precio al público
    stock_actual = models.IntegerField(default=0)  # Unidades de producto terminado en inventario
    # --- NUEVOS CAMPOS PARA ESTANDARIZACIÓN ---
    peso = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Peso (kg)")
    tamano_largo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Largo (cm)")
    tamano_ancho = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Ancho (cm)")
    tamano_alto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Alto (cm)")
    presentacion = models.CharField(max_length=200, blank=True, null=True, verbose_name="Presentación")
    # --- CAMPO MODIFICADO ---
    # Relacionamos los productos con los procesos a través de una tabla intermedia
    procesos = models.ManyToManyField(Proceso, through='PasoDeProduccion', related_name='productos')

    def __str__(self):
        return self.nombre

    # --- MÉTODO MODIFICADO: Para calcular el costo de producción total ---
    @property
    def costo_insumos(self):
        """Calcula el costo total de los insumos, incluyendo el desperdicio."""
        costo_total_insumos = decimal.Decimal(0)
        for item in self.formulacion.all():
            costo_base = item.cantidad * item.insumo.costo_unitario
            costo_con_desperdicio = costo_base * (1 + (item.porcentaje_desperdicio / 100))
            costo_total_insumos += costo_con_desperdicio
        return costo_total_insumos

    @property
    def costo_procesos(self):
        """Calcula el costo total de la mano de obra/procesos."""
        costo_total_procesos = decimal.Decimal(0)
        # Usamos 'pasodeproduccion_set' para acceder a los pasos desde el producto
        for paso in self.pasodeproduccion_set.all():
            costo_del_paso = (decimal.Decimal(paso.tiempo_en_minutos) / 60) * paso.proceso.costo_por_hora
            costo_total_procesos += costo_del_paso
        return costo_total_procesos

    @property
    def costo_de_produccion(self):
        """Suma el costo de insumos y el costo de procesos."""
        return self.costo_insumos + self.costo_procesos

    @property
    def margen_de_ganancia(self):
        """Calcula el margen de ganancia por unidad."""
        if self.precio_venta is not None:
            # El costo_de_produccion ya es una propiedad que calcula el total
            return self.precio_venta - self.costo_de_produccion
        return decimal.Decimal(0)


# --- NUEVO MODELO ---
# Tabla intermedia para definir qué procesos y por cuánto tiempo se aplican a un producto
class PasoDeProduccion(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    proceso = models.ForeignKey(Proceso, on_delete=models.CASCADE)
    tiempo_en_minutos = models.PositiveIntegerField()

    class Meta:
        unique_together = ('producto', 'proceso')

    def __str__(self):
        return f"Proceso '{self.proceso.nombre}' para '{self.producto.nombre}' ({self.tiempo_en_minutos} min)"


# Modelo que representa la "receta" o "formulación"
class Formulacion(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="formulacion")
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    # --- NUEVO CAMPO ---
    porcentaje_desperdicio = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Porcentaje de este insumo que se pierde en el proceso (ej: 5 para un 5%)"
    )

    class Meta:
        # Aseguramos que un insumo solo pueda aparecer una vez por producto
        unique_together = ('producto', 'insumo')

    def __str__(self):
        return f"{self.cantidad} {self.insumo.unidad.abreviatura} de {self.insumo.nombre} para {self.producto.nombre}"


# Modelo para estándares por producto
class EstándaresProducto(models.Model):
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE, related_name='estándares')
    peso_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Peso Mínimo (kg)")
    peso_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Peso Máximo (kg)")
    tamano_largo_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Largo Mínimo (cm)")
    tamano_largo_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Largo Máximo (cm)")
    tamano_ancho_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Ancho Mínimo (cm)")
    tamano_ancho_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Ancho Máximo (cm)")
    tamano_alto_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Alto Mínimo (cm)")
    tamano_alto_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Alto Máximo (cm)")
    presentacion_estandar = models.CharField(max_length=200, blank=True, null=True, verbose_name="Presentación Estándar")

    def __str__(self):
        return f"Estándares para {self.producto.nombre}"

    class Meta:
        verbose_name = "Estándar de Producto"
        verbose_name_plural = "Estándares de Productos"

# --- MODELOS DE VENTAS (Facturación) ---

class Venta(models.Model):
    mipyme = models.ForeignKey(Mipyme, on_delete=models.CASCADE, related_name='ventas')
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=decimal.Decimal('0.00'), editable=False)

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-fecha']

    def __str__(self):
        return f"Venta #{self.id} - {self.mipyme} - {self.fecha.strftime('%Y-%m-%d %H:%M')}"

    def calcular_total(self):
        total = decimal.Decimal('0.00')
        for item in self.items.all():
            total += item.subtotal
        self.total = total
        self.save(update_fields=['total'])


class VentaItem(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(verbose_name="Cantidad")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio unitario")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    class Meta:
        verbose_name = "Item de Venta"
        verbose_name_plural = "Items de Venta"

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"

    def save(self, *args, **kwargs):
        # Calcular subtotal automáticamente
        self.subtotal = decimal.Decimal(self.cantidad) * self.precio_unitario
        super().save(*args, **kwargs)