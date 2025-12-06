# cuentas/views.py
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.urls import reverse
from .decorators import rol_requerido
from .forms import RegistroMipymeForm, CreacionUsuarioMipymeForm, EditarRolUsuarioForm, RegistroCreadorForm, SoloMipymeForm
from .models import Mipyme, Usuario
from .funciones import generar_username_unico
from .utils import enviar_email_confirmacion, enviar_email_bienvenida, enviar_email_reset_password


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.email_confirmado:
                login(request, user)
                return redirect('cuentas:inicio')  # O a donde corresponda
            else:
                # Usuario no confirmado, enviar a confirmación
                enviar_email_confirmacion(user, request)
                request.session['user_id_confirmacion'] = user.id
                messages.info(request, 'Tu email no está confirmado. Revisa tu correo para el código de confirmación.')
                return redirect('cuentas:confirmar_email')
        else:
            messages.error(request, 'Credenciales inválidas.')
    else:
        form = AuthenticationForm()
    form.fields['username'].widget.attrs.update({'class': 'form-control'})
    form.fields['username'].label = 'Usuario o Email'
    form.fields['password'].widget.attrs.update({'class': 'form-control'})
    return render(request, 'cuentas/login.html', {'form': form})


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
            mipyme = form.save(commit=False)  # No guardamos aún
            mipyme.propietario = request.user # Asignamos el propietario
            mipyme.save()  # Ahora sí, guardamos la Mipyme

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
        'nombrepine': request.user.mipyme.nombre
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
            enviar_email_confirmacion(usuario, request)
            request.session['user_id_confirmacion'] = usuario.id
            messages.success(request, 'Usuario creado. Revisa tu correo para confirmar tu email.')
            return redirect('cuentas:confirmar_email')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegistroCreadorForm()
    return render(request, 'cuentas/registro_creador.html', {'form': form})


def registro_mipyme_view(request):
    if request.method == 'POST':
        form = RegistroMipymeForm(request.POST)
        if form.is_valid():
            try:
                datos = form.cleaned_data
                # 1. Crear la Mipyme
                mipyme = Mipyme.objects.create(
                    nombre=datos['nombre_empresa'],
                    identificador_fiscal=datos.get('identificador_fiscal') or None,
                    sector=datos['sector_economico'],
                    mostrar_productos_en_marketplace=False
                )
                # 2. Crear el Usuario Administrador
                username = generar_username_unico(datos['first_name'], datos['last_name'])
                admin_usuario = Usuario.objects.create_user(
                    username=username,
                    email=datos['email'],
                    password=datos['password'],
                    first_name=datos['first_name'],
                    last_name=datos['last_name'],
                    mipyme=mipyme,  # Lo asociamos a la nueva Mipyme
                    es_admin_mipyme=True,
                    es_creador_contenido=True
                )
                # 3. Asignar el propietario a la Mipyme
                mipyme.propietario = admin_usuario
                mipyme.save()

                enviar_email_confirmacion(admin_usuario, request)
                request.session['user_id_confirmacion'] = admin_usuario.id
                messages.success(request, 'Usuario creado. Revisa tu correo para confirmar tu email.')
                return redirect('cuentas:confirmar_email')
            except Exception as e:
                messages.error(request, f'Error al registrar la Mipyme: {e}. Asegúrate de que la base de datos esté configurada y accesible.')

        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
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


def confirmar_email_view(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        user_id = request.session.get('user_id_confirmacion')
        if user_id:
            try:
                user = Usuario.objects.get(id=user_id)
                if user.codigo_confirmacion == codigo:
                    user.email_confirmado = True
                    user.codigo_confirmacion = None
                    user.save()
                    enviar_email_bienvenida(user, request)
                    del request.session['user_id_confirmacion']
                    # Especificar el backend de autenticación explícitamente
                    login(request, user, backend='cuentas.backends.EmailOrUsernameModelBackend')
                    messages.success(request, 'Email confirmado exitosamente. Bienvenido!')
                    if user.mipyme:
                        return redirect('produccion:panel')
                    else:
                        return redirect('marketplace_listado')
                else:
                    messages.error(request, 'Código incorrecto. Inténtalo de nuevo.')
            except Usuario.DoesNotExist:
                messages.error(request, 'Usuario no encontrado.')
        else:
            messages.error(request, 'Sesión expirada. Regístrate de nuevo.')
            return redirect('cuentas:seleccion_registro')
    return render(request, 'cuentas/email/confirmar_email.html')


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


@login_required
def no_mipyme_asociada(request):
    """
    Vista para usuarios que no tienen una Mipyme asociada.
    """
    return render(request, 'cuentas/no_mipyme_asociada.html')

def manejador_error_500(request):
    """
    Vista para manejar los errores 500 (Error interno del servidor).
    """
    return render(request, 'cuentas/500.html', status=500)

from django.http import JsonResponse
from django.db import connection
from django.db.utils import OperationalError

def health_check(request):
    try:
        # Intenta forzar una conexión a la base de datos haciendo una consulta simple
        connection.cursor()
        return JsonResponse({"status": "ok", "message": "La conexión a la base de datos funciona."})
    except OperationalError as e:
        # Si falla, devuelve un error
        return JsonResponse({"status": "error", "message": f"No se pudo conectar a la base de datos: {e}"}, status=500)

from .utils import enviar_email_confirmacion, enviar_email_bienvenida, enviar_email_reset_password
from django.contrib.auth.tokens import default_token_generator

def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get('email')
        if not email:
            return JsonResponse({"success": False, "message": "Por favor ingresa un correo electrónico."})
            
        users = Usuario.objects.filter(email=email, is_active=True)
        if users.exists():
            for user in users:
                enviar_email_reset_password(user, request)
        
        # Por seguridad, siempre respondemos con éxito para no revelar si el correo existe o no (Enumeración de usuarios)
        # Y garantizamos que NO se envió nada si el usuario no existía (porque no entró al if users.exists())
        return JsonResponse({"success": True, "message": "Si el correo existe en nuestra base de datos, recibirás las instrucciones para restablecer tu contraseña."})
            
    return JsonResponse({"success": False, "message": "Método no permitido."}, status=405)