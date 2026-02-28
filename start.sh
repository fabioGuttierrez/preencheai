#!/usr/bin/env bash
set -e

python manage.py migrate
exec gunicorn saas_contratos.wsgi:application --bind 0.0.0.0:8000 --access-logfile - --error-logfile -
