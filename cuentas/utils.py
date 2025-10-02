# cuentas/utils.py
import random
import string
import logging
import os
import resend
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger(__name__)

def enviar_email_confirmacion(user):
    """
    Envía el email de confirmación usando Resend y retorna el código generado.
    El código se guarda en la BD antes de intentar enviar el email.
    """
    logger.info(f"=== INICIO enviar_email_confirmacion para {user.email} (usando Resend) ===")
    
    # Configurar API Key de Resend desde variables de entorno
    api_key = os.environ.get('RESEND_API_KEY')
    if not api_key:
        logger.error("RESEND_API_KEY no encontrada en las variables de entorno.")
        return None
    resend.api_key = api_key
    
    codigo = ''.join(random.choices(string.digits, k=6))
    user.codigo_confirmacion = codigo
    user.save()
    logger.info(f"Código de confirmación generado y guardado: {codigo}")
    
    subject = 'Confirma tu correo electrónico en NimyPine'
    html_body = render_to_string('cuentas/email_confirmacion.html', {'codigo': codigo})
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

def enviar_email_bienvenida(user):
    """
    Envía el email de bienvenida al usuario usando Resend.
    """
    logger.info(f"=== INICIO enviar_email_bienvenida para {user.email} (usando Resend) ===")

    api_key = os.environ.get('RESEND_API_KEY')
    if not api_key:
        logger.error("RESEND_API_KEY no encontrada en las variables de entorno para email de bienvenida.")
        return
    resend.api_key = api_key

    subject = '¡Bienvenido a NimyPine!'
    html_body = render_to_string('cuentas/email_bienvenida.html', {'user': user})
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