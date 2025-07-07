from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Avg, Max, Min, Count, F, Q
from django.utils import timezone
from datetime import timedelta
from accounts.admin import admin_site
from .models import (
    City, PriceSubmission, PriceEntry, 
    PriceDeactivation, ProductStatus, PriceValidation
)
from product.models import Product, Category

class ProductStatusInline(admin.StackedInline):
    model = ProductStatus
    can_delete = False
    verbose_name_plural = 'Statut'
    fields = ('status', 'visibility', 'target_price')
    readonly_fields = ('created_at', 'updated_at')

    def has_add_permission(self, request, obj=None):
        return False

class PriceEntryInline(admin.TabularInline):
    model = PriceEntry
    extra = 0
    fields = ('city', 'price', 'created_at', 'is_active')
    readonly_fields = ('created_at',)
    can_delete = True
    ordering = ['-created_at']
    show_change_link = True

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(PriceSubmission)
class PriceSubmissionAdmin(admin.ModelAdmin):
    list_display = ('product', 'city', 'price', 'user', 'status', 'created_at')
    list_filter = ('status', 'city', 'created_at')
    search_fields = ('product__title', 'user__username')
    readonly_fields = ('created_at', 'validated_at')
    fieldsets = (
        ('Informations de base', {
            'fields': ('product', 'city', 'price', 'user')
        }),
        ('Validation', {
            'fields': ('status', 'validation_notes', 'validated_by', 'validated_at')
        }),
        ('Dates', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'product', 'city', 'user', 'validated_by'
        )

@admin.register(PriceEntry)
class PriceEntryAdmin(admin.ModelAdmin):
    list_display = ('product', 'city', 'price', 'user', 'is_active', 'created_at')
    list_filter = ('is_active', 'city', 'created_at')
    search_fields = ('product__title', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Informations de base', {
            'fields': ('product', 'city', 'price', 'user', 'is_active')
        }),
        ('Soumission', {
            'fields': ('submission',),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'product', 'city', 'user', 'submission'
        )

@admin.register(PriceDeactivation)
class PriceDeactivationAdmin(admin.ModelAdmin):
    list_display = ('price_entry', 'admin_user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('price_entry__product__title', 'admin_user__username')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Informations de base', {
            'fields': ('price_entry', 'admin_user', 'notes')
        }),
        ('Dates', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'price_entry', 'admin_user'
        )

@admin.register(ProductStatus)
class ProductStatusAdmin(admin.ModelAdmin):
    list_display = ('product', 'status', 'visibility', 'target_price', 'updated_at')
    list_filter = ('status', 'visibility')
    search_fields = ('product__title',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Informations de base', {
            'fields': ('product', 'status', 'visibility', 'target_price')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')

@admin.register(PriceValidation)
class PriceValidationAdmin(admin.ModelAdmin):
    list_display = ('price_entry', 'admin_user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('price_entry__product__title', 'admin_user__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Informations de base', {
            'fields': ('price_entry', 'admin_user', 'status', 'notes')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'price_entry', 'admin_user'
        )

# Enregistrement avec admin_site
admin_site.register(City, CityAdmin)
admin_site.register(PriceSubmission, PriceSubmissionAdmin)
admin_site.register(PriceEntry, PriceEntryAdmin)
admin_site.register(PriceDeactivation, PriceDeactivationAdmin)
admin_site.register(ProductStatus, ProductStatusAdmin)
admin_site.register(PriceValidation, PriceValidationAdmin) 