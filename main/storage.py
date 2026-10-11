"""
Database-backed media storage.

Why: the site runs on a host with an ephemeral disk and the old Cloudinary
setup crashed pages whenever it was not configured. Storing uploads in the
database means every image, video and CV survives restarts, redeploys and
refreshes, with no third-party service to misconfigure.
"""
import mimetypes
import os
import re
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


@deconstructible
class DatabaseStorage(Storage):
    def _model(self):
        from .models import StoredFile
        return StoredFile

    @staticmethod
    def _clean(name):
        name = str(name).replace('\\', '/').lstrip('/')
        parts = [p for p in name.split('/') if p not in ('', '.', '..')]
        return '/'.join(parts)

    def _open(self, name, mode='rb'):
        obj = self._model().objects.filter(name=self._clean(name)).first()
        if obj is None:
            raise FileNotFoundError(name)
        return ContentFile(bytes(obj.content), name=name)

    def _save(self, name, content):
        name = self._clean(name)
        content.seek(0)
        data = content.read()
        ctype = (getattr(content, 'content_type', None)
                 or mimetypes.guess_type(name)[0] or 'application/octet-stream')
        self._model().objects.update_or_create(
            name=name,
            defaults={'content': data, 'content_type': ctype, 'size': len(data)},
        )
        return name

    def get_available_name(self, name, max_length=None):
        name = self._clean(name)
        base, ext = os.path.splitext(name)
        base = re.sub(r'[^A-Za-z0-9_/\-.]+', '_', base)
        ext = re.sub(r'[^A-Za-z0-9.]+', '', ext)
        candidate = f'{base}{ext}'
        i = 0
        Model = self._model()
        while Model.objects.filter(name=candidate).exists():
            i += 1
            candidate = f'{base}_{i}{ext}'
        if max_length and len(candidate) > max_length:
            keep = max_length - len(ext) - 8
            candidate = f'{base[:keep]}_{os.urandom(3).hex()}{ext}'
        return candidate

    def exists(self, name):
        return self._model().objects.filter(name=self._clean(name)).exists()

    def delete(self, name):
        self._model().objects.filter(name=self._clean(name)).delete()

    def size(self, name):
        return self._model().objects.values_list('size', flat=True).get(name=self._clean(name))

    def url(self, name):
        from django.conf import settings
        from urllib.parse import quote
        return settings.MEDIA_URL + quote(self._clean(name))

    def listdir(self, path):
        path = self._clean(path)
        prefix = f'{path}/' if path else ''
        names = self._model().objects.filter(name__startswith=prefix).values_list('name', flat=True)
        files, dirs = set(), set()
        for n in names:
            rest = n[len(prefix):]
            if '/' in rest:
                dirs.add(rest.split('/')[0])
            else:
                files.add(rest)
        return sorted(dirs), sorted(files)


# --------------------------------------------------------------------------
# Hybrid storage: Cloudinary when configured (best for permanent, CDN-served
# images & videos), otherwise the database. Files already in the database
# keep working after Cloudinary is switched on, and vice-versa.
# --------------------------------------------------------------------------
CLD_PREFIX = 'cld/'


def cloudinary_configured():
    """True only when all three Cloudinary credentials are present."""
    import os
    if os.environ.get('CLOUDINARY_URL'):
        return True
    return all(os.environ.get(k) for k in ('CLOUDINARY_CLOUD_NAME', 'CLOUDINARY_API_KEY', 'CLOUDINARY_API_SECRET'))


def _cld():
    import cloudinary
    import cloudinary.uploader
    import os
    if not os.environ.get('CLOUDINARY_URL'):
        cloudinary.config(cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
                          api_key=os.environ.get('CLOUDINARY_API_KEY'),
                          api_secret=os.environ.get('CLOUDINARY_API_SECRET'), secure=True)
    return cloudinary


@deconstructible
class HybridStorage(DatabaseStorage):
    """Name format for Cloudinary files:  cld/<resource_type>/v<version>/<public_id>[.<format>]"""

    def _save(self, name, content):
        if not cloudinary_configured():
            return super()._save(name, content)
        cld = _cld()
        name = self._clean(name)
        base, _ext = os.path.splitext(name)
        folder, _, stem = base.rpartition('/')
        content.seek(0)
        res = cld.uploader.upload(
            content, resource_type='auto', folder=folder or None,
            public_id=re.sub(r'[^A-Za-z0-9_\-]+', '_', stem) or 'file', unique_filename=True, overwrite=False)
        rtype, version, public_id = res['resource_type'], res['version'], res['public_id']
        fmt = res.get('format')
        tail = public_id if rtype == 'raw' or not fmt else f'{public_id}.{fmt}'
        return f'{CLD_PREFIX}{rtype}/v{version}/{tail}'

    def get_available_name(self, name, max_length=None):
        if cloudinary_configured():
            return self._clean(name)  # Cloudinary makes the name unique itself
        return super().get_available_name(name, max_length)

    def url(self, name):
        name = self._clean(name)
        if name.startswith(CLD_PREFIX):
            import os as _os
            cloud = _cld().config().cloud_name or ''
            rtype, rest = name[len(CLD_PREFIX):].split('/', 1)
            return f'https://res.cloudinary.com/{cloud}/{rtype}/upload/{rest}'
        return super().url(name)

    def exists(self, name):
        name = self._clean(name)
        return True if name.startswith(CLD_PREFIX) else super().exists(name)

    def delete(self, name):
        name = self._clean(name)
        if name.startswith(CLD_PREFIX):
            try:
                rtype, rest = name[len(CLD_PREFIX):].split('/', 1)
                public_id = rest.split('/', 1)[1]
                if rtype != 'raw':
                    public_id = os.path.splitext(public_id)[0]
                _cld().uploader.destroy(public_id, resource_type=rtype)
            except Exception:
                pass
            return
        super().delete(name)

    def size(self, name):
        name = self._clean(name)
        return 0 if name.startswith(CLD_PREFIX) else super().size(name)

    def _open(self, name, mode='rb'):
        if self._clean(name).startswith(CLD_PREFIX):
            raise FileNotFoundError('Cloudinary files are served from the CDN')
        return super()._open(name, mode)
