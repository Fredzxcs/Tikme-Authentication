from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('authentication.urls')),  # API routes for authentication
    path('systemadmin/', admin.site.urls),  # Admin interface
]
