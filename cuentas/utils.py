# cuentas/utils.py
import random
import string
import logging
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def enviar_email_confirmacion(user):
    """
    Envía el email de confirmación y retorna el código generado.
    El código se guarda en la BD antes de intentar enviar el email.
    """
    codigo = ''.join(random.choices(string.digits, k=6))
    user.codigo_confirmacion = codigo
    user.save()
    
    subject = 'Confirma tu correo electrónico'
    mensaje = render_to_string('cuentas/email_confirmacion.html', {'codigo': codigo})
    
    try:
        email = EmailMessage(
            subject,
            mensaje,
            to=[user.email],
        )
        email.content_subtype = 'html'
        email.send()
        logger.info(f"Email de confirmación enviado exitosamente a {user.email}")
    except Exception as e:
        logger.error(f"Error al enviar email de confirmación a {user.email}: {e}")
    
    return codigo


def enviar_email_bienvenida(user):
    """
    Envía el email de bienvenida al usuario.
    """
    subject = 'Bienvenido a NimyPine - Tus credenciales de acceso'
    mensaje = render_to_string('cuentas/email_bienvenida.html', {'user': user})
    
    try:
        email = EmailMessage(
            subject,
            mensaje,
            to=[user.email],
        )
        email.content_subtype = 'html'
        email.send()
        logger.info(f"Email de bienvenida enviado exitosamente a {user.email}")
    except Exception as e:
        logger.error(f"Error al enviar email de bienvenida a {user.email}: {e}")