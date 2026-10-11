#!/usr/bin/env bash
# Build step: only installs and collects static files.
# Database work (migrate, seed, admin) runs in start.sh when the app starts,
# because Render builds often cannot reach the database's internal address.
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Build completed."