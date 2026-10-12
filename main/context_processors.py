from django.conf import settings

from .models import Office


def site(request):
    try:
        branches = list(Office.objects.filter(is_associate=False))
    except Exception:
        branches = []
    return {
        'COMPANY_PHONE': settings.COMPANY_PHONE,
        'COMPANY_WHATSAPP': settings.COMPANY_WHATSAPP,
        'COMPANY_EMAIL': settings.COMPANY_EMAIL,
        'WA_DEFAULT_TEXT': 'Hello GLOBIS HR Consultancy, I would like to make an inquiry about jobs / your services.',
        'branches': branches,
    }
