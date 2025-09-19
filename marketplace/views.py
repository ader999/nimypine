from django.shortcuts import render
# marketplace/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.conf import settings
from django.urls import reverse
from decimal import Decimal
import paypalrestsdk
from .models import PlantillaExcel, Purchase  # Importamos el modelo de esta misma app
from .forms import PlantillaExcelForm

# Configurar PayPal
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,  # sandbox or live
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

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

    # Verificar si el usuario ha comprado esta plantilla
    ha_comprado = False
    if request.user.is_authenticated:
        ha_comprado = Purchase.objects.filter(usuario=request.user, plantilla=plantilla).exists()

    contexto = {
        'plantilla': plantilla,
        'ha_comprado': ha_comprado
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

@login_required
def descargar_plantilla(request, plantilla_id):
    plantilla = get_object_or_404(PlantillaExcel, pk=plantilla_id)

    # Verificar si el usuario ya ha comprado esta plantilla
    if Purchase.objects.filter(usuario=request.user, plantilla=plantilla).exists():
        # Ya pagado, descargar directamente
        response = HttpResponse(plantilla.archivo_plantilla, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{plantilla.nombre}.xlsx"'
        return response

    if plantilla.precio is None or plantilla.precio == 0:
        # Descarga gratuita
        plantilla.downloads += 1
        plantilla.save()
        response = HttpResponse(plantilla.archivo_plantilla, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{plantilla.nombre}.xlsx"'
        return response
    else:
        # Pago requerido
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": request.build_absolute_uri(reverse('marketplace_pago_exitoso', args=[plantilla_id])),
                "cancel_url": request.build_absolute_uri(reverse('marketplace_pago_cancelado', args=[plantilla_id]))
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": plantilla.nombre,
                        "sku": str(plantilla.id),
                        "price": str(plantilla.precio),
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": str(plantilla.precio),
                    "currency": "USD"
                },
                "description": f"Compra de plantilla: {plantilla.nombre}"
            }]
        })

        if payment.create():
            # Guardar payment_id en sesión para verificar después
            request.session[f'paypal_payment_id_{plantilla_id}'] = payment.id
            for link in payment.links:
                if link.rel == "approval_url":
                    return redirect(link.href)
        else:
            # Error al crear pago
            return render(request, 'marketplace/detalle_plantilla.html', {
                'plantilla': plantilla,
                'error': 'Error al procesar el pago. Inténtalo de nuevo.'
            })

@login_required
def pago_exitoso(request, plantilla_id):
    plantilla = get_object_or_404(PlantillaExcel, pk=plantilla_id)
    payment_id = request.session.get(f'paypal_payment_id_{plantilla_id}')
    payer_id = request.GET.get('PayerID')

    if payment_id and payer_id:
        payment = paypalrestsdk.Payment.find(payment_id)
        if payment.execute({"payer_id": payer_id}):
            # Pago exitoso, crear registro de compra
            transaction_id = None
            for transaction in payment.transactions:
                if hasattr(transaction, 'related_resources'):
                    for resource in transaction.related_resources:
                        if hasattr(resource, 'sale') and resource.sale:
                            transaction_id = resource.sale.id
                            break

            Purchase.objects.create(
                usuario=request.user,
                plantilla=plantilla,
                paypal_payment_id=payment_id,
                paypal_transaction_id=transaction_id,
                amount=plantilla.precio
            )

            # Limpiar sesión
            del request.session[f'paypal_payment_id_{plantilla_id}']

            # Descargar archivo
            response = HttpResponse(plantilla.archivo_plantilla, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{plantilla.nombre}.xlsx"'
            return response
        else:
            return render(request, 'marketplace/detalle_plantilla.html', {
                'plantilla': plantilla,
                'error': 'Error al ejecutar el pago.'
            })
    else:
        return render(request, 'marketplace/detalle_plantilla.html', {
            'plantilla': plantilla,
            'error': 'Pago no autorizado.'
        })

@login_required
def pago_cancelado(request, plantilla_id):
    plantilla = get_object_or_404(PlantillaExcel, pk=plantilla_id)
    # Limpiar sesión si existe
    if f'paypal_payment_id_{plantilla_id}' in request.session:
        del request.session[f'paypal_payment_id_{plantilla_id}']
    return render(request, 'marketplace/detalle_plantilla.html', {
        'plantilla': plantilla,
        'error': 'Pago cancelado.'
    })

@login_required
def perfil_creador(request):
    # Plantillas subidas por el usuario
    mis_plantillas = PlantillaExcel.objects.filter(creador=request.user)

    # Compras de las plantillas del usuario (ventas)
    ventas = Purchase.objects.filter(plantilla__creador=request.user).select_related('plantilla', 'usuario')

    # Descargas totales de plantillas gratuitas
    descargas_gratuitas = sum(p.downloads for p in mis_plantillas.filter(precio__lte=0))

    # Cálculos de ganancias
    total_ventas = sum(v.amount for v in ventas)
    comision_nimypines = total_ventas * Decimal('0.3')
    ganancias_netas = total_ventas * Decimal('0.7')

    contexto = {
        'mis_plantillas': mis_plantillas,
        'ventas': ventas,
        'descargas_gratuitas': descargas_gratuitas,
        'total_ventas': total_ventas,
        'comision_nimypines': comision_nimypines,
        'ganancias_netas': ganancias_netas,
    }

    return render(request, 'marketplace/perfil.html', contexto)