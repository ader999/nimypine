# produccion/forms.py

from django import forms
from .models import Producto, Formulacion, Insumo

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto  # Le decimos al formulario que se base en el modelo Producto

        # Definimos los campos del modelo que queremos incluir en el formulario
        fields = ['nombre', 'descripcion', 'precio_venta', 'stock_actual']

        # Opcional: Personalizar las etiquetas y widgets para que se vean mejor con Bootstrap
        labels = {
            'nombre': 'Nombre del Producto',
            'descripcion': 'Descripción (opcional)',
            'precio_venta': 'Precio de Venta (PVP)',
            'stock_actual': 'Stock Inicial (unidades)',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Tarta de Chocolate'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
        }


class FormulacionForm(forms.ModelForm):
    class Meta:
        model = Formulacion
        fields = ['insumo', 'cantidad']
        widgets = {
            'insumo': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 0.5'}),
        }

    def __init__(self, *args, **kwargs):
        # Sacamos el argumento 'mipyme' que le pasaremos desde la vista
        mipyme = kwargs.pop('mipyme', None)
        super().__init__(*args, **kwargs)

        # Si hemos recibido la mipyme (que siempre debería pasar)...
        if mipyme:
            # ...filtramos el queryset del campo 'insumo' para mostrar solo
            # los insumos que pertenecen a esa mipyme.
            self.fields['insumo'].queryset = Insumo.objects.filter(mipyme=mipyme).order_by('nombre')


class FormulacionUpdateForm(forms.ModelForm):
    class Meta:
        model = Formulacion
        # Solo incluimos el campo que queremos editar
        fields = ['cantidad']

        widgets = {
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class InsumoForm(forms.ModelForm):
    class Meta:
        model = Insumo
        fields = ['nombre', 'unidad', 'costo_unitario', 'stock_actual']

        labels = {
            'nombre': 'Nombre del Insumo',
            'unidad': 'Unidad de Medida',
            'costo_unitario': 'Costo por Unidad',
            'stock_actual': 'Stock Actual en Inventario',
        }

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Harina de Trigo'}),
            'unidad': forms.Select(attrs={'class': 'form-select'}),
            # Django creará un dropdown con las Unidades de Medida
            'costo_unitario': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1.50'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 25.5'}),
        }