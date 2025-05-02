from django.urls import path
from .views import SupplierDetailView, SupplierListView

urlpatterns = [
    path('', SupplierListView.as_view(), name='supplier_index'),
    path('<str:brand>/', SupplierDetailView.as_view(), name='supplier_detail'),
]
