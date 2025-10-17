from django.db import models

class Service(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class")
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title

class RecruitmentField(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class")
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
    logo = models.ImageField(upload_to='clients/', blank=True, null=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.name

class Office(models.Model):
    country = models.CharField(max_length=100)
    company_name = models.CharField(max_length=200)
    address = models.TextField()
    is_main = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.country} - {self.company_name}"

class GalleryImage(models.Model):
    CATEGORY_CHOICES = [
        ('team', 'Team'),
        ('office', 'Office'),
        ('event', 'Event'),
        ('recruitment', 'Recruitment'),
    ]
    
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='gallery/')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.title
    
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
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Contact Inquiries'
    
    def __str__(self):
        return f"{self.name} - {self.inquiry_type} - {self.created_at.strftime('%Y-%m-%d')}"