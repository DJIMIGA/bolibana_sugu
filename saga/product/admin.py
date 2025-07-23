from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.db.models import Count, Q, Avg
from price_checker.models import PriceEntry
from price_checker.admin import PriceEntryInline
from accounts.admin import admin_site
from django.utils.text import slugify

# Register your models here.
from .models import Product, Category, ImageProduct, Review, Size, Color, Clothing, CulturalItem, ShippingMethod, Phone, Fabric
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
    list_display = ('name', 'parent_name', 'get_full_path', 'image_preview', 'subcategories_count', 'subsubcategories_count', 'category_type', 'color')
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
            'fields': ('name', 'slug', 'parent', 'description', 'image', 'color')
        }),
        ('Configuration', {
            'fields': ('is_main', 'order', 'category_type', 'content_type', 'filter_criteria')
        }),
    )
    
    readonly_fields = ('get_full_path', 'slug')

class PhoneAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'brand', 'model', 'storage', 'ram', 'color', 'get_price', 'get_stock', 'get_sku')
    list_filter = ('brand', 'storage', 'ram', 'color')
    search_fields = ('product__title', 'brand', 'model', 'product__sku', 'resolution')

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
            'fields': ('operating_system', 'screen_size', 'processor', 'ram', 'storage', 'resolution')
        }),
        ('Multimédia et batterie', {
            'fields': ('camera_main', 'camera_front', 'battery_capacity')
        }),
        ('Connectivité', {
            'fields': ('network', 'color')
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change and hasattr(obj, 'product'):
            product = obj.product
            product.title = f"{obj.brand} {obj.model}"
            product.save()

@admin.register(CulturalItem)
class CulturalItemAdmin(admin.ModelAdmin):
    list_display = ('get_title', 'author', 'isbn', 'date')
    search_fields = ('product__title', 'author', 'isbn')
    list_filter = ('date',)
    
    def get_title(self, obj):
        return obj.product.title
    get_title.short_description = 'Titre'
    get_title.admin_order_field = 'product__title'

    class Meta:
        verbose_name = 'Livre et Culture'
        verbose_name_plural = 'Livres et Culture'

class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'brand', 'price', 'get_stock_display', 'sku', 'is_available', 'is_salam', 'created_at', 'discount_price')
    list_filter = ('is_available', 'is_salam', 'category', 'brand', 'created_at')
    search_fields = ('title', 'sku', 'brand', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('title', 'description', 'category', 'supplier', 'brand')
        }),
        ('Prix et stock classique', {
            'fields': ('price', 'stock', 'sku', 'is_available', 'discount_price')
        }),
        ('Gestion Salam', {
            'fields': ('is_salam',),
            'classes': ('collapse',)
        }),
        ('Images', {
            'fields': ('image', 'image_urls')
        }),
        ('Caractéristiques', {
            'fields': ('specifications', 'weight', 'dimensions', 'shipping_methods')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_stock_display(self, obj):
        return obj.get_stock_display()
    get_stock_display.short_description = 'Stock'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'supplier')

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            obj.slug = slugify(obj.title)
        super().save_model(request, obj, form, change)

# Enregistrement des modèles dans l'interface d'administration 2FA
admin_site.register(Category, CategoryAdmin)
admin_site.register(Size)
admin_site.register(Product, ProductAdmin)
admin_site.register(Color)
admin_site.register(ShippingMethod)
admin_site.register(ImageProduct)
admin_site.register(Review)
admin_site.register(Clothing)
admin_site.register(Phone, PhoneAdmin)
admin_site.register(Fabric)
admin_site.register(CulturalItem)