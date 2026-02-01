from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('', views.CartViewSet, basename='cart')

# URLs personnalisées pour les items du panier
# Le router Django REST Framework utilise 'pk' comme nom de paramètre
urlpatterns = router.urls + [
    path('orders/', views.CartViewSet.as_view({
        'get': 'orders'
    }), name='cart-orders'),
    path('orders/<int:order_id>/', views.CartViewSet.as_view({
        'get': 'order_detail'
    }), name='cart-order-detail'),
    path('<int:pk>/', views.CartViewSet.as_view({
        'patch': 'update',
        'put': 'update',
        'delete': 'destroy'
    }), name='cart-item-detail'),
] 