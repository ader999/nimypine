# produccion/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Producto, Insumo, Formulacion # Importamos el modelo Producto
from .forms import ProductoForm, FormulacionForm, InsumoForm, FormulacionUpdateForm
from cuentas.decorators import rol_requerido


# El decorador @login_required protege esta vista.
# Si un usuario no autenticado intenta acceder, será redirigido a la página de login.
@login_required
def panel_produccion(request):
    """
    Vista principal de la aplicación 'produccion'.
    Carga el panel de control con las funcionalidades de negocio.
    """
    # Aquí puedes agregar lógica para obtener datos de la base de datos,
    # como la lista de productos, para pasarla a la plantilla.
    # Por ahora, la dejamos simple.

    contexto = {
        'titulo': 'Panel de Producción',
        'usuario': request.user,
        'nombrepine': request.user.mipyme.nombre
    }

    # Renderiza la plantilla HTML que crearemos en el siguiente paso.
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
    }
    return render(request, 'produccion/crear_producto.html', contexto)


@login_required
def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, mipyme=request.user.mipyme)
    mipyme_actual = request.user.mipyme

    # Lógica para manejar el envío del formulario de añadir insumo
    if request.method == 'POST':
        form = FormulacionForm(request.POST, mipyme=mipyme_actual)
        if form.is_valid():
            # Evitar duplicados: Comprobar si ese insumo ya está en la receta
            insumo_seleccionado = form.cleaned_data['insumo']
            if not Formulacion.objects.filter(producto=producto, insumo=insumo_seleccionado).exists():
                nuevo_item = form.save(commit=False)
                nuevo_item.producto = producto  # Asignamos el producto actual
                nuevo_item.save()
            # Siempre redirigimos para evitar re-envío del formulario al recargar (Patrón PRG)
            return redirect('produccion:detalle_producto', producto_id=producto.id)
    else:
        # Si es una petición GET, creamos un formulario vacío
        form = FormulacionForm(mipyme=mipyme_actual)

    # Obtenemos la lista de insumos de la formulación para mostrarla
    formulacion_items = Formulacion.objects.filter(producto=producto).order_by('insumo__nombre')

    contexto = {
        'producto': producto,
        'formulacion_items': formulacion_items,
        'form': form,  # Pasamos el formulario a la plantilla
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