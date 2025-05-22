from django.contrib import admin
import logging

# Register your models here.
from .models import Shopper, ShippingAddress
from cart.models import Order, OrderItem

# Configuration du logger
logger = logging.getLogger('accounts.admin')

class ShopperAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        logger.debug(f"=== OTP DEBUG INFO ===")
        logger.debug(f"User: {request.user.email}")
        logger.debug(f"OTP verified: {request.user.is_verified()}")
        logger.debug(f"User is authenticated: {request.user.is_authenticated}")
        logger.debug(f"User is staff: {request.user.is_staff}")
        logger.debug(f"User is superuser: {request.user.is_superuser}")
        logger.debug(f"====================")
        return super().has_module_permission(request)

admin.site.register(Shopper, ShopperAdmin)
admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(OrderItem)