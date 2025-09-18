# cuentas/views.py
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .decorators import rol_requerido
from .forms import RegistroMipymeForm, CreacionUsuarioMipymeForm, EditarRolUsuarioForm, RegistroCreadorForm, SoloMipymeForm
from .models import Mipyme, Usuario
from .funciones import generar_username_unico


def pagina_inicio(request):
    # Por ahora, solo renderizamos la plantilla.
    # Más adelante puedes pasarle datos a través del diccionario de contexto.
    return render(request, 'inicio.html')

@login_required
def crear_mipyme_para_creador_view(request):
    # Redirigir si el usuario ya tiene una mipyme
    if request.user.mipyme:
        return redirect('produccion:panel')  # O a donde corresponda

    if request.method == 'POST':
        form = SoloMipymeForm(request.POST)
        if form.is_valid():
            mipyme = form.save()  # Guardamos la nueva Mipyme

            # Actualizamos al usuario actual
            usuario = request.user
            usuario.mipyme = mipyme
            usuario.es_admin_mipyme = True
            usuario.save()

            return redirect('produccion:panel')
    else:
        form = SoloMipymeForm()

    return render(request, 'cuentas/crear_mipyme_para_creador.html', {'form': form})

@login_required
def lista_usuarios_mipyme(request):
    """
    Muestra una lista de todos los usuarios que pertenecen a la misma Mipyme
    que el usuario que ha iniciado sesión.
    """
    # Obtenemos todos los usuarios que comparten la misma mipyme
    usuarios_equipo = Usuario.objects.filter(mipyme=request.user.mipyme).order_by('username')

    contexto = {
        'equipo': usuarios_equipo,
    }
    # Usaremos una plantilla dentro de la app 'cuentas'
    return render(request, 'cuentas/lista_equipo.html', contexto)


def pagina_seleccion_registro(request):
    """
    Muestra una página donde el usuario elige si registrarse como Creador o como Mipyme.
    """
    return render(request, 'cuentas/seleccion_registro.html')

def registro_creador_view(request):
    if request.method == 'POST':
        form = RegistroCreadorForm(request.POST)
        if form.is_valid():
            datos = form.cleaned_data
            # Creamos el usuario
            username = generar_username_unico(datos['first_name'], datos['last_name'])
            usuario = Usuario.objects.create_user(
                username=username,
                email=datos['email'],
                password=datos['password'],
                first_name=datos['first_name'],
                last_name=datos['last_name'],
                es_creador_contenido=True # ¡La clave está aquí!
            )
            login(request, usuario)
            return redirect('marketplace_listado') # O a donde quieras dirigirlo
    else:
        form = RegistroCreadorForm()
    return render(request, 'cuentas/registro_creador.html', {'form': form})


def registro_mipyme_view(request):
    if request.method == 'POST':
        form = RegistroMipymeForm(request.POST)
        if form.is_valid():
            datos = form.cleaned_data
            # 1. Crear la Mipyme
            mipyme = Mipyme.objects.create(
                nombre=datos['nombre_empresa'],
                identificador_fiscal=datos.get('identificador_fiscal'),
                tipo=datos['tipo_empresa'],
                sector=datos['sector_economico']
            )
            # 2. Crear el Usuario Administrador
            username = generar_username_unico(datos['first_name'], datos['last_name'])
            admin_usuario = Usuario.objects.create_user(
                username=username,
                email=datos['email'],
                password=datos['password'],
                first_name=datos['first_name'],
                last_name=datos['last_name'],
                mipyme=mipyme, # Lo asociamos a la nueva Mipyme
                es_admin_mipyme=True,
                es_creador_contenido = True
            )
            login(request, admin_usuario)
            return redirect('produccion:panel') # O al panel de la Mipyme
    else:
        form = RegistroMipymeForm()
    return render(request, 'cuentas/registro_mipyme.html', {'form': form})


@login_required
def crear_usuario_mipyme(request):
    """
    Gestiona la creación de un nuevo usuario asociado a la Mipyme del admin.
    """
    if request.method == 'POST':
        form = CreacionUsuarioMipymeForm(request.POST)
        if form.is_valid():
            nuevo_usuario = form.save(commit=False)
            # ¡Paso CRÍTICO! Asignamos la Mipyme del usuario creador al nuevo usuario.
            nuevo_usuario.mipyme = request.user.mipyme
            nuevo_usuario.save()
            # Redirigimos a la lista del equipo para ver al nuevo miembro
            return redirect('cuentas:lista_equipo')
    else:
        form = CreacionUsuarioMipymeForm()

    contexto = {
        'form': form,
    }
    return render(request, 'cuentas/crear_usuario_mipyme.html', contexto)



@rol_requerido('ADMIN') # Solo un usuario con rol ADMIN (o el dueño) puede cambiar roles
def gestionar_rol_usuario(request, usuario_id):
    usuario_a_editar = get_object_or_404(Usuario, id=usuario_id, mipyme=request.user.mipyme)

    if request.method == 'POST':
        form = EditarRolUsuarioForm(request.POST, instance=usuario_a_editar)
        if form.is_valid():
            form.save()
            return redirect('cuentas:lista_equipo')
    else:
        form = EditarRolUsuarioForm(instance=usuario_a_editar)

    contexto = {
        'form': form,
        'usuario_a_editar': usuario_a_editar
    }
    return render(request, 'cuentas/gestionar_rol.html', contexto)


def manejador_error_403(request, exception):
    """
    Vista personalizada para manejar errores 403 (Permission Denied).
    """
    contexto = {}
    # Pasamos el estado 403 para que la respuesta HTTP sea la correcta
    return render(request, 'cuentas/403.html', contexto, status=403)

def manejador_error_404(request, exception):
    """
    Vista para manejar los errores 404 (Página no encontrada).
    """
    return render(request, 'cuentas/404.html', status=404)


def manejador_error_500(request):
    """
    Vista para manejar los errores 500 (Error interno del servidor).
    """
    return render(request, 'cuentas/500.html', status=500)