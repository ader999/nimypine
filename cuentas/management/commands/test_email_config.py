# cuentas/management/commands/test_email_config.py
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.mail import EmailMessage
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Prueba la configuración de email y envía un email de prueba'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to',
            type=str,
            help='Email de destino para la prueba',
            default='codigoader@gmail.com'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== PRUEBA DE CONFIGURACIÓN DE EMAIL ===\n'))
        
        # Mostrar configuración actual
        self.stdout.write(self.style.WARNING('Configuración de Django settings:'))
        self.stdout.write(f'EMAIL_BACKEND: {settings.EMAIL_BACKEND}')
        self.stdout.write(f'EMAIL_HOST: {settings.EMAIL_HOST}')
        self.stdout.write(f'EMAIL_PORT: {settings.EMAIL_PORT}')
        self.stdout.write(f'EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}')
        self.stdout.write(f'EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
        self.stdout.write(f'EMAIL_HOST_PASSWORD: {"*" * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else "None"}')
        self.stdout.write(f'DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}\n')
        
        # Mostrar variables de entorno directamente
        self.stdout.write(self.style.WARNING('Variables de entorno (os.environ):'))
        self.stdout.write(f'EMAIL_HOST: {os.environ.get("EMAIL_HOST", "NO DEFINIDA")}')
        self.stdout.write(f'EMAIL_USER: {os.environ.get("EMAIL_USER", "NO DEFINIDA")}')
        self.stdout.write(f'EMAIL_PWS: {"*" * len(os.environ.get("EMAIL_PWS", "")) if os.environ.get("EMAIL_PWS") else "NO DEFINIDA"}\n')
        
        # Intentar enviar email de prueba
        to_email = options['to']
        self.stdout.write(self.style.WARNING(f'Intentando enviar email de prueba a: {to_email}'))
        
        try:
            email = EmailMessage(
                subject='Prueba de configuración de email - NimyPine',
                body='Este es un email de prueba para verificar la configuración de SMTP.',
                to=[to_email],
            )
            
            self.stdout.write('Enviando email...')
            result = email.send()
            
            self.stdout.write(self.style.SUCCESS(f'\n✓ Email enviado exitosamente!'))
            self.stdout.write(self.style.SUCCESS(f'email.send() retornó: {result}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Error al enviar email:'))
            self.stdout.write(self.style.ERROR(f'Tipo: {type(e).__name__}'))
            self.stdout.write(self.style.ERROR(f'Mensaje: {e}'))
            
            import traceback
            self.stdout.write(self.style.ERROR(f'\nTraceback completo:'))
            self.stdout.write(self.style.ERROR(traceback.format_exc()))