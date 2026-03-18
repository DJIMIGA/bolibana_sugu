"""
URL configuration for saga project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from accounts.api.views import LogoutView
from accounts.admin import admin_site


def health_check(request):
    """Endpoint de santé pour le healthcheck Docker / Elestio."""
    return JsonResponse({"status": "ok"})


# Chemin d'accès admin sécurisé (toujours avec trailing slash)
ADMIN_URL = settings.ADMIN_URL.rstrip('/') + '/'

urlpatterns = [
    # Healthcheck (doit être avant tout middleware d'authentification)
    path('health/', health_check, name='health_check'),

    # URL d'administration personnalisée avec 2FA
    path(ADMIN_URL, admin_site.urls),
    
    # Autres URLs
    path('accounts/', include('accounts.urls')),
    path('', include('suppliers.urls')),
    path('cart/', include('cart.urls')),
    path('api/', include('product.api.urls')),
    path('api/', include('accounts.api.urls')),
    path('api/cart/', include('cart.api.urls')),
    path('api/inventory/', include('inventory.api.urls')),
    path('api/notifications/', include('notifications.api.urls')),
    # JWT endpoints
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/token/logout/', LogoutView.as_view(), name='token_logout'),
    path('price-checker/', include('price_checker.urls', namespace='price_checker')),
    path('api/price-checker/', include('price_checker.api.urls')),
    path('api/core/', include('core.api.urls')),
    path('core/', include('core.urls', namespace='core')),
    path('inventory/', include('inventory.urls', namespace='inventory')),
]

# Ajout des URLs pour les fichiers médias en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Configuration des gestionnaires d'erreur personnalisés
if not settings.DEBUG:
    handler404 = 'core.views.custom_404'
    handler500 = 'core.views.custom_500'
    handler403 = 'core.views.custom_403' 