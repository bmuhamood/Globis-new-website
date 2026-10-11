import os
import re
import time

from django import forms
from django.conf import settings
from django.core import signing
from django.utils import timezone

from .countries import COUNTRIES, BY_ISO, NATIONALITY_CHOICES, RESIDENCE_CHOICES
from .models import ContactInquiry, Job, JobApplication

FORM_SALT = 'globis.apply.form'
MIN_FILL_SECONDS = 2.5
MAX_FORM_AGE = 60 * 60 * 6


def make_form_token():
    return signing.dumps({'t': time.time()}, salt=FORM_SALT)


def check_form_token(token):
    """Return None if fine, or a short reason string if the token looks automated."""
    try:
        data = signing.loads(token or '', salt=FORM_SALT, max_age=MAX_FORM_AGE)
    except signing.SignatureExpired:
        return 'expired'
    except signing.BadSignature:
        return 'bad'
    if time.time() - data.get('t', 0) < MIN_FILL_SECONDS:
        return 'too_fast'
    return None


class ContactForm(forms.ModelForm):
    website = forms.CharField(required=False)  # honeypot

    class Meta:
        model = ContactInquiry
        fields = ['name', 'email', 'phone', 'company', 'inquiry_type', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your full name', 'autocomplete': 'name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'you@company.com', 'autocomplete': 'email'}),
            'phone': forms.TextInput(attrs={'placeholder': '+971 5X XXX XXXX', 'autocomplete': 'tel', 'inputmode': 'tel'}),
            'company': forms.TextInput(attrs={'placeholder': 'Company (optional)', 'autocomplete': 'organization'}),
            'message': forms.Textarea(attrs={'placeholder': 'How can we help?', 'rows': 5}),
        }

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError('Spam detected.')
        return ''


ALLOWED_CV_EXT = {'.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png'}
MAGIC = {
    '.pdf': [b'%PDF'],
    '.doc': [b'\xd0\xcf\x11\xe0'],
    '.docx': [b'PK\x03\x04'],
    '.jpg': [b'\xff\xd8\xff'],
    '.jpeg': [b'\xff\xd8\xff'],
    '.png': [b'\x89PNG'],
}


class ApplicationForm(forms.Form):
    job = forms.ModelChoiceField(
        queryset=Job.objects.none(), required=False, empty_label='Any suitable job (general application)',
        label='Job you are applying for')
    full_name = forms.CharField(max_length=150, label='Full name (as on passport)',
                                widget=forms.TextInput(attrs={'autocomplete': 'name', 'placeholder': 'e.g. Aisha Nakato'}))
    phone_country = forms.ChoiceField(
        choices=[(c['iso'], f"{c['name']} (+{c['dial']})") for c in COUNTRIES],
        initial='UG', label='Country code')
    phone_number = forms.CharField(max_length=20, label='Phone number',
                                   widget=forms.TextInput(attrs={'inputmode': 'tel', 'autocomplete': 'tel-national',
                                                                 'placeholder': '700 123 456'}))
    phone_is_whatsapp = forms.BooleanField(required=False, initial=True, label='This number is on WhatsApp')
    nationality = forms.ChoiceField(choices=[('', 'Select nationality')] + NATIONALITY_CHOICES)
    email = forms.EmailField(required=False, label='Email (optional)',
                             widget=forms.EmailInput(attrs={'autocomplete': 'email', 'placeholder': 'you@email.com'}))
    residence = forms.ChoiceField(choices=[('', 'Select country')] + RESIDENCE_CHOICES, required=False,
                                  label='Country you live in now')
    gender = forms.ChoiceField(choices=[('', 'Prefer not to say')] + JobApplication.GENDER, required=False)
    experience = forms.ChoiceField(choices=[('', 'Select')] + JobApplication.EXPERIENCE, required=False,
                                   label='Work experience')
    passport = forms.ChoiceField(choices=[('', 'Select')] + JobApplication.PASSPORT, required=False,
                                 label='Do you have a passport?')
    cv = forms.FileField(required=False, label='CV / Resume (optional)',
                         widget=forms.ClearableFileInput(attrs={'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'}))
    message = forms.CharField(required=False, label='Anything else we should know? (optional)',
                              widget=forms.Textarea(attrs={'rows': 3, 'maxlength': 1000}))
    # anti-spam
    website = forms.CharField(required=False)       # honeypot, hidden via CSS
    form_token = forms.CharField(required=False)    # signed timestamp

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['job'].queryset = Job.objects.filter(is_active=True)
        self.fields['job'].label_from_instance = lambda j: f'{j.title} – {j.city or j.country}'

    # -- field cleaning ---------------------------------------------------
    def clean_full_name(self):
        name = ' '.join(self.cleaned_data['full_name'].split())
        if len(name) < 3 or not re.search(r'[A-Za-zÀ-ɏ؀-ۿ]', name):
            raise forms.ValidationError('Please enter your full name.')
        if re.search(r'https?://|www\.', name, re.I):
            raise forms.ValidationError('Please enter your name only.')
        return name

    def clean_message(self):
        msg = self.cleaned_data.get('message', '').strip()
        if re.search(r'https?://|www\.', msg, re.I):
            raise forms.ValidationError('Links are not allowed in this box.')
        return msg[:1000]

    def clean_cv(self):
        f = self.cleaned_data.get('cv')
        if not f:
            return None
        ext = os.path.splitext(f.name)[1].lower()
        if ext not in ALLOWED_CV_EXT:
            raise forms.ValidationError('Please upload a PDF, Word document or a photo (JPG/PNG).')
        if f.size > settings.CV_MAX_MB * 1024 * 1024:
            raise forms.ValidationError(f'File is too large (max {settings.CV_MAX_MB} MB).')
        head = f.read(8)
        f.seek(0)
        if not any(head.startswith(m) for m in MAGIC[ext]):
            raise forms.ValidationError('That file does not look like a valid ' + ext.strip('.').upper() + '.')
        return f

    def clean(self):
        data = super().clean()
        if data.get('website'):
            raise forms.ValidationError('Spam detected.')
        problem = check_form_token(data.get('form_token'))
        if problem == 'too_fast':
            raise forms.ValidationError('That was very quick! Please check your details and press Apply again.')
        if problem:
            raise forms.ValidationError('This page expired. Please press Apply again.')

        iso, number = data.get('phone_country'), (data.get('phone_number') or '').strip()
        if iso in BY_ISO and number:
            dial = BY_ISO[iso]['dial']
            raw = re.sub(r'[^\d+]', '', number)
            digits = re.sub(r'\D', '', raw)
            if raw.startswith('+') or digits.startswith('00'):
                full = digits[2:] if digits.startswith('00') else digits
            else:
                national = digits.lstrip('0')
                full = national if national.startswith(dial) and len(national) >= len(dial) + 8 else dial + national
            if not 8 <= len(full) <= 15:
                self.add_error('phone_number', 'Please enter a valid phone number (without the country code).')
            else:
                data['phone'] = '+' + full
        return data

    # -- persistence ------------------------------------------------------
    def save(self, ip=''):
        d = self.cleaned_data
        job = d.get('job')
        app = JobApplication(
            job=job,
            job_title=job.title if job else 'General application',
            full_name=d['full_name'],
            phone=d['phone'],
            phone_is_whatsapp=bool(d.get('phone_is_whatsapp')),
            email=d.get('email', ''),
            nationality=d['nationality'],
            residence=d.get('residence', ''),
            gender=d.get('gender', ''),
            experience=d.get('experience', ''),
            passport=d.get('passport', ''),
            message=d.get('message', ''),
            ip_hash=JobApplication.hash_ip(ip),
        )
        if d.get('cv'):
            app.cv = d['cv']
        app.save()
        return app
