import os
import secrets

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = ('Create the admin user if missing. Credentials come from ADMIN_USERNAME / ADMIN_EMAIL / '
            'ADMIN_PASSWORD. If a password is set in the environment it is applied on every start, so the '
            'environment variable is always the source of truth (use --keep-existing to skip that).')

    def add_arguments(self, parser):
        parser.add_argument('--keep-existing', action='store_true')

    def handle(self, *args, **opts):
        User = get_user_model()
        username = os.environ.get('ADMIN_USERNAME') or os.environ.get('DJANGO_ADMIN_USERNAME') or 'admin'
        email = os.environ.get('ADMIN_EMAIL') or os.environ.get('DJANGO_ADMIN_EMAIL') or 'info@globisconsultancy.com'
        password = os.environ.get('ADMIN_PASSWORD') or os.environ.get('DJANGO_ADMIN_PASSWORD') or ''
        user = User.objects.filter(username=username).first()
        if user:
            if password and not opts['keep_existing']:
                user.set_password(password)
                user.is_staff = user.is_superuser = True
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Admin "{username}" password synced from the environment variable.'))
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