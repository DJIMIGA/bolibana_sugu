from django.contrib import admin
import logging
from django.utils import timezone
from django.utils.html import format_html
from django_otp.admin import OTPAdminSite
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_totp.admin import TOTPDeviceAdmin

# Register your models here.
from .models import Shopper, ShippingAddress, AllowedIP

# Configuration du logger
logger = logging.getLogger('accounts.admin')

# Configuration des classes d'administration
class ShopperAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        logger.debug(f"=== OTP DEBUG INFO ===")
        logger.debug(f"User: {request.user.email}")
        logger.debug(f"OTP verified: {request.user.is_verified()}")
        logger.debug(f"User is authenticated: {request.user.is_authenticated}")
        logger.debug(f"User is staff: {request.user.is_staff}")
        logger.debug(f"User is superuser: {request.user.is_superuser}")
        logger.debug(f"====================")
        return super().has_module_permission(request)

class AllowedIPAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'description', 'status', 'last_used', 'expires_at', 'added_by')
    list_filter = ('is_active', 'created_at', 'expires_at')
    search_fields = ('ip_address', 'description')
    readonly_fields = ('created_at', 'updated_at', 'last_used')
    fieldsets = (
        ('Informations de base', {
            'fields': ('ip_address', 'description', 'is_active')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at', 'last_used', 'expires_at')
        }),
        ('Utilisateur', {
            'fields': ('added_by',)
        }),
    )

    def status(self, obj):
        if not obj.is_active:
            return format_html('<span style="color: red;">Inactif</span>')
        if obj.is_expired():
            return format_html('<span style="color: orange;">Expiré</span>')
        return format_html('<span style="color: green;">Actif</span>')
    status.short_description = 'Statut'

    def save_model(self, request, obj, form, change):
        if not change:  # Si c'est une nouvelle entrée
            obj.added_by = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('added_by')

# Configuration de l'admin avec 2FA
class MyOTPAdminSite(OTPAdminSite):
    """
    Site d'administration personnalisé avec authentification à deux facteurs.
    """
    def has_permission(self, request):
        """
        Vérifie si l'utilisateur a la permission d'accéder à l'interface d'administration.
        """
        return super().has_permission(request) and request.user.is_verified()

# Création de l'instance du site d'administration 2FA
admin_site = MyOTPAdminSite(name='OTPAdmin')

# Enregistrement des modèles pour l'interface d'administration 2FA
def register_admin_models(admin_site):
    """
    Enregistre les modèles dans l'interface d'administration 2FA.
    Cette fonction est utilisée pour configurer l'interface d'administration sécurisée.
    """
    admin_site.register(Shopper, ShopperAdmin)
    admin_site.register(TOTPDevice, TOTPDeviceAdmin)
    admin_site.register(AllowedIP, AllowedIPAdmin)
    admin_site.register(ShippingAddress)

# Enregistrement initial des modèles pour l'admin 2FA
register_admin_models(admin_site)