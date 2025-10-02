release: python manage.py collectstatic --noinput
web: gunicorn mipymes_project.wsgi --timeout 180 --workers 2 --graceful-timeout 30 --keep-alive 5