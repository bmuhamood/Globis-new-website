from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('recruitment/', views.recruitment, name='recruitment'),
    path('process/', views.process, name='process'),
    path('clients/', views.clients, name='clients'),
    path('contact/', views.contact, name='contact'),
    path('gallery/', views.gallery, name='gallery'),
]