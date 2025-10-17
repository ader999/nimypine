import os
import django
from django.conf import settings

def pytest_configure():
    # Configura Django solo una vez
    if not settings.configured:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mipymes_project.settings')
        django.setup()