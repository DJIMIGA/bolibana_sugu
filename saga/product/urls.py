from django.urls import path
from . import views

app_name = 'product'

urlpatterns = [
    path('', views.index, name='index'),
    path('product/<int:product_id>/', views.detail, name='product_detail'),
    path('product/<int:product_id>/review/', views.review, name='review'),
    path('quick-view/<int:product_id>/', views.quick_view, name='quick_view'),
    path('category/', views.category, name='category'),
    path('product-list/', views.product_list, name='product_list'),
    path('search/', views.search, name='search'),
    path('cart/', views.cart, name='cart'),
    path('category-tree/', views.CategoryTreeView.as_view(), name='category_tree'),
    path('category/<int:category_id>/subcategories/', views.category_subcategories, name='category_subcategories'),
    path('category/<int:category_id>/products/', views.CategoryProductsView.as_view(), name='category_products'),
    path('terms-conditions/', views.TermsConditionsView.as_view(), name='terms_conditions'),
    path('cgv/', views.CGVView.as_view(), name='cgv'),
    path('create-product-with-phone/', views.create_product_with_phone, name='create_product_with_phone'),
    path('phones/', views.PhoneListView.as_view(), name='phone_list'),
    path('phone/<int:pk>/', views.PhoneDetailView.as_view(), name='phone_detail'),
    path('add-review/<int:product_id>/', views.add_review, name='add_review'),
    path('get-filtered-phones/', views.get_filtered_phones, name='get_filtered_phones'),
]
