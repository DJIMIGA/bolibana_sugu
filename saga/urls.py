"""
URL configuration for saga project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from accounts.admin import admin_site

# Chemin d'accès admin sécurisé
ADMIN_URL = settings.ADMIN_URL

urlpatterns = [
    # URL d'administration personnalisée avec 2FA
    path(f'{settings.ADMIN_URL}', admin_site.urls),
    
    # Autres URLs
    path('accounts/', include('accounts.urls')),
    path('', include('suppliers.urls')),
    path('cart/', include('cart.urls')),
    path('api/', include('product.api.urls')),
    path('api/', include('accounts.api.urls')),
    path('api/cart/', include('cart.api.urls')),
    # JWT endpoints
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('price-checker/', include('price_checker.urls', namespace='price_checker')),
    path('core/', include('core.urls', namespace='core')),
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