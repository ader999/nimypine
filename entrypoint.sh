#!/bin/bash
# Recopila archivos estáticos
python manage.py collectstatic --noinput
# Ejecuta el comando pasado
exec "$@"