from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator
from .models import Supplier
from product.models import Category, Phone, PhoneVariant
from django.db import models


class SupplierListView(ListView):
    
    model = Supplier
    template_name = 'suppliers/suppliers_list.html'
    context_object_name = 'suppliers'
    paginate_by = 12  # Nombre d'éléments par page

    def get_queryset(self):
        if self.request.headers.get('HX-Request'):
            return Supplier.objects.none()
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        if self.request.headers.get('HX-Request'):
            return {}
        context = super().get_context_data(**kwargs)
        
        # Récupérer les marques distinctes des téléphones avec leur nombre
        brands = Phone.objects.values('brand').annotate(
            phone_count=models.Count('id')
        ).order_by('brand')
        context['phone_categories'] = brands
        
        # Récupérer les variantes de téléphones disponibles en Salam
        variants = PhoneVariant.objects.select_related(
            'phone',
            'color'
        ).prefetch_related(
            'images'
        ).filter(
            disponible_salam=True
        ).order_by('phone__brand', 'phone__model', 'storage', 'ram')
        
        # Pagination des variantes
        variants_paginator = Paginator(variants, self.paginate_by)
        variants_page_number = self.request.GET.get('variants_page', 1)
        try:
            variants_page_obj = variants_paginator.page(variants_page_number)
        except:
            variants_page_obj = variants_paginator.page(1)
        
        # Variables de pagination
        context['variants'] = variants_page_obj
        context['page_obj'] = variants_page_obj
        context['is_paginated'] = variants_page_obj.paginator.num_pages > 1
        
        # Variables de filtrage
        context['selected_brand'] = self.request.GET.get('brand')
        context['selected_model'] = self.request.GET.get('model')
        context['selected_storage'] = self.request.GET.get('storage')
        context['selected_ram'] = self.request.GET.get('ram')
        context['selected_price_min'] = self.request.GET.get('price_min')
        context['selected_price_max'] = self.request.GET.get('price_max')
        
        # Variables pour les filtres
        context['brands'] = Phone.objects.values('brand').distinct().order_by('brand')
        context['models'] = Phone.objects.values('model').distinct().order_by('model')
        context['storages'] = PhoneVariant.objects.values('storage').distinct().order_by('storage')
        context['rams'] = PhoneVariant.objects.values('ram').distinct().order_by('ram')
        
        return context


class SupplierDetailView(DetailView):
    model = Supplier
    template_name = 'suppliers/supplier_detail.html'
    slug_field = 'brand'
    slug_url_kwarg = 'brand'
    paginate_by = 12  # Nombre d'éléments par page

    def get_object(self, queryset=None):
        brand = self.kwargs.get('brand')
        return Phone.objects.filter(brand=brand).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        brand = self.kwargs.get('brand')
        
        # Récupérer les variantes de téléphones pour cette marque
        variants = PhoneVariant.objects.select_related(
            'phone',
            'color'
        ).prefetch_related(
            'images'
        ).filter(
            phone__brand=brand
        ).order_by('phone__model', 'storage', 'ram')
        
        # Pagination des variantes
        variants_paginator = Paginator(variants, self.paginate_by)
        variants_page_number = self.request.GET.get('variants_page', 1)
        try:
            variants_page_obj = variants_paginator.page(variants_page_number)
        except:
            variants_page_obj = variants_paginator.page(1)
        
        # Variables de pagination
        context['variants'] = variants_page_obj
        context['page_obj'] = variants_page_obj
        context['is_paginated'] = variants_page_obj.paginator.num_pages > 1
        
        # Variables de filtrage
        context['selected_brand'] = brand
        context['selected_model'] = self.request.GET.get('model')
        context['selected_storage'] = self.request.GET.get('storage')
        context['selected_ram'] = self.request.GET.get('ram')
        context['selected_price_min'] = self.request.GET.get('price_min')
        context['selected_price_max'] = self.request.GET.get('price_max')
        
        # Variables pour les filtres
        context['brands'] = Phone.objects.values('brand').distinct().order_by('brand')
        context['models'] = Phone.objects.filter(brand=brand).values('model').distinct().order_by('model')
        context['storages'] = variants.values('storage').distinct().order_by('storage')
        context['rams'] = variants.values('ram').distinct().order_by('ram')
        
        context['brand'] = brand
        context['page_title'] = f"Nos {brand}"
        
        return context
