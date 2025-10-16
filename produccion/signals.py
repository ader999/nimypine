# produccion/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Formulacion, PasoDeProduccion, Producto, Impuesto

@receiver(post_save, sender=Formulacion)
@receiver(post_delete, sender=Formulacion)
def recalcular_precio_producto_por_formulacion(sender, instance, **kwargs):
    """
    Recalcula el precio de venta del producto cuando se guarda o elimina
    un item de la formulación.
    """
    producto = instance.producto
    producto.save() # El método save de Producto ya recalcula el precio

@receiver(post_save, sender=PasoDeProduccion)
@receiver(post_delete, sender=PasoDeProduccion)
def recalcular_precio_producto_por_paso(sender, instance, **kwargs):
    """
    Recalcula el precio de venta del producto cuando se guarda o elimina
    un paso de producción.
    """
    producto = instance.producto
    producto.save()

@receiver(post_save, sender=Impuesto)
@receiver(post_delete, sender=Impuesto)
def recalcular_precio_producto_por_impuesto(sender, instance, **kwargs):
    """
    Recalcula el precio de venta de todos los productos asociados a una MiPyME
    cuando se actualiza o elimina un impuesto.
    """
    # Como un impuesto puede afectar a muchos productos, iteramos sobre ellos
    # Esta aproximación puede ser ineficiente si hay miles de productos.
    # Considerar una actualización en lote si el rendimiento es un problema.
    if hasattr(instance, 'mipyme'):
        productos_afectados = Producto.objects.filter(mipyme=instance.mipyme)
        for producto in productos_afectados:
            producto.save()