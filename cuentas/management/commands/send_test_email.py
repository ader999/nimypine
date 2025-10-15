from django.core.management.base import BaseCommand
from django.core.mail import send_mail

class Command(BaseCommand):
    help = 'Send a test email to verify email configuration'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='The email address to send the test to')

    def handle(self, *args, **options):
        email = options['email']
        subject = 'Test Email from MiPymes'
        message = 'This is a test email to verify that the email configuration is working correctly.'
        from_email = None  # Will use DEFAULT_FROM_EMAIL

        try:
            send_mail(subject, message, from_email, [email])
            self.stdout.write(self.style.SUCCESS(f'Test email sent successfully to {email}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to send test email: {e}'))