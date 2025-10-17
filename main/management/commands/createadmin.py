from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Create admin user if not exists'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        username = 'admin'
        email = 'bbosa2009@gmail.com'
        password = 'Globis@Admin2024'
        
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f'✅ Admin user "{username}" created successfully!'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠️ Admin user "{username}" already exists'))