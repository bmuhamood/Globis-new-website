import os
import secrets

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = ('Create the admin user if missing. Credentials come from ADMIN_USERNAME / ADMIN_EMAIL / '
            'ADMIN_PASSWORD. An existing user is never modified unless --reset-password is given.')

    def add_arguments(self, parser):
        parser.add_argument('--reset-password', action='store_true')

    def handle(self, *args, **opts):
        User = get_user_model()
        username = os.environ.get('ADMIN_USERNAME') or os.environ.get('DJANGO_ADMIN_USERNAME') or 'admin'
        email = os.environ.get('ADMIN_EMAIL') or os.environ.get('DJANGO_ADMIN_EMAIL') or 'info@globisconsultancy.com'
        password = os.environ.get('ADMIN_PASSWORD') or os.environ.get('DJANGO_ADMIN_PASSWORD') or ''
        user = User.objects.filter(username=username).first()
        if user:
            if opts['reset_password'] and password:
                user.set_password(password)
                user.is_staff = user.is_superuser = True
                user.save()
                self.stdout.write(self.style.SUCCESS('Admin password reset from ADMIN_PASSWORD.'))
            else:
                self.stdout.write(f'Admin "{username}" already exists - left unchanged.')
            return
        generated = not password
        password = password or secrets.token_urlsafe(12)
        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f'Admin "{username}" created.'))
        if generated:
            self.stdout.write(self.style.WARNING(
                f'No ADMIN_PASSWORD set. One-time generated password: {password}  (change it after logging in)'))
