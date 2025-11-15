from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('restaurant/', include('restaurant.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # Include the auth URLs
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)