# produccion/views.py

import decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Producto, Insumo, Formulacion, PasoDeProduccion, Proceso
from .forms import ProductoForm, FormulacionForm, InsumoForm, FormulacionUpdateForm, ProcesoForm, PasoUpdateForm, PasoDeProduccionForm, CalculadoraLotesForm
from cuentas.decorators import rol_requerido, mipyme_requerida


@login_required
@mipyme_requerida
def panel_produccion(request):
    """
    Vista principal de la aplicación 'produccion'.
    Solo accesible para usuarios con una Mipyme asociada.
    """
    # Gracias al decorador, ahora podemos estar SEGUROS de que
    # request.user.mipyme existe y no es None.

    contexto = {
        'titulo': 'Panel de Producción',
        'usuario': request.user,
        'nombrepine': request.user.mipyme.nombre  # Ahora esta línea es segura
    }

    return render(request, 'produccion/panel.html', contexto)
@login_required
def lista_productos(request):
    """
    Muestra una lista de todos los productos pertenecientes a la Mipyme del usuario logueado.
    """
    # Asumimos que el modelo Mipyme está relacionado con el User (ej. OneToOneField)
    # y se puede acceder a través de request.user.mipyme
    try:
        mipyme_usuario = request.user.mipyme
        productos = Producto.objects.filter(mipyme=mipyme_usuario).order_by('nombre')
    except AttributeError:
        # Manejar el caso de que el usuario no tenga una Mipyme asociada
        # (esto no debería pasar si la lógica de cuentas es correcta)
        productos = []

    contexto = {
        'productos': productos,
        'nombrepine': request.user.mipyme.nombre
    }
    return render(request, 'produccion/lista_productos.html', contexto)


@login_required
@rol_requerido('ADMIN', 'EDITOR')
def crear_producto(request):
    """
    Gestiona la creación de un nuevo producto.
    """
    if request.method == 'POST':
        # Si el formulario fue enviado, procesa los datos
        form = ProductoForm(request.POST)
        if form.is_valid():
            # El formulario es válido, pero no lo guardes todavía
            nuevo_producto = form.save(commit=False)

            # Asigna la Mipyme del usuario actual al nuevo producto
            # Esto es crucial para la seguridad y la lógica de negocio
            nuevo_producto.mipyme = request.user.mipyme

            # Ahora sí, guarda el objeto completo en la base de datos
            nuevo_producto.save()

            # Redirige al usuario a la lista de productos para que vea el nuevo item
            return redirect('produccion:lista_productos')
    else:
        # Si la petición es GET, muestra un formulario vacío
        form = ProductoForm()

    contexto = {
        'form': form,
        'nombrepine': request.user.mipyme.nombre
    }
    return render(request, 'produccion/crear_producto.html', contexto)


@login_required
def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, mipyme=request.user.mipyme)
    mipyme_actual = request.user.mipyme

    # Inicializamos ambos formularios para pasarlos al contexto
    form_insumo = FormulacionForm(mipyme=mipyme_actual)
    form_proceso = PasoDeProduccionForm(mipyme=mipyme_actual)

    if request.method == 'POST':
        # Identificamos qué formulario se envió usando el nombre del botón 'submit'

        # --- LÓGICA PARA EL FORMULARIO DE INSUMOS ---
        if 'submit_insumo' in request.POST:
            form_insumo = FormulacionForm(request.POST, mipyme=mipyme_actual)
            if form_insumo.is_valid():
                insumo_seleccionado = form_insumo.cleaned_data['insumo']
                if not Formulacion.objects.filter(producto=producto, insumo=insumo_seleccionado).exists():
                    nuevo_item = form_insumo.save(commit=False)
                    nuevo_item.producto = producto
                    nuevo_item.save()
                # Redirigimos para limpiar el formulario y evitar reenvíos
                return redirect('produccion:detalle_producto', producto_id=producto.id)

        # --- LÓGICA PARA EL FORMULARIO DE PROCESOS ---
        elif 'submit_proceso' in request.POST:
            form_proceso = PasoDeProduccionForm(request.POST, mipyme=mipyme_actual)
            if form_proceso.is_valid():
                proceso_seleccionado = form_proceso.cleaned_data['proceso']
                if not PasoDeProduccion.objects.filter(producto=producto, proceso=proceso_seleccionado).exists():
                    nuevo_paso = form_proceso.save(commit=False)
                    nuevo_paso.producto = producto
                    nuevo_paso.save()
                # Redirigimos para limpiar el formulario y evitar reenvíos
                return redirect('produccion:detalle_producto', producto_id=producto.id)

    # Obtenemos los items para mostrarlos en las tablas
    formulacion_items = Formulacion.objects.filter(producto=producto).order_by('insumo__nombre')
    pasos_produccion = PasoDeProduccion.objects.filter(producto=producto).order_by('proceso__nombre')

    contexto = {
        'producto': producto,
        'formulacion_items': formulacion_items,
        'pasos_produccion': pasos_produccion,
        'form_insumo': form_insumo,  # Pasamos el formulario de insumos
        'form_proceso': form_proceso,  # Pasamos el formulario de procesos
        'nombrepine': request.user.mipyme.nombre
    }
    return render(request, 'produccion/detalle_producto.html', contexto)

@login_required
def lista_insumos(request):
    """
    Muestra una lista de todos los insumos de la Mipyme del usuario.
    """
    insumos = Insumo.objects.filter(mipyme=request.user.mipyme).order_by('nombre')
    contexto = {
        'insumos': insumos,
        'nombrepine': request.user.mipyme.nombre
    }
    return render(request, 'produccion/lista_insumos.html', contexto)


@login_required
def crear_insumo(request):
    """
    Gestiona la creación de un nuevo insumo.
    """
    if request.method == 'POST':
        form = InsumoForm(request.POST)
        if form.is_valid():
            nuevo_insumo = form.save(commit=False)
            nuevo_insumo.mipyme = request.user.mipyme # Asigna la Mipyme del usuario
            nuevo_insumo.save()
            return redirect('produccion:lista_insumos')
    else:
        form = InsumoForm()

    contexto = {
        'form': form,
        'nombrepine': request.user.mipyme.nombre
    }
    return render(request, 'produccion/crear_insumo.html', contexto)

@login_required
def editar_producto(request, producto_id):
    """
    Gestiona la edición de un producto existente.
    """
    # Seguridad: Obtenemos el producto asegurándonos que pertenece a la Mipyme del usuario
    producto = get_object_or_404(Producto, id=producto_id, mipyme=request.user.mipyme)

    if request.method == 'POST':
        # Pasamos 'instance=producto' para indicarle al formulario que estamos actualizando
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('produccion:lista_productos') # Redirigimos a la lista de productos
    else:
        # Si es GET, mostramos el formulario pre-llenado con los datos del producto
        form = ProductoForm(instance=producto)

    contexto = {
        'form': form,
        'producto': producto, # Lo pasamos para usarlo en el título de la plantilla
        'nombrepine': request.user.mipyme.nombre
    }
    # Reutilizaremos la plantilla de creación de productos
    return render(request, 'produccion/crear_producto.html', contexto)


@login_required
def eliminar_producto(request, producto_id):
    """
    Elimina un producto específico y su formulación asociada.
    """
    # Seguridad: Obtenemos el producto asegurándonos que pertenece a la Mipyme del usuario
    producto_a_borrar = get_object_or_404(Producto, id=producto_id, mipyme=request.user.mipyme)

    # Solo proceder si la solicitud es de tipo POST
    if request.method == 'POST':
        producto_a_borrar.delete()
        # Redirigir de vuelta a la lista de productos
        return redirect('produccion:lista_productos')

    # Si alguien intenta acceder a la URL con GET, simplemente lo redirigimos
    return redirect('produccion:lista_productos')


@login_required
def eliminar_formulacion_item(request, producto_id, item_id):
    """
    Elimina un insumo específico de la formulación de un producto.
    """
    # Verificación de seguridad: Asegurarnos de que el item a borrar
    # pertenece a un producto que a su vez pertenece a la Mipyme del usuario.
    item_a_borrar = get_object_or_404(
        Formulacion,
        id=item_id,
        producto__id=producto_id,
        producto__mipyme=request.user.mipyme
    )

    # Solo proceder si la solicitud es de tipo POST por seguridad
    if request.method == 'POST':
        item_a_borrar.delete()
        # Redirigir de vuelta a la página de detalle del producto
        return redirect('produccion:detalle_producto', producto_id=producto_id)

    # Si alguien intenta acceder a la URL con GET, simplemente lo redirigimos
    # sin hacer nada.
    return redirect('produccion:detalle_producto', producto_id=producto_id)

@login_required
def editar_formulacion_item(request, producto_id, item_id):
    """
    Edita la cantidad de un insumo en la formulación de un producto.
    """
    # Seguridad: Aseguramos que el item pertenece a un producto de la mipyme del usuario
    item = get_object_or_404(
        Formulacion,
        id=item_id,
        producto__id=producto_id,
        producto__mipyme=request.user.mipyme
    )

    if request.method == 'POST':
        # Pasamos 'instance=item' para que el formulario sepa qué objeto actualizar
        form = FormulacionUpdateForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            # Redirigimos de vuelta a la página de detalle del producto
            return redirect('produccion:detalle_producto', producto_id=producto_id)
    else:
        # Si es GET, creamos el formulario pre-llenado con los datos del item existente
        form = FormulacionUpdateForm(instance=item)

    contexto = {
        'form': form,
        'item': item,
        'nombrepine': request.user.mipyme.nombre
    }
    return render(request, 'produccion/editar_formulacion_item.html', contexto)


@login_required
def editar_insumo(request, insumo_id):
    """
    Gestiona la edición de un insumo existente.
    """
    # Seguridad: Obtenemos el insumo asegurándonos que pertenece a la Mipyme del usuario
    insumo = get_object_or_404(Insumo, id=insumo_id, mipyme=request.user.mipyme)

    if request.method == 'POST':
        # Pasamos 'instance=insumo' para indicarle al formulario que estamos actualizando
        form = InsumoForm(request.POST, instance=insumo)
        if form.is_valid():
            form.save()
            return redirect('produccion:lista_insumos') # Redirigimos a la lista
    else:
        # Si es GET, mostramos el formulario pre-llenado con los datos del insumo
        form = InsumoForm(instance=insumo)

    contexto = {
        'form': form,
        'insumo': insumo, # Pasamos el insumo para poder usar su nombre en el título
        'nombrepine': request.user.mipyme.nombre
    }
    # Reutilizaremos la plantilla de creación, ya que el formulario es el mismo
    return render(request, 'produccion/crear_insumo.html', contexto)


@login_required
def eliminar_insumo(request, insumo_id):
    """
    Elimina un insumo específico.
    """
    # Seguridad: Obtenemos el insumo asegurándonos que pertenece a la Mipyme del usuario
    insumo_a_borrar = get_object_or_404(Insumo, id=insumo_id, mipyme=request.user.mipyme)

    # Solo proceder si la solicitud es de tipo POST
    if request.method == 'POST':
        insumo_a_borrar.delete()
        # Redirigir de vuelta a la lista de insumos
        return redirect('produccion:lista_insumos')

    # Si alguien intenta acceder a la URL con GET, simplemente lo redirigimos
    return redirect('produccion:lista_insumos')


# --- INICIO DE NUEVAS VISTAS PARA PROCESOS ---

@login_required
def lista_procesos(request):
    """
    Muestra una lista de todos los procesos de la Mipyme del usuario.
    """
    procesos = Proceso.objects.filter(mipyme=request.user.mipyme).order_by('nombre')
    contexto = {
        'procesos': procesos,
        'nombrepine': request.user.mipyme.nombre
    }
    return render(request, 'produccion/lista_procesos.html', contexto)

@login_required
@rol_requerido('ADMIN', 'EDITOR')
def crear_proceso(request):
    """
    Gestiona la creación de un nuevo proceso.
    """
    if request.method == 'POST':
        form = ProcesoForm(request.POST)
        if form.is_valid():
            nuevo_proceso = form.save(commit=False)
            nuevo_proceso.mipyme = request.user.mipyme
            nuevo_proceso.save()
            return redirect('produccion:lista_procesos')
    else:
        form = ProcesoForm()

    contexto = {'form': form}
    return render(request, 'produccion/crear_proceso.html', contexto)


@login_required
@rol_requerido('ADMIN', 'EDITOR')
def editar_proceso(request, proceso_id):
    """
    Gestiona la edición de un proceso existente.
    """
    proceso = get_object_or_404(Proceso, id=proceso_id, mipyme=request.user.mipyme)
    if request.method == 'POST':
        form = ProcesoForm(request.POST, instance=proceso)
        if form.is_valid():
            form.save()
            return redirect('produccion:lista_procesos')
    else:
        form = ProcesoForm(instance=proceso)
    contexto = {'form': form, 'proceso': proceso}
    return render(request, 'produccion/crear_proceso.html', contexto)


@login_required
@rol_requerido('ADMIN')
def eliminar_proceso(request, proceso_id):
    """
    Elimina un proceso específico.
    """
    proceso_a_borrar = get_object_or_404(Proceso, id=proceso_id, mipyme=request.user.mipyme)
    if request.method == 'POST':
        proceso_a_borrar.delete()
        return redirect('produccion:lista_procesos')
    return redirect('produccion:lista_procesos')

# --- FIN DE NUEVAS VISTAS PARA PROCESOS ---


# --- INICIO DE NUEVAS VISTAS PARA PASOS DE PRODUCCIÓN ---

@login_required
def editar_paso_produccion(request, producto_id, paso_id):
    """
    Edita el tiempo de un proceso en la ruta de producción de un producto.
    """
    paso = get_object_or_404(
        PasoDeProduccion, id=paso_id, producto__id=producto_id, producto__mipyme=request.user.mipyme
    )
    if request.method == 'POST':
        form = PasoUpdateForm(request.POST, instance=paso)
        if form.is_valid():
            form.save()
            return redirect('produccion:detalle_producto', producto_id=producto_id)
    else:
        form = PasoUpdateForm(instance=paso)

    contexto = {'form': form,
                'paso': paso,
                'nombrepine': request.user.mipyme.nombre
                }
    return render(request, 'produccion/editar_paso_produccion.html', contexto)


@login_required
def eliminar_paso_produccion(request, producto_id, paso_id):
    """
    Elimina un proceso de la ruta de producción de un producto.
    """
    paso_a_borrar = get_object_or_404(
        PasoDeProduccion, id=paso_id, producto__id=producto_id, producto__mipyme=request.user.mipyme
    )
    if request.method == 'POST':
        paso_a_borrar.delete()
        return redirect('produccion:detalle_producto', producto_id=producto_id)
    return redirect('produccion:detalle_producto', producto_id=producto_id)

# --- FIN DE NUEVAS VISTAS PARA PASOS DE PRODUCCIÓN ---


@login_required
def calculadora_lotes(request, producto_id):
    """
    Calculadora para estimar cantidades de insumos y costos para un lote de producción.
    """
    producto = get_object_or_404(Producto, id=producto_id, mipyme=request.user.mipyme)

    resultados = None
    costo_total_insumos = 0
    costo_total_procesos = 0
    ingresos_estimados = 0
    ganancia_estimada = 0

    if request.method == 'POST':
        form = CalculadoraLotesForm(request.POST)
        if form.is_valid():
            cantidad_unidades = form.cleaned_data['cantidad_unidades']

            # Calcular insumos para el lote
            resultados = []
            for item in producto.formulacion.all():
                cantidad_total = item.cantidad * cantidad_unidades
                costo_unitario = item.insumo.costo_unitario
                costo_con_desperdicio = cantidad_total * costo_unitario * (1 + (item.porcentaje_desperdicio / 100))
                costo_total_insumos += costo_con_desperdicio
                resultados.append({
                    'insumo': item.insumo.nombre,
                    'unidad': item.insumo.unidad.abreviatura,
                    'cantidad_por_unidad': item.cantidad,
                    'cantidad_total': cantidad_total,
                    'costo': costo_con_desperdicio,
                })

            # Calcular procesos para el lote
            for paso in producto.pasodeproduccion_set.all():
                costo_proceso_lote = (decimal.Decimal(paso.tiempo_en_minutos) / 60) * paso.proceso.costo_por_hora * cantidad_unidades
                costo_total_procesos += costo_proceso_lote

            # Calcular ingresos y ganancia
            ingresos_estimados = producto.precio_venta * cantidad_unidades
            ganancia_estimada = producto.margen_de_ganancia * cantidad_unidades
    else:
        form = CalculadoraLotesForm()

    costo_total = costo_total_insumos + costo_total_procesos

    contexto = {
        'producto': producto,
        'form': form,
        'resultados': resultados,
        'costo_total_insumos': costo_total_insumos,
        'costo_total_procesos': costo_total_procesos,
        'costo_total': costo_total,
        'ingresos_estimados': ingresos_estimados,
        'ganancia_estimada': ganancia_estimada,
        'nombrepine': request.user.mipyme.nombre
    }
    return render(request, 'produccion/calculadora_lotes.html', contexto)

# --- FIN DE CALCULADORA ---