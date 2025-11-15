# home/urls.py
from django.urls import path
from . import views

app_name = 'crispy_forms'

urlpatterns = [
    path('', views.HomeView.as_view(), name='index'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
]