from django import template
from django.contrib.staticfiles.storage import staticfiles_storage

register = template.Library()


@register.filter
def safe_url(fieldfile):
    """Return a file's URL, or '' if there is no file / storage problem. Never raises."""
    try:
        return fieldfile.url if fieldfile else ''
    except Exception:
        return ''


@register.filter
def fa(icon):
    """Normalise an icon name saved in the DB into a Font Awesome class string."""
    icon = (icon or 'fa-star').strip()
    if icon.startswith(('fas ', 'far ', 'fab ', 'fa-solid')):
        return icon
    if not icon.startswith('fa-'):
        icon = 'fa-' + icon
    return f'fas {icon}'


@register.filter
def initials(name):
    parts = [p for p in str(name).replace('_', ' ').split() if p]
    return ''.join(p[0] for p in parts[:2]).upper() or '•'


@register.simple_tag
def job_art(job):
    """URL of a job's image: its uploaded picture, or the matching bundled illustration."""
    try:
        if job.image:
            return job.image.url
    except Exception:
        pass
    return staticfiles_storage.url(f'img/jobs/{job.category}.svg')


@register.filter
def split_lines(text):
    return [l.strip() for l in str(text).splitlines() if l.strip()]
