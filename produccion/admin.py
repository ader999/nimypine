
from django.contrib import admin
from .models import Producto, Insumo, UnidadMedida, EstándaresProducto

admin.site.register(Producto)
admin.site.register(Insumo)
admin.site.register(UnidadMedida)
admin.site.register(EstándaresProducto)

