"""
URL configuration for saga project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Vues Django classiques (web)
    path('admin/', admin.site.urls),
    path('', include('suppliers.urls')),
    path('products/', include('product.urls')),
    path('accounts/', include('accounts.urls')),
    path('cart/', include('cart.urls', namespace='cart')),
    
    # API pour React Native (mobile et web moderne)
    path('api/v1/', include('product.api.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 