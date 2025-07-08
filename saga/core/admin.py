from django.contrib import admin
from django.utils.html import format_html
from .models import SiteConfiguration

@admin.register(SiteConfiguration)
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
            'fields': ('site_name', 'phone_number', 'email', 'address', 'rccm')
        }),
        ('Informations de l\'entreprise', {
            'fields': ('company_name', 'company_type', 'company_address')
        }),
        ('Réseaux sociaux', {
            'fields': ('facebook_url', 'instagram_url', 'twitter_url'),
            'classes': ('collapse',)
        }),
        ('Métadonnées SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Configuration avancée', {
            'fields': ('maintenance_mode', 'google_analytics_id', 'opening_hours'),
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