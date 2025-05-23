from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.db.models import Count, Q, Avg
from price_checker.models import PriceEntry
from price_checker.admin import PriceEntryInline
from accounts.admin import admin_site

# Register your models here.
from .models import Product, Category, ImageProduct, Review, Size, Color, Clothing, CulturalItem, ShippingMethod, Phone
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline

class CategoryLevelFilter(admin.SimpleListFilter):
    title = 'Niveau de la catégorie'
    parameter_name = 'level'

    def lookups(self, request, model_admin):
        return (
            ('root', 'Catégories racines (sans parent)'),
            ('level1', 'Catégories de niveau 1 (avec parent)'),
            ('level2', 'Catégories de niveau 2 (avec grand-parent)'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'root':
            return queryset.filter(parent__isnull=True)
        elif self.value() == 'level1':
            return queryset.filter(parent__isnull=False, parent__parent__isnull=True)
        elif self.value() == 'level2':
            return queryset.filter(parent__parent__isnull=False)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_name', 'get_full_path', 'image_preview', 'subcategories_count', 'subsubcategories_count')
    list_filter = (CategoryLevelFilter, 'parent',)
    search_fields = ('name',)
    ordering = ('parent__name', 'name')
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            subcategories_count=Count('children'),
            subsubcategories_count=Count('children__children')
        )
    
    def parent_name(self, obj):
        if obj.parent:
            url = reverse('admin:product_category_change', args=[obj.parent.id])
            return mark_safe(f'<a href="{url}">{obj.parent.name}</a>')
        return '-'
    parent_name.short_description = 'Catégorie parente'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return '-'
    image_preview.short_description = 'Image'
    
    def get_full_path(self, obj):
        path = []
        current = obj
        while current:
            url = reverse('admin:product_category_change', args=[current.id])
            path.insert(0, f'<a href="{url}">{current.name}</a>')
            current = current.parent
        return mark_safe(' > '.join(path))
    get_full_path.short_description = 'Chemin complet'
    
    def subcategories_count(self, obj):
        count = obj.subcategories_count
        if count > 0:
            url = reverse('admin:product_category_changelist') + f'?parent__id__exact={obj.id}'
            return mark_safe(f'<a href="{url}">{count} sous-catégories</a>')
        return '-'
    subcategories_count.short_description = 'Sous-catégories'
    
    def subsubcategories_count(self, obj):
        count = obj.subsubcategories_count
        if count > 0:
            return f'{count} sous-sous-catégories'
        return '-'
    subsubcategories_count.short_description = 'Sous-sous-catégories'

    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'parent', 'image')
        }),
        ('Hiérarchie', {
            'fields': ('get_full_path',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('get_full_path',)

class PhoneAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'brand', 'model', 'storage', 'ram', 'color', 'get_price', 'get_stock', 'get_sku')
    list_filter = ('brand', 'storage', 'ram', 'color')
    search_fields = ('product__title', 'brand', 'model', 'product__sku')

    def get_name(self, obj):
        return obj.product.title if hasattr(obj, 'product') else '-'
    get_name.short_description = 'Nom'

    def get_price(self, obj):
        return obj.product.price if hasattr(obj, 'product') else '-'
    get_price.short_description = 'Prix'

    def get_stock(self, obj):
        return obj.product.stock if hasattr(obj, 'product') else '-'
    get_stock.short_description = 'Stock'

    def get_sku(self, obj):
        return obj.product.sku if hasattr(obj, 'product') else '-'
    get_sku.short_description = 'SKU'

    fieldsets = (
        ('Informations de base', {
            'fields': ('product', 'brand', 'model', 'is_new', 'imei')
        }),
        ('Caractéristiques techniques', {
            'fields': ('operating_system', 'screen_size', 'processor', 'ram', 'storage')
        }),
        ('Multimédia et batterie', {
            'fields': ('camera_main', 'camera_front', 'battery_capacity')
        }),
        ('Connectivité et garantie', {
            'fields': ('network', 'warranty', 'color')
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change and hasattr(obj, 'product'):
            product = obj.product
            product.title = f"{obj.brand} {obj.model}"
            product.save()

# Enregistrement des modèles dans l'interface d'administration 2FA
admin_site.register(Category, CategoryAdmin)
admin_site.register(Size)
admin_site.register(Product)
admin_site.register(Color)
admin_site.register(ShippingMethod)
admin_site.register(ImageProduct)
admin_site.register(Review)
admin_site.register(Clothing)
admin_site.register(CulturalItem)
admin_site.register(Phone, PhoneAdmin)
