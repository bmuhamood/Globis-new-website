from django.contrib import admin
from .models import GalleryImage, Service, RecruitmentField, CoreValue, Client, Office, ContactInquiry, Testimonial

admin.site.site_header = "GLOBIS HR Consultancy Administration"
admin.site.site_title = "GLOBIS HR Admin"
admin.site.index_title = "Dashboard"

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'order']
    list_editable = ['order']

@admin.register(RecruitmentField)
class RecruitmentFieldAdmin(admin.ModelAdmin):
    list_display = ['title', 'order']
    list_editable = ['order']

@admin.register(CoreValue)
class CoreValueAdmin(admin.ModelAdmin):
    list_display = ['number', 'title']
    list_editable = ['title']

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    list_editable = ['order']

@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ['country', 'company_name', 'is_main', 'order']
    list_editable = ['is_main', 'order']

@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'inquiry_type', 'created_at']
    list_filter = ['inquiry_type', 'created_at']
    search_fields = ['name', 'email', 'company', 'message']
    readonly_fields = ['created_at']

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'order', 'created_at']
    list_filter = ['category', 'created_at']
    list_editable = ['order']

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'company', 'location', 'rating', 'order')
    list_editable = ('order',)
    search_fields = ('client_name', 'company', 'location', 'message')