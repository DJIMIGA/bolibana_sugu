from django.urls import path
from .category_views import CategoryViewFactory
from . import views

app_name = 'suppliers'

urlpatterns = [
    path('', views.SupplierListView.as_view(), name='supplier_index'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('brand/<str:brand>/', views.BrandDetailView.as_view(), name='brand_detail'),
    path('category/<slug:slug>/', CategoryViewFactory.get_view, name='category_detail'),
    path('category-tree/', views.category_tree, name='category_tree'),
    path('category/<int:category_id>/subcategories/', views.category_subcategories, name='category_subcategories'),
    
    # URLs pour les différents types de produits
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('phone/<slug:slug>/', views.PhoneDetailView.as_view(), name='phone_detail'),
    path('clothing/<slug:slug>/', views.ClothingDetailView.as_view(), name='clothing_detail'),
    path('fabric/<slug:slug>/', views.FabricDetailView.as_view(), name='fabric_detail'),
    # Garder les deux URLs pour la compatibilité
    path('cultural/<slug:slug>/', views.CulturalItemDetailView.as_view(), name='cultural_detail'),
    path('articles-culturels/<slug:slug>/', views.CulturalItemDetailView.as_view(), name='cultural_detail'),
    path('product/<slug:slug>/review/', views.add_review, name='add_review'),
    path('favorites/', views.FavoriteListView.as_view(), name='favorite_list'),
    path('favorites/<int:product_id>/', views.toggle_favorite, name='toggle_favorite'),
    
    # URLs de recherche optimisées
    path('search/', views.search, name='search'),
    path('search/suggestions/', views.search_suggestions, name='search_suggestions'),
    path('search/results/', views.search_results_page, name='search_results_page'),
    # Nouvelle URL optimisée avec slug
    path('recherche/<slug:search_term>/', views.search_by_slug, name='search_by_slug'),

    path('product-list/', views.SupplierListView.as_view(), name='product_list'),
]
