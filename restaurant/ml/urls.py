"""
URL routes for ML forecasting endpoints.
"""

from django.urls import path
from . import views

app_name = 'ml'

urlpatterns = [
    path('forecast/', views.forecast_dashboard, name='forecast_dashboard'),
    path('api/generate-forecast/', views.generate_forecast, name='generate_forecast'),
    path('api/multi-forecast/', views.multi_forecast, name='multi_forecast'),
    path('api/status/', views.forecast_status, name='forecast_status'),
]
