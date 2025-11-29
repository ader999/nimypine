# cuentas/utils.py
import random
import string
import logging
import os
import resend
from django.template.loader import render_to_string
from django.conf import settings
from django.core.files.storage import default_storage

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

logger = logging.getLogger(__name__)

def enviar_email_reset_password(user, request):
    """
    Envía el email de restablecimiento de contraseña usando Resend.
    """
    logger.info(f"=== INICIO enviar_email_reset_password para {user.email} (usando Resend) ===")
    
    api_key = os.environ.get('RESEND')
    if not api_key:
        logger.error("RESEND (API Key) no encontrada.")
        return False
    resend.api_key = api_key

    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    protocol = 'https' if request.is_secure() else 'http'
    domain = request.get_host()
    
    # Generar URL firmada del logo desde el bucket
    try:
        logo_url = default_storage.url('icono.png')
    except Exception as e:
        logger.error(f"Error generando URL del logo: {e}")
        # Fallback a URL estática si falla la generación (aunque probablemente falle también si es privado)
        logo_url = f"https://{settings.MINIO_STORAGE_ENDPOINT}/{settings.MINIO_STORAGE_MEDIA_BUCKET_NAME}/icono.png"

    context = {
        'email': user.email,
        'domain': domain,
        'site_name': 'NimyPine',
        'uid': uid,
        'token': token,
        'protocol': protocol,
        'user': user,
        'logo_url': logo_url,
    }
    
    subject = 'Restablecer tu contraseña en NimyPine'
    html_body = render_to_string('cuentas/email/password_reset_email.html', context)
    
    try:
        params = {
            "from": "NimyPine <noreply@codeader.com>",
            "to": [user.email],
            "subject": subject,
            "html": html_body,
        }
        resend.Emails.send(params)
        logger.info(f"Email de reset enviado a {user.email}")
        return True
    except Exception as e:
        logger.error(f"Error enviando email reset: {e}")
        return False

def enviar_email_confirmacion(user, request=None):
    """
    Envía el email de confirmación usando Resend y retorna el código generado.
    El código se guarda en la BD antes de intentar enviar el email.
    """
    logger.info(f"=== INICIO enviar_email_confirmacion para {user.email} (usando Resend) ===")
    
    # Configurar API Key de Resend desde variables de entorno
    api_key = os.environ.get('RESEND')
    if not api_key:
        logger.error("RESEND (API Key) no encontrada en las variables de entorno.")
        return None
    resend.api_key = api_key
    
    codigo = ''.join(random.choices(string.digits, k=6))
    user.codigo_confirmacion = codigo
    user.save()
    logger.info(f"Código de confirmación generado y guardado: {codigo}")
    
    # Obtener dominio y protocolo para URL absoluta de imágenes (fallback si falla bucket)
    protocol = 'https'
    domain = 'nimypine.com' # Fallback default
    if request:
        protocol = 'https' if request.is_secure() else 'http'
        domain = request.get_host()

    # Generar URL firmada del logo desde el bucket
    try:
        logo_url = default_storage.url('icono.png')
    except Exception as e:
        logger.error(f"Error generando URL del logo: {e}")
        logo_url = f"https://{settings.MINIO_STORAGE_ENDPOINT}/{settings.MINIO_STORAGE_MEDIA_BUCKET_NAME}/icono.png"

    context = {
        'codigo': codigo,
        'protocol': protocol,
        'domain': domain,
        'logo_url': logo_url,
    }

    subject = 'Confirma tu correo electrónico en NimyPine'
    html_body = render_to_string('cuentas/email/email_confirmacion.html', context)
    logger.info("Template de email renderizado correctamente.")
    
    try:
        logger.info(f"Intentando enviar email a {user.email} vía Resend...")
        params = {
            "from": "NimyPine <noreply@codeader.com>",
            "to": [user.email],
            "subject": subject,
            "html": html_body,
        }
        email = resend.Emails.send(params)
        logger.info(f"Email enviado exitosamente a {user.email}. Response: {email}")
        
    except Exception as e:
        logger.error(f"ERROR al enviar email de confirmación a {user.email} con Resend: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"Traceback completo:\n{traceback.format_exc()}")
    
    logger.info(f"=== FIN enviar_email_confirmacion ===")
    return codigo

def enviar_email_bienvenida(user, request=None):
    """
    Envía el email de bienvenida al usuario usando Resend.
    """
    logger.info(f"=== INICIO enviar_email_bienvenida para {user.email} (usando Resend) ===")

    api_key = os.environ.get('RESEND')
    if not api_key:
        logger.error("RESEND (API Key) no encontrada en las variables de entorno para email de bienvenida.")
        return
    resend.api_key = api_key

    # Obtener dominio y protocolo para URL absoluta de imágenes (fallback)
    protocol = 'https'
    domain = 'nimypine.com' # Fallback default
    if request:
        protocol = 'https' if request.is_secure() else 'http'
        domain = request.get_host()

    # Generar URL firmada del logo desde el bucket
    try:
        logo_url = default_storage.url('icono.png')
    except Exception as e:
        logger.error(f"Error generando URL del logo: {e}")
        logo_url = f"https://{settings.MINIO_STORAGE_ENDPOINT}/{settings.MINIO_STORAGE_MEDIA_BUCKET_NAME}/icono.png"

    context = {
        'user': user,
        'protocol': protocol,
        'domain': domain,
        'logo_url': logo_url,
    }

    subject = '¡Bienvenido a NimyPine!'
    html_body = render_to_string('cuentas/email/email_bienvenida.html', context)
    logger.info("Template de email de bienvenida renderizado correctamente.")

    try:
        logger.info(f"Intentando enviar email de bienvenida a {user.email} vía Resend...")
        params = {
            "from": "NimyPine <noreply@codeader.com>",
            "to": [user.email],
            "subject": subject,
            "html": html_body,
        }
        email = resend.Emails.send(params)
        logger.info(f"Email de bienvenida enviado exitosamente a {user.email}. Response: {email}")

    except Exception as e:
        logger.error(f"ERROR al enviar email de bienvenida a {user.email} con Resend: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"Traceback completo:\n{traceback.format_exc()}")

    logger.info(f"=== FIN enviar_email_bienvenida ===")