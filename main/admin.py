from django.contrib import admin

from .models import (Client, ContactInquiry, CoreValue, GalleryImage, Job, JobApplication, Office,
                     RecruitmentField, Service, StoredFile, Testimonial)

admin.site.site_header = "GLOBIS HR Consultancy Administration"
admin.site.site_title = "GLOBIS HR Consultancy Admin"
admin.site.index_title = "Site content"


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
    list_display = ['name', 'email', 'inquiry_type', 'is_read', 'created_at']
    list_filter = ['inquiry_type', 'is_read', 'created_at']
    search_fields = ['name', 'email', 'company', 'message']
    readonly_fields = ['created_at']


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'order', 'created_at']
    list_filter = ['category', 'created_at']
    list_editable = ['order']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'company', 'location', 'order')
    list_editable = ('order',)
    search_fields = ('client_name', 'company', 'location', 'message')


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'city', 'is_active', 'is_featured', 'created_at']
    list_filter = ['category', 'is_active', 'is_featured']
    search_fields = ['title', 'summary']
    list_editable = ['is_active', 'is_featured']


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['reference', 'full_name', 'phone', 'nationality', 'job_title', 'status', 'created_at']
    list_filter = ['status', 'nationality', 'created_at']
    search_fields = ['full_name', 'phone', 'email', 'reference']
    readonly_fields = ['reference', 'created_at', 'ip_hash']


@admin.register(StoredFile)
class StoredFileAdmin(admin.ModelAdmin):
    list_display = ['name', 'content_type', 'size', 'updated_at']
    search_fields = ['name']
    exclude = ['content']
    readonly_fields = ['name', 'content_type', 'size']
    list_per_page = 50

    def has_add_permission(self, request):
        return False
