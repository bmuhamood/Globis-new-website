import logging
import re
import threading
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseNotModified, JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET
from django.views.decorators.cache import never_cache

from . import content
from .countries import COUNTRIES
from .forms import ApplicationForm, ContactForm, make_form_token
from .models import (Client, ContactInquiry, CoreValue, GalleryImage, Job, JobApplication, Office,
                     RecruitmentField, Service, StoredFile, Testimonial)

log = logging.getLogger(__name__)


def client_ip(request):
    fwd = request.META.get('HTTP_X_FORWARDED_FOR', '')
    return (fwd.split(',')[0].strip() if fwd else request.META.get('REMOTE_ADDR', '')) or ''


def open_jobs():
    today = timezone.localdate()
    return Job.objects.filter(is_active=True).filter(Q(closing_date__isnull=True) | Q(closing_date__gte=today))


# ---------------------------------------------------------------- content ---
def _services():
    items = list(Service.objects.all())
    if items:
        return [{'title': s.title, 'description': s.description, 'icon': s.icon,
                 'points': content.SERVICE_POINTS.get(s.title, [])} for s in items]
    return [{'title': t, 'description': d, 'icon': i, 'points': content.SERVICE_POINTS.get(t, [])}
            for t, d, i in content.SERVICES]


def _fields():
    items = list(RecruitmentField.objects.all())
    pts = {t: p for t, _d, _i, p in content.RECRUITMENT_FIELDS}
    if items:
        return [{'title': f.title, 'description': f.description, 'icon': f.icon, 'points': pts.get(f.title, [])}
                for f in items]
    return [{'title': t, 'description': d, 'icon': i, 'points': p} for t, d, i, p in content.RECRUITMENT_FIELDS]


def _offices():
    items = list(Office.objects.all())
    if items:
        return items
    return [Office(country=c, company_name=n, address=a, is_main=m) for c, n, a, m in content.OFFICES]


def _values():
    items = list(CoreValue.objects.all())
    return items or [CoreValue(number=i, title=t) for i, t in enumerate(content.CORE_VALUES, 1)]


def home(request):
    return render(request, 'main/home.html', {
        'services': _services()[:6],
        'fields': _fields(),
        'clients': Client.objects.exclude(logo='').exclude(logo__isnull=True)[:30],
        'featured_jobs': open_jobs()[:6],
        'job_count': open_jobs().count(),
        'offices': _offices(),
    })


def about(request):
    return render(request, 'main/about.html', {'core_values': _values(), 'offices': _offices()})


def services(request):
    return render(request, 'main/services.html', {'services': _services()})


def recruitment(request):
    return render(request, 'main/recruitment.html', {'fields': _fields(), 'job_count': open_jobs().count()})


def process(request):
    return render(request, 'main/process.html')


def clients(request):
    return render(request, 'main/clients.html', {
        'clients': Client.objects.all(),
        'testimonials': Testimonial.objects.all(),
    })


def gallery(request):
    items = GalleryImage.objects.all()
    cat = request.GET.get('category')
    if cat in dict(GalleryImage.CATEGORY_CHOICES):
        items = items.filter(category=cat)
    return render(request, 'main/gallery.html', {
        'items': items, 'categories': GalleryImage.CATEGORY_CHOICES, 'active_category': cat or ''})


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            _notify('New website enquiry',
                    f"{form.cleaned_data['name']} <{form.cleaned_data['email']}>\n"
                    f"{form.cleaned_data['phone']}\n\n{form.cleaned_data['message']}")
            messages.success(request, 'Thank you! Your message has reached our team and we will reply shortly.')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'main/contact.html', {'form': form, 'offices': _offices()})


# ------------------------------------------------------------------- jobs ---
def jobs(request):
    qs = open_jobs()
    cat = request.GET.get('category', '')
    q = request.GET.get('q', '').strip()
    if cat in dict(Job.CATEGORIES):
        qs = qs.filter(category=cat)
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(city__icontains=q) | Q(summary__icontains=q))
    used = set(open_jobs().values_list('category', flat=True))
    return render(request, 'main/jobs.html', {
        'jobs': qs, 'q': q, 'active_category': cat,
        'categories': [(k, v) for k, v in Job.CATEGORIES if k in used],
        'total': open_jobs().count(),
    })


def job_detail(request, slug):
    job = get_object_or_404(Job, slug=slug)
    if not job.is_open and not (request.user.is_authenticated and request.user.is_staff):
        return render(request, 'main/job_closed.html', {'job': job,
                      'similar': open_jobs()[:3]}, status=410)
    similar = open_jobs().filter(category=job.category).exclude(pk=job.pk)[:3]
    return render(request, 'main/job_detail.html', {'job': job, 'similar': similar})


def _notify(subject, body):
    """Fire-and-forget email; never blocks or breaks the request."""
    def run():
        try:
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [settings.NOTIFY_EMAIL], fail_silently=True)
        except Exception:  # pragma: no cover
            log.exception('notification email failed')
    threading.Thread(target=run, daemon=True).start()


@never_cache
def apply(request, slug=None):
    """Public application form. No login, protected by honeypot + signed timer + rate limit."""
    preselect = None
    wanted = slug or request.GET.get('job')
    if wanted:
        preselect = Job.objects.filter(slug=wanted, is_active=True).first()

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        ip = client_ip(request)
        ip_hash = JobApplication.hash_ip(ip)
        recent = JobApplication.objects.filter(ip_hash=ip_hash, created_at__gte=timezone.now() - timedelta(hours=1)).count() if ip_hash else 0
        if recent >= 8:
            form.add_error(None, 'We received several applications from your connection. Please try again later, '
                                 'or message us on WhatsApp.')
        elif form.is_valid():
            d = form.cleaned_data
            dup = JobApplication.objects.filter(
                phone=d['phone'], job=d.get('job'),
                created_at__gte=timezone.now() - timedelta(hours=24)).first()
            app = dup or form.save(ip=ip)
            if not dup:
                _notify(f'New job application {app.reference}: {app.display_job}',
                        f'{app.full_name}\n{app.phone} (WhatsApp: {"yes" if app.phone_is_whatsapp else "no"})\n'
                        f'{app.nationality}\nJob: {app.display_job}\nOpen the portal: /portal/applications/{app.pk}/')
            request.session['last_application'] = app.pk
            return redirect('apply_done')
    else:
        initial = {'job': preselect.pk} if preselect else {}
        form = ApplicationForm(initial=initial)
    token = make_form_token()  # fresh signed timer on every render (also after a failed POST)
    return render(request, 'main/apply.html', {
        'form': form, 'preselect': preselect, 'form_token': token,
        'dial_map': {c['iso']: c['dial'] for c in COUNTRIES},
    })


def apply_done(request):
    pk = request.session.get('last_application')
    app = JobApplication.objects.filter(pk=pk).first() if pk else None
    if not app:
        return redirect('apply')
    return render(request, 'main/apply_done.html', {'app': app, 'more_jobs': open_jobs().exclude(pk=app.job_id)[:3]})


# --------------------------------------------------------- infrastructure ---
@require_GET
def healthz(request):
    return JsonResponse({'status': 'ok'})


@require_GET
def robots(request):
    body = ('User-agent: *\nDisallow: /portal/\nDisallow: /admin/\nAllow: /\n'
            f'Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml\n')
    return HttpResponse(body, content_type='text/plain')


@require_GET
def sitemap(request):
    base = f'{request.scheme}://{request.get_host()}'
    urls = ['/', '/about/', '/services/', '/recruitment/', '/jobs/', '/apply/', '/process/', '/clients/',
            '/gallery/', '/contact/'] + [j.get_absolute_url() for j in open_jobs()]
    xml = ('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
           + ''.join(f'<url><loc>{base}{u}</loc></url>' for u in urls) + '</urlset>')
    return HttpResponse(xml, content_type='application/xml')


_RANGE = re.compile(r'bytes=(\d*)-(\d*)')


@require_GET
def media_file(request, path):
    """Serve files stored in the database, with caching and HTTP Range support (needed for video)."""
    path = path.strip('/')
    # CVs contain personal data: staff only.
    if path.startswith('cv/') and not (request.user.is_authenticated and request.user.is_staff):
        raise Http404
    obj = StoredFile.objects.filter(name=path).only('name', 'content_type', 'size', 'updated_at').first()
    if obj is None:
        raise Http404
    etag = f'"{obj.pk}-{obj.size}-{int(obj.updated_at.timestamp())}"'
    if request.META.get('HTTP_IF_NONE_MATCH') == etag:
        resp = HttpResponseNotModified()
        resp['ETag'] = etag
        return resp
    data = bytes(StoredFile.objects.values_list('content', flat=True).get(pk=obj.pk))
    total = len(data)
    status, start, end = 200, 0, total - 1
    m = _RANGE.match(request.META.get('HTTP_RANGE', ''))
    if m and (m.group(1) or m.group(2)):
        if m.group(1):
            start = int(m.group(1))
            end = int(m.group(2)) if m.group(2) else total - 1
        else:
            start = max(total - int(m.group(2)), 0)
        end = min(end, total - 1)
        if start > end:
            resp = HttpResponse(status=416)
            resp['Content-Range'] = f'bytes */{total}'
            return resp
        status = 206
    chunk = data[start:end + 1]
    resp = HttpResponse(chunk, status=status, content_type=obj.content_type)
    resp['Accept-Ranges'] = 'bytes'
    resp['ETag'] = etag
    private = path.startswith('cv/')
    resp['Cache-Control'] = 'private, no-store' if private else 'public, max-age=86400'
    if private:
        resp['Content-Disposition'] = f'inline; filename="{path.rsplit("/", 1)[-1]}"'
    if status == 206:
        resp['Content-Range'] = f'bytes {start}-{end}/{total}'
    return resp


def error_404(request, exception=None):
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    return render(request, 'errors/500.html', status=500)
