# marketplace/forms.py
from django import forms
from .models import PlantillaExcel

class PlantillaExcelForm(forms.ModelForm):
    precio = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0.2,
        max_value=20.0,
        label="Precio",
        help_text="Ingresa un precio entre 0.2 y 20."
    )

    class Meta:
        model = PlantillaExcel
        # Excluimos el campo 'creador' porque lo asignaremos automáticamente en la vista
        fields = ['nombre', 'descripcion', 'archivo_plantilla', 'imagen_vista_previa', 'precio']