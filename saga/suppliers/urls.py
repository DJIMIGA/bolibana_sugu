from django.urls import path
from .views import SupplierListView, BrandDetailView, CategoryDetailView

app_name = 'suppliers'

urlpatterns = [
    path('', SupplierListView.as_view(), name='supplier_index'),
    path('<slug:slug>/', BrandDetailView.as_view(), name='supplier_detail'),
    path('categorie/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
]
