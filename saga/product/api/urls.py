from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views
# product api urls 
router = DefaultRouter()

router.register('products', views.ProductViewSet, basename='product')
router.register('categories', views.CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
] 