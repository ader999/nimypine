
from django.contrib import admin
from .models import (
    Producto, Insumo, UnidadMedida, EstándaresProducto,
    Venta, VentaItem
)

class VentaItemInline(admin.TabularInline):
    model = VentaItem
    extra = 0
    readonly_fields = ('subtotal',)
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'mipyme', 'fecha', 'total')
    list_filter = ('mipyme', 'fecha')
    search_fields = ('id', 'mipyme__nombre')
    readonly_fields = ('fecha', 'total')
    inlines = [VentaItemInline]

@admin.register(VentaItem)
class VentaItemAdmin(admin.ModelAdmin):
    list_display = ('venta', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('producto', 'venta__mipyme')
    search_fields = ('venta__id', 'producto__nombre')
    readonly_fields = ('subtotal',)

admin.site.register(Producto)
admin.site.register(Insumo)
admin.site.register(UnidadMedida)
admin.site.register(EstándaresProducto)

