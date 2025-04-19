from django.contrib import admin

# Register your models here.
from .models import Shopper, ShippingAddress
from cart.models import Order, OrderItem

    
admin.site.register(Shopper)
admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(OrderItem)