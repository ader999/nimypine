from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Producto
from marketplace.models import ProductoMarketplace

@receiver(post_save, sender=Producto)
def crear_o_actualizar_producto_marketplace(sender, instance, created, **kwargs):
    """
    Crea o actualiza un ProductoMarketplace cuando se guarda un Producto.
    """
    ProductoMarketplace.objects.update_or_create(
        producto=instance,
        defaults={
            'visible': instance.mipyme.mostrar_productos_en_marketplace,
            'activo': True,
        }
    )