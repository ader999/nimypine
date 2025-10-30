# produccion/forms.py

from django import forms
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory
from .models import Producto, Formulacion, Insumo, Proceso, PasoDeProduccion, EstándaresProducto, Venta, VentaItem, UnidadMedida, Impuesto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto  # Le decimos al formulario que se base en el modelo Producto

        # Definimos los campos del modelo que queremos incluir en el formulario
        fields = ['nombre', 'descripcion', 'imagen', 'porcentaje_ganancia', 'stock_actual', 'peso', 'tamano_largo', 'tamano_ancho', 'tamano_alto', 'presentacion']

        # Opcional: Personalizar las etiquetas y widgets para que se vean mejor con Bootstrap
        labels = {
            'nombre': 'Nombre del Producto',
            'descripcion': 'Descripción (opcional)',
            'porcentaje_ganancia': 'Porcentaje de Ganancia (%)',
            'stock_actual': 'Stock Inicial (unidades)',
            'peso': 'Peso (kg) - Opcional',
            'tamano_largo': 'Largo (cm) - Opcional',
            'tamano_ancho': 'Ancho (cm) - Opcional',
            'tamano_alto': 'Alto (cm) - Opcional',
            'presentacion': 'Presentación - Opcional',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Tarta de Chocolate'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'porcentaje_ganancia': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 20'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1.5'}),
            'tamano_largo': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 30'}),
            'tamano_ancho': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 20'}),
            'tamano_alto': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 10'}),
            'presentacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Bolsa de 500g'}),
        }

    def __init__(self, *args, **kwargs):
        # Sacamos el argumento 'usar_porcentaje_predeterminado' que le pasaremos desde la vista
        usar_porcentaje_predeterminado = kwargs.pop('usar_porcentaje_predeterminado', False)
        porcentaje_predeterminado = kwargs.pop('porcentaje_predeterminado', 0)
        super().__init__(*args, **kwargs)

        # Si se debe usar el porcentaje predeterminado, quitar el campo del formulario
        if usar_porcentaje_predeterminado:
            # Remover el campo porcentaje_ganancia del formulario
            if 'porcentaje_ganancia' in self.fields:
                del self.fields['porcentaje_ganancia']

        # Hacer opcionales los campos de dimensiones
        self.fields['peso'].required = False
        self.fields['tamano_largo'].required = False
        self.fields['tamano_ancho'].required = False
        self.fields['tamano_alto'].required = False
        self.fields['presentacion'].required = False

    def clean(self):
        cleaned_data = super().clean()
        mipyme = self.instance.mipyme if self.instance.pk else None
        if not mipyme:
            # If creating new, mipyme might be set in view, but for now assume instance has it
            return cleaned_data

        try:
            estándares = self.instance.estándares
        except EstándaresProducto.DoesNotExist:
            return cleaned_data

        # Validate peso
        peso = cleaned_data.get('peso')
        if peso is not None:
            if estándares.peso_min is not None and peso < estándares.peso_min:
                raise ValidationError(f"El peso ({peso} kg) es menor al estándar mínimo del sector ({estándares.peso_min} kg).")
            if estándares.peso_max is not None and peso > estándares.peso_max:
                raise ValidationError(f"El peso ({peso} kg) excede el estándar máximo del sector ({estándares.peso_max} kg).")

        # Validate tamano_largo
        tamano_largo = cleaned_data.get('tamano_largo')
        if tamano_largo is not None:
            if estándares.tamano_largo_min is not None and tamano_largo < estándares.tamano_largo_min:
                raise ValidationError(f"El largo ({tamano_largo} cm) es menor al estándar mínimo del sector ({estándares.tamano_largo_min} cm).")
            if estándares.tamano_largo_max is not None and tamano_largo > estándares.tamano_largo_max:
                raise ValidationError(f"El largo ({tamano_largo} cm) excede el estándar máximo del sector ({estándares.tamano_largo_max} cm).")

        # Similarly for ancho
        tamano_ancho = cleaned_data.get('tamano_ancho')
        if tamano_ancho is not None:
            if estándares.tamano_ancho_min is not None and tamano_ancho < estándares.tamano_ancho_min:
                raise ValidationError(f"El ancho ({tamano_ancho} cm) es menor al estándar mínimo del sector ({estándares.tamano_ancho_min} cm).")
            if estándares.tamano_ancho_max is not None and tamano_ancho > estándares.tamano_ancho_max:
                raise ValidationError(f"El ancho ({tamano_ancho} cm) excede el estándar máximo del sector ({estándares.tamano_ancho_max} cm).")

        # Similarly for alto
        tamano_alto = cleaned_data.get('tamano_alto')
        if tamano_alto is not None:
            if estándares.tamano_alto_min is not None and tamano_alto < estándares.tamano_alto_min:
                raise ValidationError(f"El alto ({tamano_alto} cm) es menor al estándar mínimo del sector ({estándares.tamano_alto_min} cm).")
            if estándares.tamano_alto_max is not None and tamano_alto > estándares.tamano_alto_max:
                raise ValidationError(f"El alto ({tamano_alto} cm) excede el estándar máximo del sector ({estándares.tamano_alto_max} cm).")

        return cleaned_data


class FormulacionForm(forms.ModelForm):
    class Meta:
        model = Formulacion
        fields = ['insumo', 'cantidad', 'porcentaje_desperdicio']
        widgets = {
            'insumo': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 0.5'}),
            'porcentaje_desperdicio': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Ej: 5 para 5%'}),
        }

    def __init__(self, *args, **kwargs):
        # Sacamos los argumentos que le pasaremos desde la vista
        mipyme = kwargs.pop('mipyme', None)
        usar_margen_desperdicio_predeterminado = kwargs.pop('usar_margen_desperdicio_predeterminado', False)
        super().__init__(*args, **kwargs)

        # Si hemos recibido la mipyme (que siempre debería pasar)...
        if mipyme:
            # ...filtramos el queryset del campo 'insumo' para mostrar solo
            # los insumos que pertenecen a esa mipyme.
            self.fields['insumo'].queryset = Insumo.objects.filter(mipyme=mipyme).order_by('nombre')

        # Si se debe usar el margen de desperdicio predeterminado, quitar el campo del formulario
        if usar_margen_desperdicio_predeterminado:
            if 'porcentaje_desperdicio' in self.fields:
                del self.fields['porcentaje_desperdicio']


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

    def __init__(self, *args, **kwargs):
        # Sacamos el argumento 'mipyme' que le pasaremos desde la vista
        mipyme = kwargs.pop('mipyme', None)
        super().__init__(*args, **kwargs)

        # Si hemos recibido la mipyme, filtramos las unidades de medida
        if mipyme:
            # Obtener las unidades de medida configuradas para esta empresa
            unidades_configuradas = mipyme.unidad_medida_predeterminada or []

            if unidades_configuradas:
                # Si hay unidades configuradas, mostrar solo esas
                self.fields['unidad'].queryset = UnidadMedida.objects.filter(id__in=unidades_configuradas).order_by('nombre')
            else:
                # Si no hay unidades configuradas, mostrar todas
                self.fields['unidad'].queryset = UnidadMedida.objects.all().order_by('nombre')
        else:
            # Si no se pasa mipyme, mostrar todas las unidades (por compatibilidad)
            self.fields['unidad'].queryset = UnidadMedida.objects.all().order_by('nombre')


class ProcesoForm(forms.ModelForm):
    class Meta:
        model = Proceso
        fields = ['nombre', 'costo_por_hora']
        labels = {
            'nombre': 'Nombre del Proceso',
            'costo_por_hora': 'Costo por Hora (Mano de Obra/Máquina)',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Amasado y Horneado'}),
            'costo_por_hora': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 15.75'}),
        }


# --- NUEVO FORMULARIO ---
class PasoDeProduccionForm(forms.ModelForm):
    class Meta:
        model = PasoDeProduccion
        fields = ['proceso', 'tiempo_en_minutos']
        labels = {
            'proceso': 'Proceso a añadir',
            'tiempo_en_minutos': 'Tiempo requerido (en minutos)',
        }
        widgets = {
            'proceso': forms.Select(attrs={'class': 'form-select'}),
            'tiempo_en_minutos': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 30'}),
        }

    def __init__(self, *args, **kwargs):
        # Filtramos los procesos para que solo muestre los de la mipyme actual
        mipyme = kwargs.pop('mipyme', None)
        super().__init__(*args, **kwargs)
        if mipyme:
            self.fields['proceso'].queryset = Proceso.objects.filter(mipyme=mipyme).order_by('nombre')


# --- NUEVO FORMULARIO ---
class PasoUpdateForm(forms.ModelForm):
    class Meta:
        model = PasoDeProduccion
        fields = ['tiempo_en_minutos']
        widgets = {
            'tiempo_en_minutos': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class CalculadoraLotesForm(forms.Form):
    cantidad_unidades = forms.IntegerField(
        min_value=1,
        label="Cantidad de Unidades Deseadas",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 100'})
    )


# --- FACTURACIÓN: Formularios de Venta ---

class VentaItemForm(forms.ModelForm):
    class Meta:
        model = VentaItem
        fields = ['producto', 'cantidad']
        labels = {
            'producto': 'Producto',
            'cantidad': 'Cantidad',
        }
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control cantidad-input', 'min': 1, 'value': 1}),
        }

    def __init__(self, *args, **kwargs):
        mipyme = kwargs.pop('mipyme', None)
        super().__init__(*args, **kwargs)
        if mipyme:
            self.fields['producto'].queryset = Producto.objects.filter(mipyme=mipyme).order_by('nombre')

    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad')
        if producto and cantidad:
            if cantidad > producto.stock_actual:
                raise ValidationError(f"No hay suficiente stock para {producto.nombre}. Stock disponible: {producto.stock_actual} unidades.")
        return cleaned_data


class ImpuestoForm(forms.ModelForm):
    class Meta:
        model = Impuesto
        fields = ['nombre', 'porcentaje', 'activo']
        labels = {
            'nombre': 'Nombre del Impuesto',
            'porcentaje': 'Porcentaje (%)',
            'activo': 'Activo',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: IVA'}),
            'porcentaje': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 15'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


VentaItemFormSet = modelformset_factory(
    VentaItem,
    form=VentaItemForm,
    extra=1,
    can_delete=True,
)