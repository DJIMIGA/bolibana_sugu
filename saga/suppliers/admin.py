from django.contrib import admin
from accounts.admin import admin_site
from .models import Supplier

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

# Enregistrement avec admin_site
admin_site.register(Supplier, SupplierAdmin)
