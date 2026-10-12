#!/usr/bin/env bash
# Start step: prepare the database, then run the web server.
set -o errexit

echo "Checking database connection..."
python manage.py shell -c "
from django.db import connection
try:
    connection.ensure_connection()
    print('Database connection OK')
except Exception as e:
    print()
    print('=' * 70)
    print('DATABASE NOT REACHABLE:', str(e).strip().splitlines()[-1])
    print('Check DATABASE_URL in Render > Environment, and that the database and')
    print('this web service are in the SAME region (otherwise use the External URL).')
    print('=' * 70)
    raise SystemExit(1)
"

echo "Running migrations..."
python manage.py migrate --no-input

echo "Importing bundled media (only files not already stored)..."
python manage.py import_media

echo "Seeding default content (never overwrites your edits)..."
python manage.py load_initial_data

echo "Ensuring admin user exists..."
python manage.py createadmin

echo "Starting web server..."
exec gunicorn globis_project.wsgi:application --bind 0.0.0.0:${PORT:-10000} --workers 2 --threads 4 --timeout 60 --access-logfile -
