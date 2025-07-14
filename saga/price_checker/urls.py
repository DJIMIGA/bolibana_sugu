from django.urls import path
from django.conf import settings
from . import views

app_name = 'price_checker'

# URLs publiques
public_urls = [
    path('check_price/', views.check_price, name='check_price'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('submit/', views.PriceSubmissionCreateView.as_view(), name='price_submission_create'),
    path('submissions/', views.PriceSubmissionListView.as_view(), name='price_submission_list'),
    path('submissions/<int:pk>/update/', views.PriceSubmissionUpdateView.as_view(), name='price_submission_update'),
    path('submissions/<int:pk>/delete/', views.PriceSubmissionDeleteView.as_view(), name='price_submission_delete'),
    path('dashboard/', views.UserDashboardView.as_view(), name='user_dashboard'),
]

# URLs admin
admin_urls = [
    path(settings.ADMIN_URL, views.AdminDashboardView.as_view(), name='admin_dashboard'),
    
    # Gestion des soumissions
    path(f'{settings.ADMIN_URL}submissions/', views.AdminPriceSubmissionListView.as_view(), name='admin_price_submission_list'),
    path(f'{settings.ADMIN_URL}submissions/<int:pk>/approve/', views.approve_price_submission, name='admin_price_submission_approve'),
    path(f'{settings.ADMIN_URL}submissions/<int:pk>/reject/', views.reject_price_submission, name='admin_price_submission_reject'),
    
    # Gestion des prix
    path(f'{settings.ADMIN_URL}prices/', views.AdminPriceEntryListView.as_view(), name='admin_price_entry_list'),
    
    # Gestion des produits
    path(f'{settings.ADMIN_URL}products/', views.AdminProductStatusListView.as_view(), name='admin_product_status_list'),
    path(f'{settings.ADMIN_URL}products/<int:pk>/toggle/', views.toggle_product_status, name='admin_toggle_product_status'),
    
    # Gestion des villes
    path(f'{settings.ADMIN_URL}cities/', views.AdminCityListView.as_view(), name='admin_city_list'),
    path(f'{settings.ADMIN_URL}cities/add/', views.add_city, name='admin_add_city'),
    path(f'{settings.ADMIN_URL}cities/<int:pk>/update/', views.update_city, name='admin_update_city'),
    path(f'{settings.ADMIN_URL}cities/<int:pk>/delete/', views.delete_city, name='admin_delete_city'),
]

# URLs API
api_urls = [
    path('api/products/', views.get_products_by_brand, name='api_products'),
    path('api/product-details/', views.get_product_details, name='api_product_details'),
    path('api/product-prices/', views.get_product_prices, name='api_product_prices'),
]

# Combinaison de toutes les URLs
urlpatterns = public_urls + admin_urls + api_urls 