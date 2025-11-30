from rest_framework import serializers
from .models import Producto, Formulacion, PasoDeProduccion, Impuesto


class FormulacionSerializer(serializers.ModelSerializer):
    """
    Serializer for Formulacion model, providing details of insumos used in the product.
    """
    insumo_nombre = serializers.CharField(source='insumo.nombre', read_only=True)
    insumo_descripcion = serializers.CharField(source='insumo.descripcion', read_only=True)
    unidad = serializers.CharField(source='insumo.unidad.abreviatura', read_only=True)
    costo_unitario = serializers.DecimalField(source='insumo.costo_unitario', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Formulacion
        fields = [
            'insumo_nombre',
            'insumo_descripcion',
            'unidad',
            'cantidad',
            'porcentaje_desperdicio',
            'costo_unitario'
        ]


class PasoDeProduccionSerializer(serializers.ModelSerializer):
    """
    Serializer for PasoDeProduccion model, providing details of processes used in the product.
    """
    proceso_nombre = serializers.CharField(source='proceso.nombre', read_only=True)
    costo_por_hora = serializers.DecimalField(source='proceso.costo_por_hora', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = PasoDeProduccion
        fields = [
            'proceso_nombre',
            'tiempo_en_minutos',
            'costo_por_hora'
        ]


class ImpuestoSerializer(serializers.ModelSerializer):
    """
    Serializer for Impuesto model, providing details of taxes applied to the product.
    """
    class Meta:
        model = Impuesto
        fields = [
            'nombre',
            'porcentaje',
            'activo'
        ]


class ProductoSerializer(serializers.ModelSerializer):
    """
    Serializer for Producto model, including product details, pricing, stock, and related mipyme information.
    """
    mipyme_name = serializers.CharField(source='mipyme.nombre', read_only=True)
    costo_de_produccion = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    formulacion = FormulacionSerializer(many=True, read_only=True)
    procesos_detalles = PasoDeProduccionSerializer(source='pasodeproduccion_set', many=True, read_only=True)
    impuestos_detalles = ImpuestoSerializer(source='impuestos', many=True, read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id',
            'nombre',
            'descripcion',
            'imagen',
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
            'impuestos',
            'formulacion',
            'procesos_detalles',
            'impuestos_detalles'
        ]
        read_only_fields = ['id', 'costo_de_produccion']
from .models import Venta, VentaItem


class VentaItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = VentaItem
        fields = ('producto', 'cantidad', 'precio_unitario')


class VentaSerializer(serializers.ModelSerializer):
    items = VentaItemSerializer(many=True)

    class Meta:
        model = Venta
        fields = ('id', 'fecha', 'total', 'items')
        read_only_fields = ('id', 'fecha', 'total')

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        mipyme = self.context['request'].user.mipyme
        venta = Venta.objects.create(mipyme=mipyme, **validated_data)
        for item_data in items_data:
            VentaItem.objects.create(venta=venta, **item_data)
            # Actualizar stock de producto
            producto = item_data['producto']
            producto.stock_actual -= item_data['cantidad']
            producto.save()
        venta.calcular_total()
        return venta
