from django.shortcuts import render
# marketplace/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import PlantillaExcel  # Importamos el modelo de esta misma app
from .forms import PlantillaExcelForm

def listado_plantillas(request):
    """
    Esta vista muestra todas las plantillas de Excel disponibles en el marketplace.
    """
    # Obtenemos todos los objetos del modelo PlantillaExcel
    plantillas = PlantillaExcel.objects.all()

    # Creamos el contexto (un diccionario) para pasar los datos a la plantilla
    contexto = {
        'plantillas': plantillas
    }

    # Renderizamos la plantilla, que ahora está en la ruta namespaced
    return render(request, 'marketplace/listado_plantillas.html', contexto)


def detalle_plantilla(request, plantilla_id):
    """
    Esta vista muestra los detalles de una plantilla específica.
    """
    # Obtenemos la plantilla por su ID, o mostramos un error 404 si no existe
    plantilla = get_object_or_404(PlantillaExcel, pk=plantilla_id)

    contexto = {
        'plantilla': plantilla
    }

    return render(request, 'marketplace/detalle_plantilla.html', contexto)
# Create your views here.

@login_required
def subir_plantilla_view(request):
    # --- LÓGICA DE PERMISOS ---
    # Solo pueden subir plantillas los "Creadores" O los "Admins de Mipyme"
    if not request.user.es_creador_contenido and not request.user.es_admin_mipyme:
        # Si no cumple, le negamos el acceso.
        raise PermissionDenied

    if request.method == 'POST':
        form = PlantillaExcelForm(request.POST, request.FILES)
        if form.is_valid():
            # No guardamos directamente en la BD todavía
            plantilla = form.save(commit=False)
            # Asignamos el usuario actual como el creador
            plantilla.creador = request.user
            # Ahora sí, guardamos el objeto completo
            plantilla.save()
            return redirect('marketplace_detalle', plantilla_id=plantilla.id)
    else:
        form = PlantillaExcelForm()

    return render(request, 'marketplace/subir_plantilla.html', {'form': form})