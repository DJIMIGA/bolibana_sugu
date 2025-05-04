from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator
from .models import Supplier
from product.models import Category, Phone
from django.db import models
from django.db.models import Count, Q
from django.contrib.auth.mixins import LoginRequiredMixin


class SupplierListView(ListView):
    
    model = Supplier
    template_name = 'suppliers/supplier_list.html'
    context_object_name = 'suppliers'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')
        
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        return queryset.annotate(
            total_phones=Count('products__phone', distinct=True)
        )


class SupplierDetailView(DetailView):
    model = Supplier
    template_name = 'suppliers/supplier_detail.html'
    context_object_name = 'supplier'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supplier = self.get_object()
        
        # Get all phones for this supplier
        phones = Phone.objects.filter(product__supplier=supplier)
        
        # Get all categories that have phones from this supplier
        categories = Category.objects.filter(
            products__supplier=supplier,
            products__phone__isnull=False
        ).distinct()
        
        context['phones'] = phones
        context['categories'] = categories
        return context
