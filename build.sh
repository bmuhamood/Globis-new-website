#!/usr/bin/env bash
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

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
    print('This is a Render configuration problem, not a code problem. Check:')
    print('  1. The Postgres database still exists (free databases expire after ~30 days).')
    print('  2. The database and this web service are in the SAME region.')
    print('  3. DATABASE_URL points to a live database (copy it again from the DB page).')
    print('=' * 70)
    raise SystemExit(1)
"

echo "Running migrations..."
python manage.py migrate --no-input

echo "Importing bundled media into storage (only files not already stored)..."
python manage.py import_media

echo "Seeding default content (never overwrites your edits)..."
python manage.py load_initial_data

echo "Ensuring admin user exists (set ADMIN_USERNAME / ADMIN_PASSWORD in Render)..."
python manage.py createadmin

echo "Build completed."
