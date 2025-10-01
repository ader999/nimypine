# marketplace/forms.py
from django import forms
from .models import PlantillaExcel

class PlantillaExcelForm(forms.ModelForm):
    class Meta:
        model = PlantillaExcel
        # Excluimos el campo 'creador' porque lo asignaremos automáticamente en la vista
        fields = ['nombre', 'descripcion', 'archivo_plantilla', 'imagen_vista_previa']