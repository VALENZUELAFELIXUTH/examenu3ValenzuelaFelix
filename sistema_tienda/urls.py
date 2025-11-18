# sistema_tienda/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView  # Para redirecciones

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/login/')),  # Redirige la raíz al login
    path('', include('tienda.urls')),  # Incluye todas las URLs de la app 'tienda'
]
