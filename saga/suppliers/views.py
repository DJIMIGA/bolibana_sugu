from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, DetailView
from .models import Supplier
from product.models import Category


class SupplierListView(ListView):
    
    model = Supplier
    template_name = 'suppliers/suppliers_list.html'
    context_object_name = 'suppliers'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Récupérer les catégories de téléphones (sous-catégories de la catégorie "Téléphones")
        phone_category = Category.objects.get(name='Téléphones')
        context['phone_categories'] = phone_category.children.all()
        return context


class SupplierDetailView(DetailView):
    model = Supplier
    template_name = 'suppliers/supplier_detail.html'
    context_object_name = 'supplier'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = self.object.products.all()
        return context
