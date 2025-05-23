from django.contrib import admin
from accounts.admin import admin_site
from .models import Cart, CartItem, Order, OrderItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ('product', 'variant', 'quantity', 'colors', 'sizes')
    can_delete = True

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_key', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__email', 'session_key')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CartItemInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'quantity', 'price')
    readonly_fields = ('price',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'total', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user__email')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at')
    inlines = [OrderItemInline]
    fieldsets = (
        ('Informations de base', {
            'fields': ('user', 'order_number', 'status', 'payment_method', 'is_paid')
        }),
        ('Livraison', {
            'fields': ('shipping_address', 'shipping_method', 'tracking_number')
        }),
        ('Montants', {
            'fields': ('subtotal', 'shipping_cost', 'tax', 'discount', 'total')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes', 'cancellation_reason'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'shipping_address', 'shipping_method'
        )

# Enregistrement avec admin_site
admin_site.register(Cart, CartAdmin)
admin_site.register(Order, OrderAdmin)


