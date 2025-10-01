from django.shortcuts import render
# marketplace/views.py
from django.conf import settings # <--- ¡IMPORTA ESTO AL PRINCIPIO!

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import PlantillaExcel  # Importamos el modelo de esta misma app
from .forms import PlantillaExcelForm
from botocore.exceptions import ClientError # <--- ¡IMPORTA ESTO!


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
    # ... (tu código de diagnóstico y permisos puede quedar aquí) ...

    if request.method == 'POST':
        form = PlantillaExcelForm(request.POST, request.FILES)
        if form.is_valid():
            plantilla = form.save(commit=False)
            plantilla.creador = request.user

            # --- BLOQUE DE CAPTURA DE ERRORES ---
            try:
                # Intentamos guardar el objeto. Aquí es donde ocurre la llamada a MinIO.
                plantilla.save()
                print("✅ ¡ÉXITO! El objeto se guardó en la base de datos y (teóricamente) en MinIO.")
                print(f"   URL del archivo: {plantilla.archivo_plantilla.url}")
                print(f"   URL de la imagen: {plantilla.imagen_vista_previa.url}")
                return redirect('marketplace_detalle', plantilla_id=plantilla.id)

            except ClientError as e:
                # Si boto3 falla (ej. por permisos), el error se captura aquí.
                print("=" * 20, "¡ERROR DE BOTO3/MINIO!", "=" * 20)
                print(f"Ocurrió un error al intentar subir el archivo a MinIO.")
                error_code = e.response.get("Error", {}).get("Code")
                print(f"CÓDIGO DE ERROR: {error_code}")
                print(f"MENSAJE COMPLETO: {e}")
                print("=" * 64)
                # Opcional: puedes añadir un mensaje de error para el usuario en el formulario.
                form.add_error(None, f"No se pudo subir el archivo al almacenamiento. Error: {error_code}")

            except Exception as e:
                # Captura cualquier otro error inesperado.
                print("=" * 20, "¡ERROR INESPERADO!", "=" * 20)
                print(f"Ocurrió un error no relacionado con Boto3: {e}")
                print("=" * 55)
                form.add_error(None, "Ocurrió un error inesperado al guardar.")

    else:
        form = PlantillaExcelForm()

    return render(request, 'marketplace/subir_plantilla.html', {'form': form})
