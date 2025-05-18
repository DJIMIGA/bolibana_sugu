from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.core.paginator import Paginator
from .models import Supplier
from product.models import Category, Phone, Product
from django.db import models
from django.db.models import Count, Q
from django.contrib.auth.mixins import LoginRequiredMixin


class SupplierListView(ListView):
    model = Product
    template_name = 'suppliers/supplier_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_available=True).select_related(
            'phone',
            'phone__color',
            'supplier'
        )
        
        # Appliquer les filtres
        brand = self.request.GET.get('brand')
        model = self.request.GET.get('model')
        storage = self.request.GET.get('storage')
        ram = self.request.GET.get('ram')
        price_min = self.request.GET.get('price_min')
        price_max = self.request.GET.get('price_max')
        
        if brand:
            queryset = queryset.filter(phone__brand=brand)
        if model:
            queryset = queryset.filter(phone__model=model)
        if storage:
            queryset = queryset.filter(phone__storage=storage)
        if ram:
            queryset = queryset.filter(phone__ram=ram)
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        if price_max:
            queryset = queryset.filter(price__lte=price_max)
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Récupérer les produits actifs avec leurs téléphones
        active_products = Product.objects.filter(is_available=True).select_related('phone', 'phone__color')
        
        # Récupérer les marques de téléphones des produits actifs (sans doublons, sans valeurs vides, triées)
        brands_list = list(active_products.values_list('phone__brand', flat=True))
        brands_clean = sorted(set(filter(None, brands_list)))
        context['phone_categories'] = [{'brand': b} for b in brands_clean]
        context['brands'] = [{'phone__brand': b} for b in brands_clean]
        
        # Récupérer les modèles des produits actifs (sans doublons, sans valeurs vides, triés)
        models_list = list(active_products.values_list('phone__model', flat=True))
        models_clean = sorted(set(filter(None, models_list)))
        context['models'] = [{'phone__model': m} for m in models_clean]
        
        # Récupérer les stockages des produits actifs (sans doublons, sans valeurs vides, triés)
        storages_list = list(active_products.values_list('phone__storage', flat=True))
        storages_clean = sorted(set(filter(None, storages_list)))
        context['storages'] = [{'phone__storage': s} for s in storages_clean]
        
        # Récupérer les RAM des produits actifs (sans doublons, sans valeurs vides, triés)
        rams_list = list(active_products.values_list('phone__ram', flat=True))
        rams_clean = sorted(set(filter(None, rams_list)))
        context['rams'] = [{'phone__ram': r} for r in rams_clean]
        
        # Filtres sélectionnés
        context['selected_brand'] = self.request.GET.get('brand', '')
        context['selected_model'] = self.request.GET.get('model', '')
        context['selected_storage'] = self.request.GET.get('storage', '')
        context['selected_ram'] = self.request.GET.get('ram', '')
        context['selected_price_min'] = self.request.GET.get('price_min', '')
        context['selected_price_max'] = self.request.GET.get('price_max', '')
        
        return context

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['suppliers/components/_product_grid.html']
        return [self.template_name]


class BrandDetailView(TemplateView):
    template_name = 'suppliers/supplier_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        brand_slug = kwargs.get('slug')
        
        # Récupérer les produits de cette marque
        products = Product.objects.filter(
            phone__brand__iexact=brand_slug,
            is_available=True
        ).select_related(
            'phone',
            'phone__color',
            'supplier'
        )
        
        # Appliquer les filtres
        model = self.request.GET.get('model')
        storage = self.request.GET.get('storage')
        ram = self.request.GET.get('ram')
        price_min = self.request.GET.get('price_min')
        price_max = self.request.GET.get('price_max')
        
        if model:
            products = products.filter(phone__model=model)
        if storage:
            products = products.filter(phone__storage=storage)
        if ram:
            products = products.filter(phone__ram=ram)
        if price_min:
            products = products.filter(price__gte=price_min)
        if price_max:
            products = products.filter(price__lte=price_max)
        
        # Pagination
        paginator = Paginator(products, 12)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context['products'] = page_obj
        context['page_title'] = f"Téléphones {brand_slug.title()}"
        
        # Filtres disponibles
        context['brands'] = Phone.objects.filter(brand__iexact=brand_slug).values('brand').distinct()
        context['models'] = Phone.objects.filter(brand__iexact=brand_slug).values('model').distinct()
        context['storages'] = Phone.objects.filter(brand__iexact=brand_slug).values('storage').distinct()
        context['rams'] = Phone.objects.filter(brand__iexact=brand_slug).values('ram').distinct()
        
        # Filtres sélectionnés
        context['selected_brand'] = brand_slug
        context['selected_model'] = model
        context['selected_storage'] = storage
        context['selected_ram'] = ram
        context['selected_price_min'] = price_min
        context['selected_price_max'] = price_max
        
        return context

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['suppliers/components/_product_grid.html']
        return [self.template_name]
