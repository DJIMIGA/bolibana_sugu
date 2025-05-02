from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from .views import create_product_with_phone


urlpatterns = [
    path('', views.index, name='product_index'),
    path('search/', views.search, name='search'),
    path('product/<int:product_id>/', views.detail, name='product_detail'),
    path('review/<int:product_id>/', views.review, name='review'),
    path('quick_view/<int:product_id>/', views.quick_view, name='product_quick_view'),
    path('category/', views.category, name='category'),
    path('product_list/', views.product_list, name='product_list'),
    path('categories/', views.CategoryTreeView.as_view(), name='category_tree'),
    path('categories/<int:category_id>/subcategories/', views.category_subcategories, name='category_subcategories'),
    path('category/<int:category_id>/', views.CategoryProductsView.as_view(), name='category_products'),
    path('terms-conditions/', views.TermsConditionsView.as_view(), name='terms_conditions'),
    path('cgv/', views.CGVView.as_view(), name='cgv'),
    path('create-product-with-phone/', create_product_with_phone, name='create_product_with_phone'),
    path('phones/', views.PhoneListView.as_view(), name='phone_list'),
    path('phones/<int:phone_id>/', views.phone_detail, name='phone_detail'),
    path('api/variants/<int:variant_id>/images/', views.get_variant_images, name='variant_images'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
