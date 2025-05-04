from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from .views import create_product_with_phone

app_name = 'product'

urlpatterns = [
    # Routes principales
    path('', views.product_list, name='product_list'),
    path('search/', views.search, name='search'),
    
    # Routes pour les produits
    path('product/<int:product_id>/', views.detail, name='product_detail'),
    path('quick_view/<int:product_id>/', views.quick_view, name='product_quick_view'),
    path('review/<int:product_id>/', views.add_review, name='add_review'),
    path('create-product-with-phone/', create_product_with_phone, name='create_product_with_phone'),
    
    # Routes pour les catégories
    path('category/', views.category, name='category'),
    path('categories/', views.CategoryTreeView.as_view(), name='category_tree'),
    path('categories/<int:category_id>/subcategories/', views.category_subcategories, name='category_subcategories'),
    path('category/<int:category_id>/', views.CategoryProductsView.as_view(), name='category_products'),
    
    # Routes pour les téléphones
    path('phones/', views.PhoneListView.as_view(), name='phone_list'),
    path('phones/<int:pk>/', views.PhoneDetailView.as_view(), name='phone_detail'),
    path('phones/filter/', views.get_filtered_phones, name='get_filtered_phones'),
    
    # Routes légales
    path('terms-conditions/', views.TermsConditionsView.as_view(), name='terms_conditions'),
    path('cgv/', views.CGVView.as_view(), name='cgv'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
