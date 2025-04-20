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
        # Récupérer la catégorie "Téléphones" la plus récente
        phone_category = Category.objects.filter(name='Téléphones').order_by('-id').first()
        if phone_category:
            context['phone_categories'] = phone_category.children.all()
        else:
            context['phone_categories'] = []
        return context


class SupplierDetailView(DetailView):
    model = Supplier
    template_name = 'suppliers/supplier_detail.html'
    context_object_name = 'supplier'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = self.object.products.all()
        return context
