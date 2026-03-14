from django.urls import path
from . import views

app_name = 'product'

urlpatterns = [
    # URLs à supprimer progressivement (commentées pour vérification)
    # path('', views.index, name='index'),
    # path('product/<int:product_id>/', views.detail, name='product_detail'),
    # path('product/<int:product_id>/review/', views.review, name='review'),
    # path('quick-view/<int:product_id>/', views.quick_view, name='quick_view'),
    # path('category/', views.category, name='category'),
    # path('product-list/', views.product_list, name='product_list'),
    # path('search/', views.search, name='search'),
    # path('cart/', views.cart, name='cart'),
    # path('category-tree/', views.category_tree, name='category_tree'),
    # path('category/<int:category_id>/subcategories/', views.category_subcategories, name='category_subcategories'),
    # path('category/<int:category_id>/products/', views.category_products, name='category_products'),
    # path('phones/', views.phone_list, name='phone_list'),
    # path('phone/<int:phone_id>/', views.phone_detail, name='phone_detail'),
    # path('product/<int:product_id>/add-review/', views.add_review, name='add_review'),
    # path('api/phones/filtered/', views.get_filtered_phones, name='get_filtered_phones'),
    # path('create-product-with-phone/', views.create_product_with_phone, name='create_product_with_phone'),
]
