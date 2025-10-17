#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input --clear
python manage.py migrate

# Force create admin
echo "Creating admin user..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.filter(username='admin').delete()
User.objects.create_superuser('admin', 'bbosa2009@gmail.com', 'Globis@Admin2024')
print('✅ Admin created!')
EOF