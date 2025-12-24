from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('', views.CartViewSet, basename='cart')

# URLs personnalisées pour les items du panier
urlpatterns = router.urls + [
    path('<int:item_id>/', views.CartViewSet.as_view({
        'patch': 'update',
        'put': 'update',
        'delete': 'destroy'
    }), name='cart-item-detail'),
] 