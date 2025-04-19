from django.contrib import admin

# Register your models here.
from .models import Product, Category, ImageProduct, Review, Size, Color, Clothing, CulturalItem, ShippingMethod
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline

admin.site.register(Size)
admin.site.register(Product)
admin.site.register(Color)
admin.site.register(ShippingMethod)

admin.site.register(Category)
admin.site.register(ImageProduct)
admin.site.register(Review)
admin.site.register(Clothing)
admin.site.register(CulturalItem)
