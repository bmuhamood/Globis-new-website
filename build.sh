#!/usr/bin/env bash
# Build step: install, collect static files, then try the database setup.
# If the database cannot be reached from the build environment the DB steps are
# skipped with a warning (start.sh repeats them when the app starts).
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Database setup (best effort)..."
if python manage.py migrate --no-input; then
  python manage.py import_media || echo "WARNING: import_media failed"
  python manage.py load_initial_data || echo "WARNING: load_initial_data failed"
  python manage.py createadmin || echo "WARNING: createadmin failed"
else
  echo "=========================================================="
  echo "WARNING: database not reachable during build - skipped."
  echo "Set DATABASE_URL to the EXTERNAL database URL, or set the"
  echo "Start Command to: bash start.sh"
  echo "=========================================================="
fi

echo "Build completed."