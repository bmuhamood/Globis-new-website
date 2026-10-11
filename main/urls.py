from django.urls import path, re_path

from . import portal, views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('recruitment/', views.recruitment, name='recruitment'),
    path('process/', views.process, name='process'),
    path('clients/', views.clients, name='clients'),
    path('contact/', views.contact, name='contact'),
    path('gallery/', views.gallery, name='gallery'),

    # Jobs & public application (no login)
    path('jobs/', views.jobs, name='jobs'),
    path('jobs/<slug:slug>/', views.job_detail, name='job_detail'),
    path('apply/', views.apply, name='apply'),
    path('apply/done/', views.apply_done, name='apply_done'),
    path('apply/<slug:slug>/', views.apply, name='apply_job'),

    # Staff portal
    path('portal/login/', portal.PortalLoginView.as_view(), name='portal_login'),
    path('portal/logout/', portal.portal_logout, name='portal_logout'),
    path('portal/', portal.dashboard, name='portal'),
    path('portal/applications/', portal.applications, name='portal_applications'),
    path('portal/applications/export.csv', portal.applications_csv, name='portal_applications_csv'),
    path('portal/applications/<int:pk>/', portal.application_detail, name='portal_application'),
    path('portal/jobs/', portal.jobs_list, name='portal_jobs'),
    path('portal/jobs/new/', portal.job_edit, name='portal_job_new'),
    path('portal/jobs/<int:pk>/', portal.job_edit, name='portal_job_edit'),
    path('portal/jobs/<int:pk>/toggle/', portal.job_toggle, name='portal_job_toggle'),
    path('portal/jobs/<int:pk>/delete/', portal.job_delete, name='portal_job_delete'),
    path('portal/inquiries/', portal.inquiries, name='portal_inquiries'),
    path('portal/team/', portal.team, name='portal_team'),
    path('portal/<str:kind>/', portal.crud_list, name='portal_crud'),
    path('portal/<str:kind>/new/', portal.crud_edit, name='portal_crud_new'),
    path('portal/<str:kind>/<int:pk>/', portal.crud_edit, name='portal_crud_edit'),
    path('portal/<str:kind>/<int:pk>/delete/', portal.crud_delete, name='portal_crud_delete'),

    # Infrastructure
    path('healthz/', views.healthz, name='healthz'),
    path('robots.txt', views.robots),
    path('sitemap.xml', views.sitemap),
    re_path(r'^media/(?P<path>.+)$', views.media_file, name='media'),
]
