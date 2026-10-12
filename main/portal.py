"""Staff portal: monitor applications, manage jobs, read enquiries. Login required (staff only)."""
import csv
from datetime import timedelta
from functools import wraps

from django import forms
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from .models import ContactInquiry, Job, JobApplication


def staff_required(view):
    @wraps(view)
    @never_cache
    def wrapper(request, *args, **kwargs):
        u = request.user
        if not (u.is_authenticated and u.is_staff):
            return redirect(f'/portal/login/?next={request.path}')
        return view(request, *args, **kwargs)
    return wrapper


# --------------------------------------------------------------- login ------
class PortalAuthForm(AuthenticationForm):
    error_messages = {
        'invalid_login': 'Wrong username or password.',
        'inactive': 'This account is disabled.',
    }

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise forms.ValidationError('This account does not have portal access.', code='no_access')


class PortalLoginView(LoginView):
    template_name = 'portal/login.html'
    authentication_form = PortalAuthForm
    redirect_authenticated_user = True
    MAX_FAILS, WINDOW = 6, 15 * 60

    @staticmethod
    def _key(request):
        fwd = request.META.get('HTTP_X_FORWARDED_FOR', '')
        ip = (fwd.split(',')[0].strip() if fwd else request.META.get('REMOTE_ADDR', ''))
        return f'portal-fail:{ip}'

    def post(self, request, *args, **kwargs):
        if cache.get(self._key(request), 0) >= self.MAX_FAILS:
            form = self.get_form()
            form.add_error(None, 'Too many failed attempts. Please wait 15 minutes and try again.')
            return self.render_to_response(self.get_context_data(form=form), status=429)
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        key = self._key(self.request)
        cache.set(key, cache.get(key, 0) + 1, self.WINDOW)
        return super().form_invalid(form)

    def form_valid(self, form):
        cache.delete(self._key(self.request))
        return super().form_valid(form)


def portal_logout(request):
    logout(request)
    return redirect('portal_login')


# ------------------------------------------------------------ dashboard -----
@staff_required
def dashboard(request):
    now = timezone.now()
    today = timezone.localdate()
    apps = JobApplication.objects.all()
    total = apps.count()
    by_status = {k: 0 for k, _ in JobApplication.STATUS}
    for row in apps.values('status').annotate(n=Count('id')):
        by_status[row['status']] = row['n']

    days = [today - timedelta(days=i) for i in range(13, -1, -1)]
    series_raw = {r['d']: r['n'] for r in
                  apps.filter(created_at__gte=now - timedelta(days=15))
                  .annotate(d=TruncDate('created_at')).values('d').annotate(n=Count('id'))}
    series = [{'day': d, 'n': series_raw.get(d, 0)} for d in days]
    peak = max([s['n'] for s in series] + [1])
    for s in series:
        s['pct'] = round(s['n'] / peak * 100)

    top_jobs = (apps.values('job_title').annotate(n=Count('id')).order_by('-n')[:6])
    top_nat = (apps.values('nationality').annotate(n=Count('id')).order_by('-n')[:6])
    top_jobs_max = max([r['n'] for r in top_jobs] + [1])
    top_nat_max = max([r['n'] for r in top_nat] + [1])

    ctx = {
        'total': total,
        'new': by_status['new'],
        'today': apps.filter(created_at__date=today).count(),
        'week': apps.filter(created_at__gte=now - timedelta(days=7)).count(),
        'by_status': [(k, label, by_status[k]) for k, label in JobApplication.STATUS],
        'series': series, 'peak': peak,
        'top_jobs': [{**r, 'pct': round(r['n'] / top_jobs_max * 100)} for r in top_jobs],
        'top_nat': [{**r, 'pct': round(r['n'] / top_nat_max * 100)} for r in top_nat],
        'recent': apps.select_related('job')[:8],
        'active_jobs': Job.objects.filter(is_active=True).count(),
        'unread': ContactInquiry.objects.filter(is_read=False).count(),
        'nav': 'dashboard',
    }
    return render(request, 'portal/dashboard.html', ctx)


# --------------------------------------------------------- applications -----
def _filtered(request):
    qs = JobApplication.objects.select_related('job')
    g = request.GET
    if g.get('status') in dict(JobApplication.STATUS):
        qs = qs.filter(status=g['status'])
    if g.get('job', '').isdigit():
        qs = qs.filter(job_id=int(g['job']))
    elif g.get('job') == 'general':
        qs = qs.filter(job__isnull=True)
    if g.get('nationality'):
        qs = qs.filter(nationality=g['nationality'])
    if g.get('q'):
        q = g['q'].strip()
        digits = ''.join(ch for ch in q if ch.isdigit())
        cond = Q(full_name__icontains=q) | Q(email__icontains=q) | Q(reference__icontains=q) | Q(job_title__icontains=q)
        if digits:
            cond |= Q(phone__contains=digits)
        qs = qs.filter(cond)
    if g.get('cv') == '1':
        qs = qs.exclude(cv='').exclude(cv__isnull=True)
    return qs


@staff_required
def applications(request):
    qs = _filtered(request)
    page = Paginator(qs, 25).get_page(request.GET.get('page'))
    params = request.GET.copy()
    params.pop('page', None)
    return render(request, 'portal/applications.html', {
        'page': page, 'count': qs.count(),
        'statuses': JobApplication.STATUS,
        'jobs': Job.objects.order_by('title'),
        'nationalities': JobApplication.objects.order_by().values_list('nationality', flat=True).distinct().order_by('nationality'),
        'qs': params.urlencode(), 'f': request.GET, 'nav': 'applications',
    })


@staff_required
def applications_csv(request):
    resp = HttpResponse(content_type='text/csv; charset=utf-8')
    resp['Content-Disposition'] = f'attachment; filename="globis-applications-{timezone.localdate()}.csv"'
    resp.write('﻿')
    w = csv.writer(resp)
    w.writerow(['Reference', 'Date', 'Status', 'Name', 'Phone', 'WhatsApp', 'Email', 'Nationality', 'Lives in',
                'Job', 'Experience', 'Passport', 'Has CV', 'Notes'])
    for a in _filtered(request):
        w.writerow([a.reference, timezone.localtime(a.created_at).strftime('%Y-%m-%d %H:%M'), a.get_status_display(),
                    a.full_name, a.phone, 'yes' if a.phone_is_whatsapp else 'no', a.email, a.nationality, a.residence,
                    a.display_job, a.get_experience_display(), a.get_passport_display(), 'yes' if a.cv else 'no',
                    a.admin_notes.replace('\n', ' ')])
    return resp


class ApplicationUpdateForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['status', 'admin_notes']
        widgets = {'admin_notes': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Call notes, interview date, documents received…'})}


@staff_required
def application_detail(request, pk):
    app = get_object_or_404(JobApplication.objects.select_related('job'), pk=pk)
    if request.method == 'POST':
        if request.POST.get('action') == 'delete':
            app.delete()
            messages.success(request, 'Application deleted.')
            return redirect('portal_applications')
        form = ApplicationUpdateForm(request.POST, instance=app)
        if form.is_valid():
            obj = form.save(commit=False)
            if obj.status != 'new' and not obj.contacted_at:
                obj.contacted_at = timezone.now()
            obj.save()
            messages.success(request, 'Saved.')
            return redirect('portal_application', pk=pk)
    else:
        form = ApplicationUpdateForm(instance=app)
    neighbours = {
        'newer': JobApplication.objects.filter(created_at__gt=app.created_at).order_by('created_at').first(),
        'older': JobApplication.objects.filter(created_at__lt=app.created_at).first(),
    }
    return render(request, 'portal/application.html', {'app': app, 'form': form, 'nav': 'applications', **neighbours})


# ----------------------------------------------------------------- jobs -----
class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'category', 'country', 'city', 'employment_type', 'salary', 'working_hours', 'contract_length', 'vacancies', 'summary',
                  'description', 'requirements', 'benefits', 'image', 'closing_date', 'is_active', 'is_featured']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'requirements': forms.Textarea(attrs={'rows': 5, 'placeholder': 'One per line'}),
            'benefits': forms.Textarea(attrs={'rows': 4, 'placeholder': 'One per line'}),
            'closing_date': forms.DateInput(attrs={'type': 'date'}),
            'country': forms.TextInput(attrs={'list': 'countries', 'placeholder': 'United Arab Emirates, Saudi Arabia, Oman, Europe…'}),
            'city': forms.TextInput(attrs={'list': 'cities', 'placeholder': 'Dubai, Abu Dhabi, Sharjah…'}),
            'image': forms.FileInput(attrs={'accept': 'image/*'}),
        }


@staff_required
def jobs_list(request):
    jobs = Job.objects.annotate(n_apps=Count('applications')).order_by('-is_active', '-created_at')
    return render(request, 'portal/jobs.html', {'jobs': jobs, 'nav': 'jobs'})


@staff_required
def job_edit(request, pk=None):
    job = get_object_or_404(Job, pk=pk) if pk else None
    form = JobForm(request.POST or None, request.FILES or None, instance=job)
    if request.method == 'POST' and form.is_valid():
        saved = form.save()
        messages.success(request, f'"{saved.title}" saved and live on the website.' if saved.is_active else f'"{saved.title}" saved (hidden).')
        return redirect('portal_jobs')
    return render(request, 'portal/job_form.html', {'form': form, 'job': job, 'nav': 'jobs'})


@staff_required
@require_POST
def job_toggle(request, pk):
    job = get_object_or_404(Job, pk=pk)
    job.is_active = not job.is_active
    job.save(update_fields=['is_active', 'updated_at'])
    messages.success(request, f'"{job.title}" is now {"live" if job.is_active else "hidden"}.')
    return redirect('portal_jobs')


@staff_required
@require_POST
def job_delete(request, pk):
    job = get_object_or_404(Job, pk=pk)
    title = job.title
    job.delete()
    messages.success(request, f'"{title}" deleted. Existing applications were kept.')
    return redirect('portal_jobs')


# ------------------------------------------------------------ enquiries -----
@staff_required
def inquiries(request):
    if request.method == 'POST':
        pk = request.POST.get('id')
        ContactInquiry.objects.filter(pk=pk).update(is_read=request.POST.get('read') == '1')
        return redirect('portal_inquiries')
    page = Paginator(ContactInquiry.objects.all(), 20).get_page(request.GET.get('page'))
    return render(request, 'portal/inquiries.html', {'page': page, 'nav': 'inquiries'})


# ======================================================================
# Generic content management: clients, gallery, branches, testimonials
# ======================================================================
from django.conf import settings as dj_settings
from django.contrib.auth import get_user_model
from django.http import Http404

from .models import Client, GalleryImage, Office, Testimonial

VIDEO_EXT = ('.mp4', '.webm', '.mov', '.m4v')


def _check_size(f, label='File'):
    if f and f.size > dj_settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise forms.ValidationError(f'{label} is larger than {dj_settings.MAX_UPLOAD_MB} MB.')


class _Base(forms.ModelForm):
    def clean(self):
        data = super().clean()
        for name, f in self.files.items():
            _check_size(f, name)
        return data


class ClientForm(_Base):
    class Meta:
        model = Client
        fields = ['name', 'logo', 'order']
        widgets = {'logo': forms.FileInput(attrs={'accept': 'image/*'})}


class GalleryForm(_Base):
    class Meta:
        model = GalleryImage
        fields = ['title', 'category', 'image', 'video', 'description', 'order']
        widgets = {'image': forms.FileInput(attrs={'accept': 'image/*'}),
                   'video': forms.FileInput(attrs={'accept': 'video/mp4,video/webm,video/quicktime'}),
                   'description': forms.Textarea(attrs={'rows': 3})}

    def clean_video(self):
        v = self.cleaned_data.get('video')
        if v and hasattr(v, 'name') and not v.name.lower().endswith(VIDEO_EXT):
            raise forms.ValidationError('Please upload an MP4, WebM or MOV video.')
        return v

    def clean(self):
        data = super().clean()
        has_img = data.get('image') or (self.instance.pk and self.instance.image)
        has_vid = data.get('video') or (self.instance.pk and self.instance.video)
        if not (has_img or has_vid):
            raise forms.ValidationError('Add a photo or a video.')
        return data


class TestimonialForm(_Base):
    class Meta:
        model = Testimonial
        fields = ['client_name', 'company', 'location', 'message', 'logo', 'order']
        widgets = {'logo': forms.FileInput(attrs={'accept': 'image/*'}), 'message': forms.Textarea(attrs={'rows': 4})}


class BranchForm(_Base):
    class Meta:
        model = Office
        fields = ['country', 'company_name', 'address', 'phone', 'is_main', 'is_associate',
                  'tiktok_url', 'facebook_url', 'instagram_url', 'youtube_url', 'order']
        widgets = {'address': forms.Textarea(attrs={'rows': 2}),
                   'tiktok_url': forms.URLInput(attrs={'placeholder': 'https://www.tiktok.com/@…'}),
                   'facebook_url': forms.URLInput(attrs={'placeholder': 'https://www.facebook.com/…'}),
                   'instagram_url': forms.URLInput(attrs={'placeholder': 'https://www.instagram.com/…'}),
                   'youtube_url': forms.URLInput(attrs={'placeholder': 'https://www.youtube.com/@…'})}


CRUD = {
    'clients': dict(model=Client, form=ClientForm, title='Clients', one='client', icon='fa-building', thumb='logo',
                    sub=lambda o: f'Order {o.order}', add='Add client',
                    help='Logos appear on the Home and Clients pages.'),
    'gallery': dict(model=GalleryImage, form=GalleryForm, title='Gallery', one='gallery item', icon='fa-photo-film', thumb='image',
                    sub=lambda o: f'{o.get_category_display()}{" · video" if o.video else ""}', add='Add photo / video',
                    help='Photos and videos shown on the Gallery page.'),
    'branches': dict(model=Office, form=BranchForm, title='Branches & social links', one='branch', icon='fa-location-dot', thumb=None,
                     sub=lambda o: f'{o.address[:60]}', add='Add branch',
                     help='Offices, plus TikTok / Facebook / Instagram links shown on the site (not for associate offices).'),
    'testimonials': dict(model=Testimonial, form=TestimonialForm, title='Testimonials', one='testimonial', icon='fa-quote-left', thumb='logo',
                         sub=lambda o: o.company or '', add='Add testimonial', help='Shown on the Clients page.'),
}


def _cfg(kind):
    if kind not in CRUD:
        raise Http404
    return CRUD[kind]


def _label(o):
    return getattr(o, 'title', None) or getattr(o, 'name', None) or getattr(o, 'client_name', None) or str(o)


@staff_required
def crud_list(request, kind):
    cfg = _cfg(kind)
    rows = []
    for o in cfg['model'].objects.all():
        thumb = ''
        if cfg['thumb']:
            try:
                f = getattr(o, cfg['thumb'])
                thumb = f.url if f else ''
            except Exception:
                thumb = ''
        rows.append({'obj': o, 'label': _label(o), 'sub': cfg['sub'](o), 'thumb': thumb,
                     'social': kind == 'branches' and o.has_social})
    return render(request, 'portal/crud_list.html', {'cfg': cfg, 'kind': kind, 'rows': rows, 'nav': kind})


@staff_required
def crud_edit(request, kind, pk=None):
    cfg = _cfg(kind)
    obj = get_object_or_404(cfg['model'], pk=pk) if pk else None
    form = cfg['form'](request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'{cfg["one"].capitalize()} saved.')
        return redirect('portal_crud', kind=kind)
    return render(request, 'portal/crud_form.html', {'cfg': cfg, 'kind': kind, 'form': form, 'obj': obj, 'nav': kind})


@staff_required
@require_POST
def crud_delete(request, kind, pk):
    cfg = _cfg(kind)
    obj = get_object_or_404(cfg['model'], pk=pk)
    obj.delete()
    messages.success(request, f'{cfg["one"].capitalize()} deleted.')
    return redirect('portal_crud', kind=kind)


# ======================================================================
# Team (portal users) - superusers only
# ======================================================================
def superuser_required(view):
    @wraps(view)
    @staff_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, 'Only the main administrator can manage team accounts.')
            return redirect('portal')
        return view(request, *args, **kwargs)
    return wrapper


class TeamUserForm(forms.Form):
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=60, required=False, label='Full name')
    email = forms.EmailField(required=False)
    password = forms.CharField(min_length=8, widget=forms.PasswordInput, help_text='At least 8 characters.')
    is_superuser = forms.BooleanField(required=False, label='Main administrator (can manage team accounts)')

    def clean_username(self):
        u = self.cleaned_data['username'].strip()
        if get_user_model().objects.filter(username__iexact=u).exists():
            raise forms.ValidationError('That username is taken.')
        return u


@superuser_required
def team(request):
    User = get_user_model()
    form = TeamUserForm(request.POST or None)
    if request.method == 'POST' and request.POST.get('action') in ('toggle', 'password'):
        u = get_object_or_404(User, pk=request.POST.get('id'))
        if request.POST['action'] == 'toggle' and u != request.user:
            u.is_active = not u.is_active
            u.save(update_fields=['is_active'])
            messages.success(request, f'{u.username} is now {"active" if u.is_active else "disabled"}.')
        elif request.POST['action'] == 'password':
            pw = request.POST.get('new_password', '')
            if len(pw) >= 8:
                u.set_password(pw)
                u.save()
                messages.success(request, f'Password changed for {u.username}.')
            else:
                messages.error(request, 'Password must be at least 8 characters.')
        return redirect('portal_team')
    if request.method == 'POST' and form.is_valid():
        d = form.cleaned_data
        u = User.objects.create_user(d['username'], d['email'], d['password'], first_name=d['first_name'])
        u.is_staff = True
        u.is_superuser = d['is_superuser']
        u.save()
        messages.success(request, f'Account "{u.username}" created. Share the sign-in details securely.')
        return redirect('portal_team')
    return render(request, 'portal/team.html', {'users': User.objects.filter(is_staff=True).order_by('username'),
                                                'form': form, 'nav': 'team'})
