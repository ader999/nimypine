# cuentas/views.py
import re
import random
import string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from .decorators import rol_requerido
from .forms import RegistroMipymeForm, CreacionUsuarioMipymeForm, EditarRolUsuarioForm, RegistroCreadorForm, SoloMipymeForm
from .models import Mipyme, Usuario
from .funciones import generar_username_unico


def enviar_email_confirmacion(user):
    codigo = ''.join(random.choices(string.digits, k=6))
    user.codigo_confirmacion = codigo
    user.save()
    subject = 'Confirma tu correo electrónico'
    html_message = render_to_string('cuentas/email_confirmacion.html', {'codigo': codigo})
    send_mail(
        subject=subject,
        message='',
        from_email=None,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False
    )


def enviar_email_bienvenida(user):
    subject = 'Bienvenido a NimyPine - Tus credenciales de acceso'
    html_message = render_to_string('cuentas/email_bienvenida.html', {'user': user})
    send_mail(
        subject=subject,
        message='',
        from_email=None,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False
    )


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
                enviar_email_confirmacion(user)
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
            enviar_email_confirmacion(usuario)
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
                    identificador_fiscal=datos.get('identificador_fiscal'),
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
                    mipyme=mipyme,  # Lo asociamos a la nueva Mipyme
                    es_admin_mipyme=True,
                    es_creador_contenido=True
                )
                enviar_email_confirmacion(admin_usuario)
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
                    enviar_email_bienvenida(user)
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
    return render(request, 'cuentas/confirmar_email.html')


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

def test_email_view(request):
    """
    Vista para probar el envío de emails.
    """
    try:
        send_mail(
            subject='Test Email from MiPymes',
            message='This is a test email to verify that the email configuration is working correctly.',
            from_email=None,
            recipient_list=['aderjasmirzeasrocha@gmail.com'],
            fail_silently=False
        )
        messages.success(request, 'Test email sent successfully to aderjasmirzeasrocha@gmail.com')
    except Exception as e:
        messages.error(request, f'Failed to send test email: {str(e)}')
    return redirect('cuentas:seleccion_registro')
def manejador_error_500(request):
    """
    Vista para manejar los errores 500 (Error interno del servidor).
    """
    return render(request, 'cuentas/500.html', status=500)