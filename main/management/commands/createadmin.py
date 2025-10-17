from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Create admin user if not exists'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        username = 'admin'
        email = 'bbosa2009@gmail.com'
        password = 'Globis@Admin2024'
        
        try:
            # Check if user exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f'⚠️ Admin user "{username}" already exists'))
                # Update password in case it changed
                user = User.objects.get(username=username)
                user.set_password(password)
                user.is_staff = True
                user.is_superuser = True
                user.save()
                self.stdout.write(self.style.SUCCESS(f'✅ Admin password updated'))
            else:
                # Create new superuser
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                self.stdout.write(self.style.SUCCESS(f'✅ Admin user "{username}" created successfully!'))
                self.stdout.write(self.style.SUCCESS(f'   Username: {username}'))
                self.stdout.write(self.style.SUCCESS(f'   Email: {email}'))
                
        except IntegrityError as e:
            self.stdout.write(self.style.ERROR(f'❌ Error creating admin: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Unexpected error: {e}'))