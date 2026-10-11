#!/usr/bin/env bash
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running migrations..."
python manage.py migrate --no-input

echo "Importing bundled media into database storage (only files not already stored)..."
python manage.py import_media

echo "Seeding default content (never overwrites your edits)..."
python manage.py load_initial_data

echo "Ensuring admin user exists (set ADMIN_USERNAME / ADMIN_PASSWORD in Render)..."
python manage.py createadmin

echo "Build completed."
