# cuentas/utils.py
import random
import string
import logging
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger(__name__)


def enviar_email_confirmacion(user):
    """
    Envía el email de confirmación y retorna el código generado.
    El código se guarda en la BD antes de intentar enviar el email.
    """
    logger.info(f"=== INICIO enviar_email_confirmacion para {user.email} ===")
    logger.info(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    logger.info(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    logger.info(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    logger.info(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    logger.info(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    logger.info(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    codigo = ''.join(random.choices(string.digits, k=6))
    user.codigo_confirmacion = codigo
    user.save()
    logger.info(f"Código generado y guardado: {codigo}")
    
    subject = 'Confirma tu correo electrónico'
    mensaje = render_to_string('cuentas/email_confirmacion.html', {'codigo': codigo})
    logger.info(f"Template renderizado correctamente")
    
    try:
        logger.info(f"Creando EmailMessage...")
        email = EmailMessage(
            subject,
            mensaje,
            to=[user.email],
        )
        email.content_subtype = 'html'
        logger.info(f"Intentando enviar email...")
        result = email.send()
        logger.info(f"Email.send() retornó: {result}")
        logger.info(f"Email de confirmación enviado exitosamente a {user.email}")
    except Exception as e:
        logger.error(f"ERROR al enviar email de confirmación a {user.email}: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"Traceback completo:\n{traceback.format_exc()}")
    
    logger.info(f"=== FIN enviar_email_confirmacion ===")
    return codigo


def enviar_email_bienvenida(user):
    """
    Envía el email de bienvenida al usuario.
    """
    logger.info(f"=== INICIO enviar_email_bienvenida para {user.email} ===")
    
    subject = 'Bienvenido a NimyPine - Tus credenciales de acceso'
    mensaje = render_to_string('cuentas/email_bienvenida.html', {'user': user})
    logger.info(f"Template renderizado correctamente")
    
    try:
        logger.info(f"Creando EmailMessage...")
        email = EmailMessage(
            subject,
            mensaje,
            to=[user.email],
        )
        email.content_subtype = 'html'
        logger.info(f"Intentando enviar email...")
        result = email.send()
        logger.info(f"Email.send() retornó: {result}")
        logger.info(f"Email de bienvenida enviado exitosamente a {user.email}")
    except Exception as e:
        logger.error(f"ERROR al enviar email de bienvenida a {user.email}: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"Traceback completo:\n{traceback.format_exc()}")
    
    logger.info(f"=== FIN enviar_email_bienvenida ===")