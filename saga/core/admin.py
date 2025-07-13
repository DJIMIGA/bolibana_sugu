from django.contrib import admin
from django.utils.html import format_html
from accounts.admin import admin_site
from .models import SiteConfiguration

class SiteConfigurationAdmin(admin.ModelAdmin):
    """Interface admin pour la configuration du site"""
    
    def has_add_permission(self, request):
        """Empêcher la création de plusieurs configurations"""
        return not SiteConfiguration.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Empêcher la suppression de la configuration"""
        return False
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('site_name', 'phone_number', 'email', 'address', 'rccm', 'ninea_number')
        }),
        ('Informations de l\'entreprise', {
            'fields': ('company_name', 'company_type', 'company_address')
        }),
        ('Réseaux sociaux', {
            'fields': ('whatsapp_number', 'facebook_url', 'instagram_url', 'twitter_url', 'tiktok_url'),
            'classes': ('collapse',)
        }),
        ('Horaires et services', {
            'fields': ('opening_hours', 'opening_hours_detailed', 'delivery_info', 'return_policy'),
            'classes': ('collapse',)
        }),
        ('Configuration visuelle', {
            'fields': ('logo_url', 'favicon_url'),
            'classes': ('collapse',)
        }),
        ('Contenu du footer - À propos', {
            'fields': (
                ('about_story_title', 'about_story_content'),
                ('about_values_title', 'about_values_content'),
            ),
            'classes': ('collapse',)
        }),
        ('Contenu du footer - Services', {
            'fields': (
                ('service_loyalty_title', 'service_loyalty_content'),
                ('service_express_title', 'service_express_content'),
            ),
            'classes': ('collapse',)
        }),
        ('Contenu du footer - Assistance', {
            'fields': (
                ('help_center_title', 'help_center_content'),
                ('help_returns_title', 'help_returns_content'),
                ('help_warranty_title', 'help_warranty_content'),
            ),
            'classes': ('collapse',)
        }),
        ('Métadonnées SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Configuration avancée', {
            'fields': ('maintenance_mode', 'google_analytics_id'),
            'classes': ('collapse',)
        }),
    )
    
    list_display = ('site_name', 'phone_number', 'email', 'maintenance_mode')
    list_editable = ('maintenance_mode',)
    
    def get_readonly_fields(self, request, obj=None):
        """Rendre certains champs en lecture seule"""
        if obj:  # Si on édite un objet existant
            return ('id',)
        return ()
    
    def save_model(self, request, obj, form, change):
        """S'assurer qu'il n'y a qu'une seule configuration"""
        if not change:  # Si c'est une nouvelle configuration
            obj.id = 1  # Forcer l'ID à 1
        super().save_model(request, obj, form, change)

# Enregistrement avec admin_site
admin_site.register(SiteConfiguration, SiteConfigurationAdmin) 