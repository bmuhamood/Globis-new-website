from django.shortcuts import render, redirect
from django.contrib import messages
from .models import GalleryImage, Service, RecruitmentField, CoreValue, Client, Office, ContactInquiry
from .forms import ContactForm

def home(request):
    services = Service.objects.all()[:6]
    core_values = CoreValue.objects.all()
    clients = Client.objects.all()
    
    context = {
        'services': services,
        'core_values': core_values,
        'clients': clients,
    }
    return render(request, 'main/home.html', context)

def about(request):
    core_values = CoreValue.objects.all()
    return render(request, 'main/about.html', {'core_values': core_values})

def services(request):
    services = Service.objects.all()
    return render(request, 'main/services.html', {'services': services})

def recruitment(request):
    fields = RecruitmentField.objects.all()
    return render(request, 'main/recruitment.html', {'fields': fields})

def process(request):
    return render(request, 'main/process.html')

def clients(request):
    clients = Client.objects.all()
    return render(request, 'main/clients.html', {'clients': clients})

def contact(request):
    offices = Office.objects.all()
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your inquiry! We will get back to you soon.')
            return redirect('contact')
    else:
        form = ContactForm()
    
    context = {
        'form': form,
        'offices': offices,
    }
    return render(request, 'main/contact.html', context)

def gallery(request):
    images = GalleryImage.objects.all()
    category = request.GET.get('category')
    if category:
        images = images.filter(category=category)
    
    context = {'images': images}
    return render(request, 'main/gallery.html', context)