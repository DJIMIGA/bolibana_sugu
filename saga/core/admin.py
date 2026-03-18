from django.contrib import admin
from django.utils.html import format_html
from .models import SiteConfiguration, CookieConsent, StaticPage

class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'company_name', 'email', 'phone_number', 'maintenance_mode']
    list_editable = ['maintenance_mode']
    search_fields = ['site_name', 'company_name', 'email']
    fieldsets = (
        ('Informations générales', {
            'fields': ('site_name', 'phone_number', 'email', 'address', 'rccm')
        }),
        ('Réseaux sociaux', {
            'fields': ('whatsapp_number', 'facebook_url', 'instagram_url', 'twitter_url', 'tiktok_url')
        }),
        ('Informations légales', {
            'fields': ('company_name', 'company_type', 'company_address', 'ninea_number')
        }),
        ('Métadonnées', {
            'fields': ('meta_description', 'meta_keywords')
        }),
        ('Configuration du site', {
            'fields': ('maintenance_mode', 'google_analytics_id', 'facebook_pixel_id', 'facebook_access_token')
        }),
        ('Horaires et services', {
            'fields': ('opening_hours', 'opening_hours_detailed', 'delivery_info', 'return_policy')
        }),
        ('Configuration visuelle', {
            'fields': ('logo_url', 'logo_small_url', 'favicon_url')
        }),
        ('Identite visuelle - Branding', {
            'fields': ('brand_primary_color', 'brand_secondary_color', 'brand_accent_color', 
                       'brand_tagline', 'brand_short_tagline'),
            'description': 'Couleurs et identite de marque BoliBana (vert #008000, or #FFD700, rouge #EF4444)'
        }),
    )
    
    def has_add_permission(self, request):
        # Permettre seulement une configuration
        return not SiteConfiguration.objects.exists()

class CookieConsentAdmin(admin.ModelAdmin):
    list_display = ['user_display', 'session_display', 'analytics', 'marketing', 'created_at', 'updated_at']
    list_filter = ['analytics', 'marketing', 'created_at', 'updated_at']
    search_fields = ['user__username', 'user__email', 'session_id']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    def user_display(self, obj):
        if obj.user:
            username = getattr(obj.user, 'username', None)
            email = getattr(obj.user, 'email', '')
            if username:
                return f"{username} ({email})"
            return f"{email}"
        return "Utilisateur anonyme"
    user_display.short_description = "Utilisateur"
    
    def session_display(self, obj):
        if obj.session_id:
            return obj.session_id[:20] + "..." if len(obj.session_id) > 20 else obj.session_id
        return "Pas de session"
    session_display.short_description = "Session"
    
    def has_add_permission(self, request):
        # Les consentements sont créés automatiquement via l'API
        return False
    
    def has_change_permission(self, request, obj=None):
        # Permettre la modification pour corriger les données si nécessaire
        return True
    
    def has_delete_permission(self, request, obj=None):
        # Permettre la suppression pour le nettoyage des données
        return True

class StaticPageAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'is_published', 'updated_at']
    list_editable = ['is_published']
    list_filter = ['is_published']
    search_fields = ['title', 'slug', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']


# Enregistrement différé pour éviter les problèmes d'import circulaire
def register_admin_models(admin_site=None):
    if admin_site is None:
        from accounts.admin import admin_site
    admin_site.register(SiteConfiguration, SiteConfigurationAdmin)
    admin_site.register(CookieConsent, CookieConsentAdmin)
    admin_site.register(StaticPage, StaticPageAdmin)