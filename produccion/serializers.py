from rest_framework import serializers
from .models import Producto


class ProductoSerializer(serializers.ModelSerializer):
    """
    Serializer for Producto model, including product details, pricing, stock, and related mipyme information.
    """
    mipyme_name = serializers.CharField(source='mipyme.nombre', read_only=True)
    costo_de_produccion = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id',
            'nombre',
            'descripcion',
            'mipyme',
            'mipyme_name',
            'precio_venta',
            'porcentaje_ganancia',
            'stock_actual',
            'peso',
            'tamano_largo',
            'tamano_ancho',
            'tamano_alto',
            'presentacion',
            'costo_de_produccion',
            'procesos',
            'impuestos'
        ]
        read_only_fields = ['id', 'costo_de_produccion']