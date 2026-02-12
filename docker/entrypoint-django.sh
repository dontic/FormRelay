#!/bin/bash

echo "Migrating..."

python manage.py migrate --no-input

echo "Collecting static files..."

python manage.py collectstatic --no-input

# Ensure the data directory exists
mkdir -p data

# Create default superuser if it doesn't already exist
echo "Ensuring superuser exists..."
python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email='', password=password)
    print(f'Superuser \"{username}\" created.')
else:
    print(f'Superuser \"{username}\" already exists, skipping.')
"

echo "Starting server..."

gunicorn core.wsgi:application --forwarded-allow-ips="*" --bind 0.0.0.0:8000

#####################################################################################
# Options to DEBUG Django server
# Optional commands to replace abouve gunicorn command

# Option 1:
# run gunicorn with debug log level
# gunicorn server.wsgi --bind 0.0.0.0:8000 --workers 1 --threads 1 --log-level debug

# Option 2:
# run development server
# DEBUG=True ./manage.py runserver 0.0.0.0:8000