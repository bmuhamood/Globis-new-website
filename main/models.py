import hashlib
import re

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from .storage import DatabaseStorage


# --------------------------------------------------------------------------
# Media storage (rows backing main.storage.DatabaseStorage)
# --------------------------------------------------------------------------
class StoredFile(models.Model):
    name = models.CharField(max_length=500, unique=True)
    content = models.BinaryField()
    content_type = models.CharField(max_length=150, default='application/octet-stream')
    size = models.PositiveBigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# --------------------------------------------------------------------------
# Existing site content
# --------------------------------------------------------------------------
class Service(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class, e.g. fa-users")
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class RecruitmentField(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class, e.g. fa-hard-hat")
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class CoreValue(models.Model):
    title = models.CharField(max_length=100)
    number = models.IntegerField()

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f"{self.number}. {self.title}"


class Client(models.Model):
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='clients/', max_length=300, blank=True, null=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Office(models.Model):
    country = models.CharField(max_length=100)
    company_name = models.CharField(max_length=200)
    address = models.TextField()
    is_main = models.BooleanField(default=False)
    is_associate = models.BooleanField(default=False, help_text="Associate offices do not get social media links")
    phone = models.CharField(max_length=40, blank=True)
    tiktok_url = models.URLField(blank=True, verbose_name='TikTok')
    facebook_url = models.URLField(blank=True, verbose_name='Facebook')
    instagram_url = models.URLField(blank=True, verbose_name='Instagram')
    youtube_url = models.URLField(blank=True, verbose_name='YouTube')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Branch'

    def __str__(self):
        return f"{self.country} - {self.company_name}"

    @property
    def short_name(self):
        return self.country.split(',')[0]

    @property
    def has_social(self):
        return any([self.tiktok_url, self.facebook_url, self.instagram_url, self.youtube_url])


class GalleryImage(models.Model):
    CATEGORY_CHOICES = [
        ('team', 'Team'),
        ('office', 'Office'),
        ('event', 'Event'),
        ('recruitment', 'Recruitment'),
    ]

    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='gallery/', max_length=300, blank=True, null=True,
                              help_text="Photo (also used as the video poster)")
    video = models.FileField(upload_to='gallery/videos/', max_length=300, blank=True, null=True,
                             help_text="Optional MP4/WebM video (max ~40 MB)")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Gallery item'
        verbose_name_plural = 'Gallery items'

    def __str__(self):
        return self.title

    @property
    def is_video(self):
        return bool(self.video)


class ContactInquiry(models.Model):
    INQUIRY_TYPES = [
        ('recruitment', 'Recruitment Services'),
        ('tourism', 'Tourism'),
        ('trade', 'Trade'),
        ('consultation', 'Consultation'),
        ('training', 'Training'),
        ('ticketing', 'Airline Ticketing'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    company = models.CharField(max_length=200, blank=True)
    inquiry_type = models.CharField(max_length=50, choices=INQUIRY_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Contact Inquiries'

    def __str__(self):
        return f"{self.name} - {self.inquiry_type} - {self.created_at.strftime('%Y-%m-%d')}"


class Testimonial(models.Model):
    client_name = models.CharField(max_length=200)
    company = models.CharField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    message = models.TextField()
    logo = models.ImageField(upload_to='testimonials/logos/', max_length=300, blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True,
                             help_text="Optional (no longer used by the new design)")
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.client_name} ({self.company})"


# --------------------------------------------------------------------------
# Jobs & applications
# --------------------------------------------------------------------------
class Job(models.Model):
    CATEGORIES = [
        ('construction', 'Construction & Labour'),
        ('security', 'Security'),
        ('driving', 'Drivers & Transport'),
        ('hospitality', 'Hospitality & Tourism'),
        ('medical', 'Medical & Care'),
        ('admin', 'Office & Administration'),
        ('engineering', 'Engineering & Technical'),
        ('sales', 'Sales & Retail'),
        ('education', 'Education'),
        ('beauty', 'Beauty & Tailoring'),
        ('cleaning', 'Cleaning & Facilities'),
        ('other', 'Other'),
    ]
    TYPES = [('full_time', 'Full-time'), ('contract', 'Contract'), ('part_time', 'Part-time')]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.CharField(max_length=30, choices=CATEGORIES, default='other')
    country = models.CharField(max_length=100, default='United Arab Emirates')
    city = models.CharField(max_length=100, default='Dubai', blank=True)
    employment_type = models.CharField(max_length=20, choices=TYPES, default='full_time')
    salary = models.CharField(max_length=120, blank=True, help_text='e.g. "AED 1,500 – 2,200 / month"')
    working_hours = models.CharField(max_length=120, blank=True, help_text='e.g. "8 hours/day, 6 days/week"')
    contract_length = models.CharField(max_length=80, blank=True, help_text='e.g. "2 years, renewable"')
    vacancies = models.PositiveIntegerField(default=1)
    summary = models.CharField(max_length=300, blank=True, help_text="One-line teaser shown on cards")
    description = models.TextField(blank=True)
    requirements = models.TextField(blank=True, help_text="One requirement per line")
    benefits = models.TextField(blank=True, help_text="One benefit per line (e.g. Accommodation, Visa, Air ticket)")
    image = models.ImageField(upload_to='jobs/', max_length=300, blank=True, null=True,
                              help_text="Optional. A matching illustration is used when left empty.")
    is_active = models.BooleanField(default=True, help_text="Untick to hide this job from the public site")
    is_featured = models.BooleanField(default=False)
    closing_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f'{self.title}-{self.city or self.country}')[:200] or 'job'
            slug, i = base, 1
            while Job.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f'{base}-{i}'
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('job_detail', args=[self.slug])

    @property
    def requirements_list(self):
        return [l.strip(' -•\t') for l in self.requirements.splitlines() if l.strip()]

    @property
    def benefits_list(self):
        return [l.strip(' -•\t') for l in self.benefits.splitlines() if l.strip()]

    @property
    def is_open(self):
        if not self.is_active:
            return False
        return not self.closing_date or self.closing_date >= timezone.localdate()

    @property
    def location(self):
        return ', '.join(p for p in [self.city, self.country] if p)


class JobApplication(models.Model):
    STATUS = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('shortlisted', 'Shortlisted'),
        ('interview', 'Interview'),
        ('placed', 'Placed'),
        ('rejected', 'Not suitable'),
    ]
    EXPERIENCE = [
        ('none', 'No experience'),
        ('lt1', 'Less than 1 year'),
        ('1-2', '1 – 2 years'),
        ('3-5', '3 – 5 years'),
        ('6-10', '6 – 10 years'),
        ('10+', 'More than 10 years'),
    ]
    PASSPORT = [('valid', 'Yes, valid passport'), ('applying', 'Applying for one'), ('none', 'No passport yet')]
    GENDER = [('male', 'Male'), ('female', 'Female')]

    reference = models.CharField(max_length=20, unique=True, blank=True)
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True, related_name='applications')
    job_title = models.CharField(max_length=200, blank=True, help_text="Snapshot of the job title at apply time")

    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=24, help_text="International format, e.g. +256700123456")
    phone_is_whatsapp = models.BooleanField(default=True)
    email = models.EmailField(blank=True)
    nationality = models.CharField(max_length=100)
    residence = models.CharField(max_length=100, blank=True, verbose_name='Country of residence')
    gender = models.CharField(max_length=10, choices=GENDER, blank=True)
    experience = models.CharField(max_length=10, choices=EXPERIENCE, blank=True)
    passport = models.CharField(max_length=10, choices=PASSPORT, blank=True)
    cv = models.FileField(upload_to='cv/', storage=DatabaseStorage(), max_length=300, blank=True, null=True)  # always private, in DB
    message = models.TextField(blank=True)

    status = models.CharField(max_length=15, choices=STATUS, default='new', db_index=True)
    admin_notes = models.TextField(blank=True)
    contacted_at = models.DateTimeField(blank=True, null=True)

    ip_hash = models.CharField(max_length=64, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.reference or self.pk} – {self.full_name}'

    def save(self, *args, **kwargs):
        if self.job and not self.job_title:
            self.job_title = self.job.title
        super().save(*args, **kwargs)
        if not self.reference:
            self.reference = f'GL-{self.created_at:%y}{self.pk:05d}'
            JobApplication.objects.filter(pk=self.pk).update(reference=self.reference)

    @staticmethod
    def hash_ip(ip):
        return hashlib.sha256(f'globis:{ip}'.encode()).hexdigest()[:40] if ip else ''

    @property
    def digits(self):
        return re.sub(r'\D', '', self.phone)

    @property
    def whatsapp_link(self):
        return f'https://wa.me/{self.digits}'

    @property
    def display_job(self):
        return self.job_title or 'General application'
