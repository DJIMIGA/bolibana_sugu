"""
URL configuration for saga project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django_otp.admin import OTPAdminSite
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_totp.admin import TOTPDeviceAdmin
from accounts.models import Shopper

# Chemin d'accès admin sécurisé
ADMIN_URL = settings.ADMIN_URL

# Configuration de l'admin avec 2FA
class MyOTPAdminSite(OTPAdminSite):
    pass

admin_site = MyOTPAdminSite(name='OTPAdmin')
admin_site.register(Shopper)
admin_site.register(TOTPDevice, TOTPDeviceAdmin)

urlpatterns = [
    # Redirection de l'URL admin par défaut vers notre URL personnalisée
    path('240821', RedirectView.as_view(url=f'/{settings.ADMIN_URL}', permanent=True)),
    
    # URL d'administration personnalisée avec 2FA
    path(f'{settings.ADMIN_URL}', admin_site.urls),
    
    # Autres URLs
    path('products/', include('product.urls')),
    path('accounts/', include('accounts.urls')),
    path('', include('suppliers.urls')),
    path('cart/', include('cart.urls')),
    path('api/', include('product.api.urls')),
    path('price-checker/', include('price_checker.urls', namespace='price_checker')),
]

# Ajout des URLs pour les fichiers médias en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 