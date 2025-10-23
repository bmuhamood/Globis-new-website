#!/usr/bin/env bash
set -o errexit

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🗂️ Collecting static files..."
python manage.py collectstatic --no-input  # Remove --clear

echo "🔄 Running migrations..."
python manage.py migrate

echo "👤 Checking admin user..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'bbosa2009@gmail.com', 'Globis@Admin2024')
    print('✅ Admin user created successfully!')
else:
    print('ℹ️ Admin user already exists, skipping creation.')
EOF

echo "✅ Build completed successfully!"