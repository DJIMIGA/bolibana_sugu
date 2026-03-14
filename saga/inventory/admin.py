from django.contrib import admin
from django.utils.html import format_html
from django import forms
from accounts.admin import admin_site
from .models import (
    ExternalProduct,
    ExternalCategory,
    ApiKey
)


class ExternalProductAdmin(admin.ModelAdmin):
    list_display = ['product', 'external_id', 'external_sku', 'sync_status', 'last_synced_at']
    list_filter = ['sync_status', 'last_synced_at']
    search_fields = ['product__title', 'external_sku', 'external_id']
    readonly_fields = ['last_synced_at']
    raw_id_fields = ['product']
    fieldsets = (
        ('Produit SagaKore', {
            'fields': ('product',)
        }),
        ('Informations B2B', {
            'fields': ('external_id', 'external_sku', 'external_category_id')
        }),
        ('Synchronisation', {
            'fields': ('sync_status', 'sync_error', 'last_synced_at')
        }),
    )


class ExternalCategoryAdmin(admin.ModelAdmin):
    list_display = ['category', 'external_id', 'external_parent_id', 'last_synced_at']
    list_filter = ['last_synced_at']
    search_fields = ['category__name', 'external_id']
    readonly_fields = ['last_synced_at']
    raw_id_fields = ['category']
    fieldsets = (
        ('Catégorie SagaKore', {
            'fields': ('category',)
        }),
        ('Informations B2B', {
            'fields': ('external_id', 'external_parent_id', 'last_synced_at')
        }),
    )


class ApiKeyForm(forms.ModelForm):
    """Formulaire pour l'admin avec champ pour la clé API en clair"""
    api_key = forms.CharField(
        label='Clé API',
        widget=forms.PasswordInput(attrs={'placeholder': 'Entrez la clé API'}),
        help_text='La clé sera chiffrée avant stockage',
        required=False
    )
    
    class Meta:
        model = ApiKey
        fields = ['name', 'is_active', 'api_key']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Ne pas afficher la clé existante (sécurité)
            self.fields['api_key'].help_text = 'Laissez vide pour conserver la clé actuelle. Entrez une nouvelle clé pour la modifier.'
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        api_key = self.cleaned_data.get('api_key')
        
        if api_key:
            # Chiffrer et stocker la nouvelle clé
            instance.set_key(api_key)
        
        if commit:
            instance.save()
        return instance


class ApiKeyAdmin(admin.ModelAdmin):
    form = ApiKeyForm
    list_display = ['name', 'is_active_badge', 'created_at', 'last_used_at', 'key_preview']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'last_used_at', 'key_preview']
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'is_active')
        }),
        ('Clé API', {
            'fields': ('api_key', 'key_preview'),
            'description': 'Entrez la clé API en clair. Elle sera automatiquement chiffrée avant stockage.'
        }),
        ('Dates', {
            'fields': ('created_at', 'last_used_at')
        }),
    )
    
    def is_active_badge(self, obj):
        """Affiche le statut avec un badge coloré"""
        if obj.is_active:
            return format_html(
                '<span style="background-color: green; color: white; padding: 3px 8px; border-radius: 3px;">Active</span>'
            )
        return format_html(
            '<span style="background-color: gray; color: white; padding: 3px 8px; border-radius: 3px;">Inactive</span>'
        )
    is_active_badge.short_description = 'Statut'
    
    def key_preview(self, obj):
        """Affiche un aperçu de la clé (sans la révéler)"""
        if obj.pk and obj.key_encrypted:
            try:
                key = obj.get_key()
                if len(key) > 10:
                    return f"{key[:6]}...{key[-4:]}"
                return "***"
            except:
                return "Erreur de déchiffrement"
        return "Aucune clé"
    key_preview.short_description = 'Aperçu de la clé'


# Enregistrement avec admin_site (admin 2FA)
admin_site.register(ExternalProduct, ExternalProductAdmin)
admin_site.register(ExternalCategory, ExternalCategoryAdmin)
admin_site.register(ApiKey, ApiKeyAdmin)
