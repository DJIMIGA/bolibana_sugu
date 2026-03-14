from django.contrib import admin
from accounts.admin import admin_site
from django.utils.html import format_html
from .models import Supplier, Hero, HeroImage

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'email', 'phone', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'specialty', 'created_at')
    search_fields = ('company_name', 'user__email', 'phone', 'email')
    readonly_fields = ('created_at', 'updated_at', 'slug')
    fieldsets = (
        ('Informations de base', {
            'fields': ('user', 'company_name', 'description', 'specialty')
        }),
        ('Contact', {
            'fields': ('email', 'phone', 'website', 'address')
        }),
        ('Médias', {
            'fields': ('image',)
        }),
        ('Statut', {
            'fields': ('is_verified', 'rating')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

class HeroImageInline(admin.TabularInline):
    model = HeroImage
    extra = 1
    fields = ('image', 'image_preview', 'ordre', 'is_active')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px; object-fit: contain;" />',
                obj.image.url
            )
        return "Aucune image"
    image_preview.short_description = "Aperçu"

class HeroAdmin(admin.ModelAdmin):
    list_display = ('title', 'image_preview', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'subtitle')
    readonly_fields = ('created_at', 'updated_at', 'slug')
    inlines = [HeroImageInline]
    fieldsets = (
        ('Informations principales', {
            'fields': ('title', 'subtitle')
        }),
        ('Boutons', {
            'fields': (
                'primary_button_text', 'primary_button_url',
                'secondary_button_text', 'secondary_button_url'
            )
        }),
        ('Paramètres', {
            'fields': ('is_active', 'slug', 'created_at', 'updated_at')
        }),
    )

    def image_preview(self, obj):
        active_image = obj.images.filter(is_active=True).first()
        if active_image and active_image.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; object-fit: contain;" />',
                active_image.image.url
            )
        return "Aucune image"
    image_preview.short_description = "Image active"

class HeroImageAdmin(admin.ModelAdmin):
    list_display = ('hero', 'image_preview', 'ordre', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('hero__title',)
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    fieldsets = (
        ('Informations principales', {
            'fields': ('hero', 'image', 'image_preview', 'ordre', 'is_active')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; object-fit: contain;" />',
                obj.image.url
            )
        return "Aucune image"
    image_preview.short_description = "Aperçu de l'image"

# Enregistrement avec admin_site
admin_site.register(Supplier, SupplierAdmin)
admin_site.register(Hero, HeroAdmin)
admin_site.register(HeroImage, HeroImageAdmin)
