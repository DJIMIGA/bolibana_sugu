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
    path('products/', include('product.urls')),
    path('accounts/', include('accounts.urls')),
    path('', include('suppliers.urls')),
    path('cart/', include('cart.urls')),
    path('api/', include('product.api.urls')),
    path('price-checker/', include('price_checker.urls', namespace='price_checker')),
]

# Ajouter les URLs pour les fichiers statiques uniquement en développement
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 