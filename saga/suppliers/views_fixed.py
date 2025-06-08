from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.core.paginator import Paginator
from .models import Supplier
from product.models import Category, Phone, Product, Clothing, CulturalItem
from django.db import models
from django.db.models import Count, Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg
from product.forms import ReviewForm
from django.http import Http404
import logging
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify

logger = logging.getLogger(__name__)

# ... existing code ...

class BrandDetailView(TemplateView):
    template_name = 'suppliers/brand_detail.html'

    def get_queryset(self):
        brand = self.kwargs.get('brand')
        if not brand:
            logger.error("Aucune marque fournie")
            raise Http404("Marque non trouvée")
            
        logger.info(f"Recherche des produits de la marque: {brand}")
        
        # Récupérer toutes les marques disponibles pour le debug
        all_brands = Product.objects.filter(
            is_available=True,
            is_salam=True
        ).values_list('phone__brand', flat=True).distinct()
        logger.info(f"Marques disponibles dans la base de données: {list(all_brands)}")
        
        # Récupérer les produits de cette marque (insensible à la casse)
        queryset = Product.objects.filter(
            phone__brand__iexact=brand,
            is_available=True,
            is_salam=True
        ).select_related(
            'phone',
            'phone__color',
            'supplier'
        )
        
        logger.info(f"Nombre de produits trouvés pour la marque {brand}: {queryset.count()}")
        
        # Appliquer les filtres
        model = self.request.GET.get('model')
        storage = self.request.GET.get('storage')
        ram = self.request.GET.get('ram')
        price_min = self.request.GET.get('price_min')
        price_max = self.request.GET.get('price_max')
        
        if model:
            queryset = queryset.filter(phone__model=model)
            logger.info(f"Filtre par modèle: {model}")
        if storage:
            queryset = queryset.filter(phone__storage=storage)
            logger.info(f"Filtre par stockage: {storage}")
        if ram:
            queryset = queryset.filter(phone__ram=ram)
            logger.info(f"Filtre par RAM: {ram}")
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
            logger.info(f"Filtre par prix minimum: {price_min}")
        if price_max:
            queryset = queryset.filter(price__lte=price_max)
            logger.info(f"Filtre par prix maximum: {price_max}")
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        brand = self.kwargs.get('brand')
        
        if not brand:
            logger.error("Aucune marque fournie dans le contexte")
            raise Http404("Marque non trouvée")
        
        logger.info(f"Préparation du contexte pour la marque: {brand}")
        
        try:
            # Récupérer les produits avec les filtres
            products = self.get_queryset()
            
            if not products.exists():
                logger.warning(f"Aucun produit trouvé pour la marque {brand}")
                raise Http404(f"Aucun produit trouvé pour la marque {brand}")
            
            # Pagination
            paginator = Paginator(products, 12)
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            context['products'] = page_obj
            context['brand'] = brand
            context['page_title'] = f"Téléphones {brand}"
            
            # Récupérer les produits actifs avec leurs téléphones pour les filtres
            active_products = Product.objects.filter(
                phone__brand__iexact=brand,
                is_available=True,
                is_salam=True
            ).select_related('phone', 'phone__color')
            
            logger.info(f"Nombre de produits actifs pour les filtres: {active_products.count()}")
            
            # Récupérer les modèles des produits actifs
            models_list = list(active_products.values_list('phone__model', flat=True))
            models_clean = sorted(set(filter(None, models_list)))
            context['models'] = [{'phone__model': m} for m in models_clean]
            logger.info(f"Modèles disponibles: {models_clean}")
            
            # Récupérer les stockages des produits actifs
            storages_list = list(active_products.values_list('phone__storage', flat=True))
            storages_clean = sorted(set(filter(None, storages_list)))
            context['storages'] = [{'phone__storage': s} for s in storages_clean]
            logger.info(f"Stockages disponibles: {storages_clean}")
            
            # Récupérer les RAM des produits actifs
            rams_list = list(active_products.values_list('phone__ram', flat=True))
            rams_clean = sorted(set(filter(None, rams_list)))
            context['rams'] = [{'phone__ram': r} for r in rams_clean]
            logger.info(f"RAM disponibles: {rams_clean}")
            
            # Filtres sélectionnés
            context['selected_brand'] = brand
            context['selected_model'] = self.request.GET.get('model', '')
            context['selected_storage'] = self.request.GET.get('storage', '')
            context['selected_ram'] = self.request.GET.get('ram', '')
            context['selected_price_min'] = self.request.GET.get('price_min', '')
            context['selected_price_max'] = self.request.GET.get('price_max', '')
            
            # Ajouter la marque pour le template de filtres
            context['brands'] = [{'phone__brand': brand}]
            
            logger.info("Contexte préparé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de la préparation du contexte: {str(e)}")
            raise
        
        return context

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['suppliers/components/_product_grid.html']
        return [self.template_name]

# ... rest of the code ... 