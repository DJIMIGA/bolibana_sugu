from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('api', views.InventoryAPIViewSet, basename='inventory-api')
router.register('categories', views.CategoryViewSet, basename='inventory-category')
router.register('products', views.ProductViewSet, basename='inventory-product')

urlpatterns = [
    path('', include(router.urls)),
    # URL alternative pour l'endpoint synced (au cas où le router ne la génère pas correctement)
    path('products/synced/', views.synced_products_view, name='inventory-product-synced-alt'),
    path('categories/synced/', views.synced_categories_view, name='inventory-category-synced-alt'),
]
