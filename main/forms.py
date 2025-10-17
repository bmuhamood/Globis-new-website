from django import forms
from .models import ContactInquiry

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactInquiry
        fields = ['name', 'email', 'phone', 'company', 'inquiry_type', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name *',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email *',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Phone'
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company Name'
            }),
            'inquiry_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Your Message *',
                'rows': 5,
                'required': True
            }),
        }