from django.shortcuts import render
# marketplace/views.py
from django.shortcuts import render, get_object_or_404
from .models import PlantillaExcel  # Importamos el modelo de esta misma app


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
