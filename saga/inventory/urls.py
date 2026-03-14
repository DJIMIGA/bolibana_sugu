from django.urls import path
from . import views
from . import category_views

app_name = 'inventory'

urlpatterns = [
    # Vues de synchronisation
    path('sync/products/', views.sync_products, name='sync_products'),
    path('sync/categories/', views.sync_categories, name='sync_categories'),
    path('status/', views.sync_status, name='sync_status'),
    path('api/status/', views.api_sync_status, name='api_sync_status'),
    
    # Vues pour exploiter les catégories synchronisées
    path('categories/', category_views.category_list_synced, name='category_list_synced'),
    path('categories/<slug:category_slug>/', category_views.category_detail_synced, name='category_detail_synced'),
    path('api/categories/tree/', category_views.category_tree_json, name='category_tree_json'),
    path('api/categories/<int:category_id>/products/', category_views.category_products_json, name='category_products_json'),
]
