import mimetypes
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from main.models import StoredFile


class Command(BaseCommand):
    help = 'Import files from the bundled /media folder into database storage (only files not already stored).'

    def handle(self, *args, **opts):
        root = Path(settings.MEDIA_ROOT)
        added = 0
        if root.exists():
            for p in sorted(root.rglob('*')):
                if not p.is_file():
                    continue
                name = p.relative_to(root).as_posix()
                if StoredFile.objects.filter(name=name).exists():
                    continue
                data = p.read_bytes()
                StoredFile.objects.create(
                    name=name, content=data, size=len(data),
                    content_type=mimetypes.guess_type(name)[0] or 'application/octet-stream')
                added += 1
        self.stdout.write(self.style.SUCCESS(f'Imported {added} media file(s).'))
