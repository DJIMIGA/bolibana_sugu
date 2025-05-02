from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.db.models import Count, Q
from price_checker.models import PriceEntry
from price_checker.admin import PriceEntryInline

# Register your models here.
from .models import Product, Category, ImageProduct, Review, Size, Color, Clothing, CulturalItem, ShippingMethod, Phone, PhoneVariant, PhoneVariantImage
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

admin.site.register(Category, CategoryAdmin)
admin.site.register(Size)
admin.site.register(Color)
admin.site.register(ShippingMethod)
admin.site.register(ImageProduct)
admin.site.register(Review)
admin.site.register(Clothing)
admin.site.register(CulturalItem)
admin.site.register(PhoneVariantImage)

class PhoneVariantInline(admin.TabularInline):
    model = PhoneVariant
    extra = 1
    fields = ('color', 'storage', 'price', 'stock', 'sku', 'image_preview')
    readonly_fields = ('sku', 'image_preview')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "-"
    image_preview.short_description = 'Aperçu'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'supplier', 'is_active', 'created_at', 'current_price', 'price_trend')
    list_filter = ('is_active', 'category', 'supplier', 'created_at')
    search_fields = ('title', 'description', 'supplier__name')
    readonly_fields = ('created_at', 'updated_at', 'current_price', 'price_trend')
    list_editable = ('is_active',)
    date_hierarchy = 'created_at'
    inlines = [PriceEntryInline]

    fieldsets = (
        ('Informations de base', {
            'fields': ('title', 'category', 'supplier', 'price', 'description', 'highlight', 'image', 'is_active')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Prix', {
            'fields': ('current_price', 'price_trend'),
            'classes': ('collapse',)
        }),
    )

    def current_price(self, obj):
        latest_price = obj.price_entries.filter(is_active=True).first()
        if latest_price:
            return f"{latest_price.price} FCFA ({latest_price.city.name})"
        return '-'
    current_price.short_description = 'Prix actuel'

    def price_trend(self, obj):
        prices = obj.price_entries.filter(is_active=True).order_by('-created_at')[:2]
        if len(prices) >= 2:
            change = prices[0].price - prices[1].price
            if change == 0:
                return format_html('<span style="color: gray">Stable</span>')
            color = 'green' if change > 0 else 'red'
            sign = '+' if change > 0 else ''
            return format_html(
                '<span style="color: {}">{}{} FCFA</span>',
                color,
                sign,
                change
            )
        elif len(prices) == 1:
            return format_html('<span style="color: blue">Nouveau prix</span>')
        return '-'
    price_trend.short_description = 'Tendance'

@admin.register(Phone)
class PhoneAdmin(admin.ModelAdmin):
    list_display = ('model', 'operating_system', 'get_variants_count', 'get_min_price', 'get_max_price', 'is_new')
    list_filter = ('operating_system', 'is_new')
    search_fields = ('model', 'imei')
    inlines = [PhoneVariantInline]

    def get_variants_count(self, obj):
        count = obj.variants.count()
        if count > 0:
            url = reverse('admin:product_phonevariant_changelist') + f'?phone__id__exact={obj.id}'
            return mark_safe(f'<a href="{url}">{count} variantes</a>')
        return "-"
    get_variants_count.short_description = 'Variantes'

    def get_min_price(self, obj):
        min_price = obj.get_min_price()
        return f"{min_price} FCFA" if min_price else "-"
    get_min_price.short_description = 'Prix min'

    def get_max_price(self, obj):
        max_price = obj.get_max_price()
        return f"{max_price} FCFA" if max_price else "-"
    get_max_price.short_description = 'Prix max'

    fieldsets = (
        ('Informations de base', {
            'fields': ('product', 'model', 'is_new', 'imei')
        }),
        ('Caractéristiques techniques', {
            'fields': ('operating_system', 'screen_size', 'resolution', 'processor', 'ram')
        }),
        ('Multimédia et batterie', {
            'fields': ('camera_main', 'camera_front', 'battery_capacity')
        }),
        ('Connectivité et garantie', {
            'fields': ('network', 'warranty', 'box_included', 'accessories')
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change and hasattr(obj, 'product'):
            product = obj.product
            product.title = f"{obj.model}"
            product.save()

class PhoneVariantImageInline(admin.TabularInline):
    model = PhoneVariantImage
    extra = 1
    fields = ('image', 'is_primary', 'order')
    readonly_fields = ('order',)

@admin.register(PhoneVariant)
class PhoneVariantAdmin(admin.ModelAdmin):
    list_display = ('phone', 'color', 'storage', 'ram', 'price', 'stock', 'sku', 'disponible_salam', 'image_preview')
    list_filter = ('phone', 'color', 'storage', 'ram', 'disponible_salam')
    search_fields = ('sku', 'phone__model', 'color__name')
    list_editable = ('price', 'stock', 'disponible_salam')
    readonly_fields = ('sku', 'image_preview')
    fields = ('phone', 'color', 'storage', 'ram', 'price', 'stock', 'sku', 'disponible_salam', 'image_preview')
    inlines = [PhoneVariantImageInline]

    def image_preview(self, obj):
        primary_image = obj.primary_image
        if primary_image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', primary_image.image.url)
        return "-"
    image_preview.short_description = 'Aperçu'

    def save_model(self, request, obj, form, change):
        if not obj.sku:
            obj.sku = f"{obj.phone.model}-{obj.color.name}-{obj.storage}GB"
        super().save_model(request, obj, form, change)
