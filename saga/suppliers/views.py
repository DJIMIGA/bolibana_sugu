from django.shortcuts import render, get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.generic import ListView, DetailView, TemplateView
from django.core.paginator import Paginator
from .models import Supplier, Hero, HeroImage
from product.models import Category, Phone, Product, Clothing, CulturalItem, Review, Favorite
from django.db import models
from django.db.models import Count, Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg
from product.forms import ReviewForm
from django.http import Http404, HttpResponse, JsonResponse
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.cache import cache
from django.template.loader import render_to_string
import json
import logging
import re
import unicodedata
from core.utils import track_search

logger = logging.getLogger(__name__)

def normalize_search_term(term):
    """
    Normalise un terme de recherche pour ignorer les accents et la casse.
    Exemple: 'telephones' -> 'telephones', 'Téléphones' -> 'telephones'
    """
    if not term:
        return ''
    
    # Convertir en minuscules
    term = term.lower()
    
    # Normaliser les caractères Unicode (supprimer les accents)
    term = unicodedata.normalize('NFD', term)
    term = ''.join(c for c in term if not unicodedata.combining(c))
    
    return term

def create_search_query(term):
    """
    Recherche multi-mots avec logique ET et recherche permissive.
    Permet de trouver "Bazin Super Riche1" quand on tape "bazin supp"
    """
    if not term or not term.strip():
        return Q()
    
    words = [normalize_search_term(word) for word in term.strip().split() if word.strip()]
    if not words:
        return Q()
    
    query = Q()
    for word in words:
        # Recherche permissive : le mot dans le produit doit contenir le terme saisi
        word_query = (
            Q(title__icontains=word) |
            Q(description__icontains=word) |
            Q(category__name__icontains=word) |
            Q(brand__icontains=word)
        )
        
        # Recherche par préfixe pour plus de flexibilité
        word_query |= (
            Q(title__istartswith=word) |
            Q(description__istartswith=word) |
            Q(category__name__istartswith=word) |
            Q(brand__istartswith=word)
        )
        
        # Recherche par suffixe pour capturer les mots qui se terminent par le terme
        word_query |= (
            Q(title__iendswith=word) |
            Q(description__iendswith=word) |
            Q(category__name__iendswith=word) |
            Q(brand__iendswith=word)
        )
        
        query &= word_query
    
    return query


class SupplierListView(ListView):
    model = Product
    template_name = 'suppliers/supplier_list.html'
    context_object_name = 'products'
    paginate_by = 12
    def get_queryset(self):
        queryset = Product.objects.filter(
            is_available=True
        ).select_related(
            'phone',
            'phone__color',
            'supplier',
            'category',
            'fabric_product',
            'clothing_product',
            'cultural_product'
        ).prefetch_related(
            'clothing_product__size',
            'clothing_product__color',
            'fabric_product__color',
            'images'
        )

        # Appliquer les filtres selon le type de produit
        product_type = self.request.GET.get('type')
        if product_type:
            if product_type == 'phone':
                queryset = queryset.filter(phone__isnull=False)
            elif product_type == 'clothing':
                queryset = queryset.filter(clothing_product__isnull=False)
            elif product_type == 'fabric':
                queryset = queryset.filter(fabric_product__isnull=False)
            elif product_type == 'cultural':
                queryset = queryset.filter(cultural_product__isnull=False)

        # Filtres spécifiques aux téléphones
        if not product_type or product_type == 'phone':
            brand = self.request.GET.get('brand')
            model = self.request.GET.get('model')
            storage = self.request.GET.get('storage')
            ram = self.request.GET.get('ram')

            if brand:
                queryset = queryset.filter(phone__brand=brand)
            if model:
                queryset = queryset.filter(phone__model=model)
            if storage:
                queryset = queryset.filter(phone__storage=storage)
            if ram:
                queryset = queryset.filter(phone__ram=ram)

        # Filtres spécifiques aux vêtements
        if not product_type or product_type == 'clothing':
            gender = self.request.GET.get('gender')
            size = self.request.GET.get('size')
            color = self.request.GET.get('color')
            material = self.request.GET.get('material')
            style = self.request.GET.get('style')
            season = self.request.GET.get('season')

            if gender:
                queryset = queryset.filter(clothing_product__gender=gender)
            if size:
                queryset = queryset.filter(clothing_product__size__name=size)
            if color:
                queryset = queryset.filter(clothing_product__color__name=color)
            if material:
                queryset = queryset.filter(clothing_product__material=material)
            if style:
                queryset = queryset.filter(clothing_product__style=style)
            if season:
                queryset = queryset.filter(clothing_product__season=season)

        # Filtres spécifiques aux tissus
        if not product_type or product_type == 'fabric':
            fabric_type = self.request.GET.get('fabric_type')
            fabric_color = self.request.GET.get('fabric_color')
            quality = self.request.GET.get('quality')

            if fabric_type:
                queryset = queryset.filter(fabric_product__fabric_type=fabric_type)
            if fabric_color:
                queryset = queryset.filter(fabric_product__color__name=fabric_color)
            if quality:
                queryset = queryset.filter(fabric_product__quality=quality)

        # Filtres spécifiques aux produits culturels
        if not product_type or product_type == 'cultural':
            author = self.request.GET.get('author')
            isbn = self.request.GET.get('isbn')
            date = self.request.GET.get('date')

            if author:
                queryset = queryset.filter(cultural_product__author__icontains=author)
            if isbn:
                queryset = queryset.filter(cultural_product__isbn=isbn)
            if date:
                queryset = queryset.filter(cultural_product__date=date)

        # Filtres communs
        price_min = self.request.GET.get('price_min')
        price_max = self.request.GET.get('price_max')
        
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        if price_max:
            queryset = queryset.filter(price__lte=price_max)
        
        logger.info(f"Nombre de produits récupérés: {queryset.count()}")
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        logger.info("\n=== SUPPLIER LIST VIEW - GET_CONTEXT_DATA ===")
        context = super().get_context_data(**kwargs)
        
        # Récupérer le hero actif avec ses images actives uniquement
        hero = Hero.objects.filter(is_active=True).first()
        
        if hero:
            # Récupérer les 3 premières images actives et ordonnées
            context['hero_images'] = hero.images.filter(
                is_active=True
            ).order_by('ordre').distinct()[:3]
            logger.info(f"Hero trouvé: {hero.title} avec {context['hero_images'].count()} images")
            
        context['hero'] = hero

        # Récupérer les catégories principales
        main_categories = Category.objects.filter(
            is_main=True,
            parent__isnull=True
        ).prefetch_related(
            'children',
            'products'
        ).annotate(
            available_products_count=Count('products', filter=Q(products__is_available=True))
        ).order_by('order', 'name')
        
        context['main_categories'] = main_categories
        logger.info(f"Nombre de catégories principales: {main_categories.count()}")
        for cat in main_categories:
            logger.info(f"Catégorie: {cat.name} (slug: {cat.slug})")
            logger.info(f"Nombre de produits: {cat.available_products_count}")
            logger.info(f"Sous-catégories: {[child.name for child in cat.children.all()]}")
            logger.info("---")

        # Récupérer les produits actifs avec leurs relations
        active_products = Product.objects.filter(
            is_available=True
        ).select_related(
            'phone',
            'phone__color',
            'clothing_product',
            'fabric_product',
            'cultural_product'
        ).prefetch_related(
            'clothing_product__size',
            'clothing_product__color',
            'fabric_product__color'
        )

        # Log détaillé des vêtements
        clothing_products = active_products.filter(clothing_product__isnull=False)
        logger.info("\n=== VÊTEMENTS ===")
        logger.info(f"Nombre total de vêtements: {clothing_products.count()}")
        for product in clothing_products:
            logger.info(f"Vêtement: {product.title} (ID: {product.id})")
            logger.info(f"Catégorie: {product.category.name if product.category else 'Pas de catégorie'}")
            logger.info(f"Disponible: {product.is_available}")
            logger.info(f"Salam: {product.is_salam}")
            logger.info("---")

        # Filtres pour les téléphones
        context['phone_categories'] = [{'brand': b} for b in sorted(filter(None, active_products.filter(phone__isnull=False).values_list('phone__brand', flat=True).distinct()))]
        context['brands'] = [{'phone__brand': b} for b in sorted(filter(None, active_products.filter(phone__isnull=False).values_list('phone__brand', flat=True).distinct()))]
        context['models'] = [{'phone__model': m} for m in sorted(filter(None, active_products.filter(phone__isnull=False).values_list('phone__model', flat=True).distinct()))]
        context['storages'] = [{'phone__storage': s} for s in sorted(filter(None, active_products.filter(phone__isnull=False).values_list('phone__storage', flat=True).distinct()))]
        context['rams'] = [{'phone__ram': r} for r in sorted(filter(None, active_products.filter(phone__isnull=False).values_list('phone__ram', flat=True).distinct()))]

        # Filtres pour les vêtements
        context['genders'] = [{'clothing_product__gender': g} for g in sorted(filter(None, active_products.filter(clothing_product__isnull=False).values_list('clothing_product__gender', flat=True).distinct()))]
        context['sizes'] = [{'clothing_product__size': s} for s in sorted(filter(None, active_products.filter(clothing_product__isnull=False).values_list('clothing_product__size', flat=True).distinct()))]
        context['clothing_colors'] = [{'clothing_product__color__name': c} for c in sorted(filter(None, active_products.filter(clothing_product__isnull=False).values_list('clothing_product__color__name', flat=True).distinct()))]
        context['materials'] = [{'clothing_product__material': m} for m in sorted(filter(None, active_products.filter(clothing_product__isnull=False).values_list('clothing_product__material', flat=True).distinct()))]
        context['styles'] = [{'clothing_product__style': s} for s in sorted(filter(None, active_products.filter(clothing_product__isnull=False).values_list('clothing_product__style', flat=True).distinct()))]
        context['seasons'] = [{'clothing_product__season': s} for s in sorted(filter(None, active_products.filter(clothing_product__isnull=False).values_list('clothing_product__season', flat=True).distinct()))]

        # Filtres pour les tissus
        context['fabric_types'] = [{'fabric_product__fabric_type': t} for t in sorted(filter(None, active_products.filter(fabric_product__isnull=False).values_list('fabric_product__fabric_type', flat=True).distinct()))]
        context['fabric_colors'] = [{'fabric_product__color__name': c} for c in sorted(filter(None, active_products.filter(fabric_product__isnull=False).values_list('fabric_product__color__name', flat=True).distinct()))]
        context['qualities'] = [{'fabric_product__quality': q} for q in sorted(filter(None, active_products.filter(fabric_product__isnull=False).values_list('fabric_product__quality', flat=True).distinct()))]

        # Filtres pour les produits culturels
        context['authors'] = [{'cultural_product__author': a} for a in sorted(filter(None, active_products.filter(cultural_product__isnull=False).values_list('cultural_product__author', flat=True).distinct()))]
        context['isbns'] = [{'cultural_product__isbn': i} for i in sorted(filter(None, active_products.filter(cultural_product__isnull=False).values_list('cultural_product__isbn', flat=True).distinct()))]
        context['dates'] = [{'cultural_product__date': d} for d in sorted(filter(None, active_products.filter(cultural_product__isnull=False).values_list('cultural_product__date', flat=True).distinct()))]

        # Filtres sélectionnés
        context['selected_brand'] = self.request.GET.get('brand', '')
        context['selected_model'] = self.request.GET.get('model', '')
        context['selected_storage'] = self.request.GET.get('storage', '')
        context['selected_ram'] = self.request.GET.get('ram', '')
        context['selected_gender'] = self.request.GET.get('gender', '')
        context['selected_size'] = self.request.GET.get('size', '')
        context['selected_color'] = self.request.GET.get('color', '')
        context['selected_material'] = self.request.GET.get('material', '')
        context['selected_style'] = self.request.GET.get('style', '')
        context['selected_season'] = self.request.GET.get('season', '')
        context['selected_fabric_type'] = self.request.GET.get('fabric_type', '')
        context['selected_fabric_color'] = self.request.GET.get('fabric_color', '')
        context['selected_quality'] = self.request.GET.get('quality', '')
        context['selected_author'] = self.request.GET.get('author', '')
        context['selected_isbn'] = self.request.GET.get('isbn', '')
        context['selected_date'] = self.request.GET.get('date', '')
        context['selected_price_min'] = self.request.GET.get('price_min', '')
        context['selected_price_max'] = self.request.GET.get('price_max', '')
        
        # Récupérer le queryset complet avant pagination
        products = self.get_queryset()
        logger.info("\n=== PRODUITS ===")
        logger.info(f"Nombre total de produits: {products.count()}")
        
        # Compter les produits par type
        phone_count = products.filter(phone__isnull=False).count()
        clothing_count = products.filter(clothing_product__isnull=False).count()
        fabric_count = products.filter(fabric_product__isnull=False).count()
        cultural_count = products.filter(cultural_product__isnull=False).count()
        
        logger.info(f"Nombre de téléphones: {phone_count}")
        logger.info(f"Nombre de vêtements: {clothing_count}")
        logger.info(f"Nombre de tissus: {fabric_count}")
        logger.info(f"Nombre de produits culturels: {cultural_count}")

        # Récupérer les produits en promotion (avec discount_price)
        promotional_products = active_products.filter(
            discount_price__isnull=False,
            discount_price__gt=0
        ).order_by('-created_at')[:8]
        
        logger.info(f"Nombre de produits en promotion: {promotional_products.count()}")

        # Ajouter les produits par type au contexte
        context['products'] = products  # Tous les produits
        context['phone_products'] = products.filter(phone__isnull=False)[:4]
        context['clothing_products'] = products.filter(clothing_product__isnull=False)[:4]
        context['fabric_products'] = products.filter(fabric_product__isnull=False)[:4]
        context['cultural_products'] = products.filter(cultural_product__isnull=False)[:4]
        context['promotional_products'] = promotional_products
        
        # Log des produits ajoutés au contexte
        logger.info("\n=== PRODUITS DANS LE CONTEXTE ===")
        logger.info(f"Nombre de produits totaux: {len(context['products'])}")
        logger.info(f"Nombre de vêtements: {len(context['clothing_products'])}")
        for product in context['clothing_products']:
            logger.info(f"Vêtement dans le contexte: {product.title}")
        
        return context

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['suppliers/components/_product_grid.html']
        return [self.template_name]


class BrandDetailView(TemplateView):
    template_name = 'suppliers/brand_detail.html'

    def get_queryset(self):
        brand = self.kwargs.get('brand')
        if not brand:
            logger.error("Aucune marque fournie")
            raise Http404("Marque non trouvée")
            
        logger.info(f"Recherche des produits de la marque: {brand}")
        
        # Récupérer les produits de cette marque (insensible à la casse)
        queryset = Product.objects.filter(
            phone__brand__iexact=brand,
            is_available=True
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
        
        logger.info(f"Nombre final de produits après filtres: {queryset.count()}")
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        brand = kwargs.get('brand')
        
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
            
            logger.info("Contexte préparé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de la préparation du contexte: {str(e)}")
            raise
        
        return context

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['suppliers/components/_product_grid.html']
        return [self.template_name]


class CategoryDetailView(TemplateView):
    template_name = 'suppliers/category_detail.html'

    def get_queryset(self):
        category_slug = self.kwargs.get('slug')
        category = get_object_or_404(Category, slug=category_slug)
        
        # Base queryset pour tous les produits disponibles et actifs
        queryset = Product.objects.filter(
            is_available=True
        ).select_related(
            'phone',
            'phone__color',
            'supplier',
            'category',
            'fabric_product',
            'clothing_product',
            'cultural_product'
        )
        
        # Si c'est la catégorie "Tous les produits", récupérer les produits de toutes les catégories principales
        if category.slug == 'tous-les-produits':
            main_categories = Category.objects.filter(
                is_main=True,
                parent__isnull=True
            ).exclude(slug='tous-les-produits')
            
            # Récupérer tous les IDs des catégories principales et leurs enfants
            category_ids = []
            for main_cat in main_categories:
                category_ids.extend(main_cat.get_all_children_ids())
                category_ids.append(main_cat.id)
            
            queryset = queryset.filter(category_id__in=category_ids)
        else:
            # Si ce n'est pas "Tous les produits", filtrer par catégorie spécifique
            child_ids = list(category.get_all_children_ids())
            parent_ids = list(category.get_all_parent_ids())
            category_ids = set([category.id] + child_ids + parent_ids)
            queryset = queryset.filter(category_id__in=category_ids)
            
            # Appliquer les filtres selon le type de catégorie
            if category.slug == 'tissus':
                queryset = queryset.filter(fabric_product__isnull=False)
            elif category.slug == 'vetements' or category.parent and category.parent.slug == 'vetements':
                queryset = queryset.filter(clothing_product__isnull=False)
                # Si c'est une sous-catégorie de vêtements, filtrer par style ou matériau
                if category.parent and category.parent.slug == 'vetements':
                    # Essayer de filtrer par style d'abord, puis par matériau
                    queryset = queryset.filter(
                        Q(clothing_product__style__iexact=category.name) |
                        Q(clothing_product__material__iexact=category.name)
                    )
            elif category.slug == 'telephones' or category.name == 'Téléphones':
                queryset = queryset.filter(phone__isnull=False)
            elif category.slug == 'culture' or category.slug == 'articles-culturels':
                queryset = queryset.filter(cultural_product__isnull=False)
        
        # Appliquer les filtres de prix
        price_min = self.request.GET.get('price_min')
        price_max = self.request.GET.get('price_max')
        
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        if price_max:
            queryset = queryset.filter(price__lte=price_max)
            
        # Appliquer les filtres spécifiques aux téléphones uniquement pour les sous-catégories
        if category.parent and category.parent.slug == 'telephones':
            brand = self.request.GET.get('brand')
            model = self.request.GET.get('model')
            storage = self.request.GET.get('storage')
            ram = self.request.GET.get('ram')
            
            if brand:
                queryset = queryset.filter(phone__brand=brand)
            if model:
                queryset = queryset.filter(phone__model=model)
            if storage:
                queryset = queryset.filter(phone__storage=storage)
            if ram:
                queryset = queryset.filter(phone__ram=ram)
                
        # Appliquer les filtres spécifiques aux vêtements
        elif category.slug == 'vetements' or category.parent and category.parent.slug == 'vetements':
            gender = self.request.GET.get('gender')
            size = self.request.GET.get('size')
            color = self.request.GET.get('color')
            material = self.request.GET.get('material')
            style = self.request.GET.get('style')
            season = self.request.GET.get('season')
            
            if gender:
                queryset = queryset.filter(clothing_product__gender=gender)
            if size:
                queryset = queryset.filter(clothing_product__size__name=size)
            if color:
                queryset = queryset.filter(clothing_product__color__name=color)
            if material:
                queryset = queryset.filter(clothing_product__material=material)
            if style:
                queryset = queryset.filter(clothing_product__style=style)
            if season:
                queryset = queryset.filter(clothing_product__season=season)
                
        # Appliquer les filtres spécifiques aux tissus
        elif category.slug == 'tissus':
            fabric_type = self.request.GET.get('fabric_type')
            color = self.request.GET.get('color')
            quality = self.request.GET.get('quality')
            
            if fabric_type:
                queryset = queryset.filter(fabric_product__fabric_type=fabric_type)
            if color:
                queryset = queryset.filter(fabric_product__color__name=color)
            if quality:
                queryset = queryset.filter(fabric_product__quality=quality)
                
        # Appliquer les filtres spécifiques aux articles culturels
        elif category.slug == 'culture' or category.slug == 'articles-culturels':
            author = self.request.GET.get('author')
            isbn = self.request.GET.get('isbn')
            date = self.request.GET.get('date')
            
            if author:
                queryset = queryset.filter(cultural_product__author__icontains=author)
            if isbn:
                queryset = queryset.filter(cultural_product__isbn=isbn)
            if date:
                queryset = queryset.filter(cultural_product__date=date)
        
        return queryset.order_by('-created_at')

    def get_product_card_template(self, category):
        """
        Retourne le template de carte approprié pour la catégorie
        """
        if category.slug == 'tissus':
            return 'suppliers/components/fabric_card.html'
        elif category.slug == 'vetements':
            return 'suppliers/components/clothing_card.html'
        elif category.slug == 'telephones':
            return 'suppliers/components/phone_card.html'
        elif category.slug == 'produits-culturels':
            return 'suppliers/components/cultural_card.html'
        else:
            return 'suppliers/components/product_card.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = kwargs.get('slug')
        
        # Récupérer la catégorie
        category = get_object_or_404(Category, slug=category_slug)
        context['category'] = category
        
        # Construire le fil d'Ariane
        breadcrumbs = []
        current = category
        while current:
            breadcrumbs.insert(0, {
                'name': current.name,
                'url': reverse('suppliers:category_detail', kwargs={'slug': current.slug})
            })
            current = current.parent
        context['breadcrumbs'] = breadcrumbs
        
        # Récupérer les produits avec les filtres
        products = self.get_queryset()
        
        # Pagination
        paginator = Paginator(products, 12)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context['products'] = page_obj
        context['is_paginated'] = page_obj.has_other_pages()
        context['page_obj'] = page_obj
        
        # Déterminer le template à utiliser pour les cartes de produits
        context['product_card_template'] = self.get_product_card_template(category)
        
        return context

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['suppliers/components/_product_grid.html']
        
        category_slug = self.kwargs.get('slug')
        if category_slug == 'articles-culturels':
            return ['suppliers/category_detail.html']
        return [self.template_name]


class SupplierDetailView(DetailView):
    model = Product
    template_name = 'suppliers/supplier_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.filter(
            is_available=True
        ).select_related(
            'phone',
            'phone__color',
            'supplier'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Récupérer les avis
        reviews = product.reviews.all()
        context['reviews'] = reviews
        context['review_form'] = ReviewForm()
        
        # Calculer la moyenne des avis
        if reviews.exists():
            context['average_rating'] = reviews.aggregate(Avg('rating'))['rating__avg']
            context['review_count'] = reviews.count()
        
        # Récupérer les images
        context['images'] = product.images.all().order_by('ordre')
        
        # Si c'est un téléphone, ajouter les informations spécifiques
        if hasattr(product, 'phone'):
            context['phone'] = product.phone
            # Récupérer les téléphones similaires
            similar_phones = Phone.objects.filter(
                Q(brand=product.phone.brand) | 
                Q(model=product.phone.model)
            ).exclude(id=product.phone.id)[:4]
            context['similar_phones'] = similar_phones
        
        return context


class PhoneDetailView(DetailView):
    model = Phone
    template_name = 'suppliers/phone_detail.html'
    context_object_name = 'phone'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        slug = self.kwargs.get('slug')
        return get_object_or_404(
            Phone.objects.select_related(
                'product',
                'product__category',
                'color'
            ).prefetch_related(
                'product__images'
            ),
            product__slug=slug
        )

    def get_breadcrumbs(self, product):
        """Génère les fil d'Ariane pour la navigation"""
        breadcrumbs = [
            {'name': 'Accueil', 'url': reverse('suppliers:supplier_index')}
        ]
        
        # Ajouter toutes les catégories parentes
        current = product.category
        parent_categories = []
        while current:
            parent_categories.insert(0, {
                'name': current.name,
                'url': reverse('suppliers:category_detail', args=[current.slug])
            })
            current = current.parent
        
        breadcrumbs.extend(parent_categories)
        
        # Ajouter le produit actuel
        breadcrumbs.append({
            'name': product.title,
            'url': None
        })
        
        return breadcrumbs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        phone = self.get_object()
        product = phone.product
        
        # Ajouter les images
        context['images'] = product.images.all()
        
        # Ajouter les avis avec optimisation
        reviews = product.reviews.select_related('user').all()
        context['reviews'] = reviews
        if reviews:
            context['average_rating'] = sum(review.rating for review in reviews) / len(reviews)
            context['review_count'] = len(reviews)
        
        # Ajouter les produits similaires avec optimisation et priorité
        # Récupérer toutes les catégories liées (catégorie actuelle + sous-catégories)
        category_ids = [product.category.id]
        
        # Ajouter les sous-catégories directes
        direct_children = product.category.children.all()
        category_ids.extend(direct_children.values_list('id', flat=True))
        
        # Ajouter les sous-sous-catégories
        for child in direct_children:
            grand_children = child.children.all()
            category_ids.extend(grand_children.values_list('id', flat=True))
        
        # Construire les conditions de base
        similar_conditions = Q(phone__isnull=False)
        
        # Ajouter les conditions de caractéristiques seulement si les champs ne sont pas None ou vides
        characteristic_conditions = Q()
        if phone.brand:
            characteristic_conditions |= Q(phone__brand=phone.brand)
        if phone.model:
            characteristic_conditions |= Q(phone__model=phone.model)
        if phone.storage:
            characteristic_conditions |= Q(phone__storage=phone.storage)
        if phone.ram:
            characteristic_conditions |= Q(phone__ram=phone.ram)
        
        # Construire la requête avec priorité
        # Priorité 1: Même catégorie exacte + caractéristiques similaires
        priority_1 = Q(category=product.category)
        if characteristic_conditions:
            priority_1 &= characteristic_conditions
        
        # Priorité 2: Même catégorie exacte
        priority_2 = Q(category=product.category)
        
        # Priorité 3: Sous-catégories + caractéristiques similaires
        priority_3 = Q(category__in=direct_children)
        if characteristic_conditions:
            priority_3 &= characteristic_conditions
        
        # Priorité 4: Sous-catégories
        priority_4 = Q(category__in=direct_children)
        
        # Priorité 5: Sous-sous-catégories + caractéristiques similaires
        grand_children_ids = []
        for child in direct_children:
            grand_children_ids.extend(child.children.values_list('id', flat=True))
        priority_5 = Q(category__id__in=grand_children_ids)
        if characteristic_conditions:
            priority_5 &= characteristic_conditions
        
        # Priorité 6: Sous-sous-catégories
        priority_6 = Q(category__id__in=grand_children_ids)
        
        # Combiner toutes les priorités
        similar_conditions = (
            priority_1 | priority_2 | priority_3 | priority_4 | priority_5 | priority_6
        )
        
        similar_products = Product.objects.filter(
            similar_conditions,
            is_available=True,  # Uniquement les produits disponibles
        ).exclude(
            id=product.id
        ).select_related(
            'phone',
            'phone__color',
            'category'
        ).prefetch_related(
            'images'
        ).order_by(
            # Ordre par priorité : même catégorie d'abord, puis sous-catégories
            'category__id',  # Même catégorie en premier
            '-created_at'    # Puis par date de création
        )[:8]  # Augmenter le nombre pour avoir plus de choix
        
        # Ajouter les catégories principales pour la navigation
        main_categories = Category.objects.filter(
            is_main=True,
            parent__isnull=True
        ).prefetch_related(
            'children',
            'products'
        ).annotate(
            available_products_count=Count('products', filter=Q(products__is_available=True))
        ).order_by('order', 'name')
        
        context.update({
            'similar_products': similar_products,
            'product': product,
            'category_slug': product.category.slug,
            'breadcrumbs': self.get_breadcrumbs(product),
            'main_categories': main_categories
        })
        
        return context


class ClothingDetailView(DetailView):
    model = Product
    template_name = 'suppliers/clothing_detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        slug = self.kwargs.get('slug')
        product = get_object_or_404(
            Product.objects.select_related(
                'clothing_product',
                'category'
            ).prefetch_related(
                'images',
                'clothing_product__size',
                'clothing_product__color'
            ),
            slug=slug
        )
        if not hasattr(product, 'clothing_product'):
            raise Http404("Ce produit n'est pas un vêtement")
        return product

    def get_breadcrumbs(self, product):
        """Génère les fil d'Ariane pour la navigation"""
        breadcrumbs = [
            {'name': 'Accueil', 'url': reverse('suppliers:supplier_index')}
        ]
        
        # Ajouter toutes les catégories parentes
        current = product.category
        parent_categories = []
        while current:
            parent_categories.insert(0, {
                'name': current.name,
                'url': reverse('suppliers:category_detail', args=[current.slug])
            })
            current = current.parent
        
        breadcrumbs.extend(parent_categories)
        
        # Ajouter le produit actuel
        breadcrumbs.append({
            'name': product.title,
            'url': None
        })
        
        return breadcrumbs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        clothing = product.clothing_product
        
        # Ajouter les images
        context['images'] = product.images.all()
        
        # Ajouter les avis
        reviews = product.reviews.all()
        context['reviews'] = reviews
        if reviews:
            context['average_rating'] = sum(review.rating for review in reviews) / len(reviews)
            context['review_count'] = len(reviews)
        
        # Ajouter les produits similaires avec optimisation et priorité
        # Récupérer toutes les catégories liées (catégorie actuelle + sous-catégories)
        category_ids = [product.category.id]
        
        # Ajouter les sous-catégories directes
        direct_children = product.category.children.all()
        category_ids.extend(direct_children.values_list('id', flat=True))
        
        # Ajouter les sous-sous-catégories
        for child in direct_children:
            grand_children = child.children.all()
            category_ids.extend(grand_children.values_list('id', flat=True))
        
        # Construire les conditions de base
        similar_conditions = Q(clothing_product__isnull=False)
        
        # Ajouter les conditions de caractéristiques seulement si les champs ne sont pas None ou vides
        characteristic_conditions = Q()
        if clothing.material:
            characteristic_conditions |= Q(clothing_product__material=clothing.material)
        if clothing.style:
            characteristic_conditions |= Q(clothing_product__style=clothing.style)
        if clothing.gender:
            characteristic_conditions |= Q(clothing_product__gender=clothing.gender)
        
        # Construire la requête avec priorité
        # Priorité 1: Même catégorie exacte + caractéristiques similaires
        priority_1 = Q(category=product.category)
        if characteristic_conditions:
            priority_1 &= characteristic_conditions
        
        # Priorité 2: Même catégorie exacte
        priority_2 = Q(category=product.category)
        
        # Priorité 3: Sous-catégories + caractéristiques similaires
        priority_3 = Q(category__in=direct_children)
        if characteristic_conditions:
            priority_3 &= characteristic_conditions
        
        # Priorité 4: Sous-catégories
        priority_4 = Q(category__in=direct_children)
        
        # Priorité 5: Sous-sous-catégories + caractéristiques similaires
        grand_children_ids = []
        for child in direct_children:
            grand_children_ids.extend(child.children.values_list('id', flat=True))
        priority_5 = Q(category__id__in=grand_children_ids)
        if characteristic_conditions:
            priority_5 &= characteristic_conditions
        
        # Priorité 6: Sous-sous-catégories
        priority_6 = Q(category__id__in=grand_children_ids)
        
        # Combiner toutes les priorités
        similar_conditions = (
            priority_1 | priority_2 | priority_3 | priority_4 | priority_5 | priority_6
        )
        
        similar_products = Product.objects.filter(
            similar_conditions,
            is_available=True,  # Uniquement les produits disponibles
        ).exclude(
            id=product.id
        ).select_related(
            'clothing_product',
            'category'
        ).prefetch_related(
            'images',
            'clothing_product__size',
            'clothing_product__color'
        ).order_by(
            # Ordre par priorité : même catégorie d'abord, puis sous-catégories
            'category__id',  # Même catégorie en premier
            '-created_at'    # Puis par date de création
        )[:8]  # Augmenter le nombre pour avoir plus de choix
        
        # Ajouter les catégories principales pour la navigation
        main_categories = Category.objects.filter(
            is_main=True,
            parent__isnull=True
        ).prefetch_related(
            'children',
            'products'
        ).annotate(
            available_products_count=Count('products', filter=Q(products__is_available=True))
        ).order_by('order', 'name')
        
        context.update({
            'similar_products': similar_products,
            'category_slug': product.category.slug,
            'breadcrumbs': self.get_breadcrumbs(product),
            'main_categories': main_categories,
            'clothing': clothing  # Ajouter l'objet clothing au contexte
        })
        
        return context


class CulturalItemDetailView(DetailView):
    model = Product
    template_name = 'suppliers/cultural_item_detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        slug = self.kwargs.get('slug')
        product = get_object_or_404(
            Product.objects.select_related(
                'cultural_product',
                'category'
            ),
            slug=slug
        )
        if not hasattr(product, 'cultural_product'):
            raise Http404("Ce produit n'est pas un article culturel")
        return product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        cultural_item = product.cultural_product
        
        # Ajouter les images
        context['images'] = product.images.all()
        
        # Ajouter les avis
        reviews = product.reviews.all()
        context['reviews'] = reviews
        if reviews:
            context['average_rating'] = sum(review.rating for review in reviews) / len(reviews)
            context['review_count'] = len(reviews)
        
        # Ajouter les produits similaires avec conditions robustes et priorité
        # Récupérer toutes les catégories liées (catégorie actuelle + sous-catégories)
        category_ids = [product.category.id]
        
        # Ajouter les sous-catégories directes
        direct_children = product.category.children.all()
        category_ids.extend(direct_children.values_list('id', flat=True))
        
        # Ajouter les sous-sous-catégories
        for child in direct_children:
            grand_children = child.children.all()
            category_ids.extend(grand_children.values_list('id', flat=True))
        
        # Construire les conditions de base
        similar_conditions = Q(cultural_product__isnull=False)
        
        # Ajouter les conditions de caractéristiques seulement si les champs ne sont pas None ou vides
        characteristic_conditions = Q()
        if cultural_item.author:
            characteristic_conditions |= Q(cultural_product__author=cultural_item.author)
        
        # Ajouter une condition sur le titre si possible
        if product.title and len(product.title.split()) > 0:
            first_word = product.title.split()[0]
            if len(first_word) > 2:  # Éviter les mots trop courts
                characteristic_conditions |= Q(title__icontains=first_word)
        
        # Construire la requête avec priorité
        # Priorité 1: Même catégorie exacte + caractéristiques similaires
        priority_1 = Q(category=product.category)
        if characteristic_conditions:
            priority_1 &= characteristic_conditions
        
        # Priorité 2: Même catégorie exacte
        priority_2 = Q(category=product.category)
        
        # Priorité 3: Sous-catégories + caractéristiques similaires
        priority_3 = Q(category__in=direct_children)
        if characteristic_conditions:
            priority_3 &= characteristic_conditions
        
        # Priorité 4: Sous-catégories
        priority_4 = Q(category__in=direct_children)
        
        # Priorité 5: Sous-sous-catégories + caractéristiques similaires
        grand_children_ids = []
        for child in direct_children:
            grand_children_ids.extend(child.children.values_list('id', flat=True))
        priority_5 = Q(category__id__in=grand_children_ids)
        if characteristic_conditions:
            priority_5 &= characteristic_conditions
        
        # Priorité 6: Sous-sous-catégories
        priority_6 = Q(category__id__in=grand_children_ids)
        
        # Combiner toutes les priorités
        similar_conditions = (
            priority_1 | priority_2 | priority_3 | priority_4 | priority_5 | priority_6
        )
        
        similar_products = Product.objects.filter(
            similar_conditions,
            is_available=True,  # Uniquement les produits disponibles
        ).exclude(
            id=product.id
        ).select_related(
            'cultural_product',
            'category'
        ).prefetch_related(
            'images'
        ).order_by(
            # Ordre par priorité : même catégorie d'abord, puis sous-catégories
            'category__id',  # Même catégorie en premier
            '-created_at'    # Puis par date de création
        )[:8]  # Augmenter le nombre pour avoir plus de choix
        
        context['similar_products'] = similar_products
        context['cultural_item'] = cultural_item
        context['category_slug'] = product.category.slug  # Ajouter le slug de la catégorie
        
        return context


class FabricDetailView(DetailView):
    model = Product
    template_name = 'suppliers/fabric_detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        slug = self.kwargs.get('slug')
        product = get_object_or_404(Product.objects.select_related('fabric_product'), slug=slug)
        if not hasattr(product, 'fabric_product'):
            raise Http404("Ce produit n'est pas un tissu")
        return product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Récupérer les produits similaires avec conditions robustes et priorité
        # Récupérer toutes les catégories liées (catégorie actuelle + sous-catégories)
        category_ids = [product.category.id]
        
        # Ajouter les sous-catégories directes
        direct_children = product.category.children.all()
        category_ids.extend(direct_children.values_list('id', flat=True))
        
        # Ajouter les sous-sous-catégories
        for child in direct_children:
            grand_children = child.children.all()
            category_ids.extend(grand_children.values_list('id', flat=True))
        
        # Construire les conditions de base
        similar_conditions = Q(fabric_product__isnull=False)
        
        # Ajouter les conditions de caractéristiques seulement si les champs ne sont pas None ou vides
        characteristic_conditions = Q()
        if product.fabric_product.fabric_type:
            characteristic_conditions |= Q(fabric_product__fabric_type=product.fabric_product.fabric_type)
        if product.fabric_product.quality:
            characteristic_conditions |= Q(fabric_product__quality=product.fabric_product.quality)
        
        # Construire la requête avec priorité
        # Priorité 1: Même catégorie exacte + caractéristiques similaires
        priority_1 = Q(category=product.category)
        if characteristic_conditions:
            priority_1 &= characteristic_conditions
        
        # Priorité 2: Même catégorie exacte
        priority_2 = Q(category=product.category)
        
        # Priorité 3: Sous-catégories + caractéristiques similaires
        priority_3 = Q(category__in=direct_children)
        if characteristic_conditions:
            priority_3 &= characteristic_conditions
        
        # Priorité 4: Sous-catégories
        priority_4 = Q(category__in=direct_children)
        
        # Priorité 5: Sous-sous-catégories + caractéristiques similaires
        grand_children_ids = []
        for child in direct_children:
            grand_children_ids.extend(child.children.values_list('id', flat=True))
        priority_5 = Q(category__id__in=grand_children_ids)
        if characteristic_conditions:
            priority_5 &= characteristic_conditions
        
        # Priorité 6: Sous-sous-catégories
        priority_6 = Q(category__id__in=grand_children_ids)
        
        # Combiner toutes les priorités
        similar_conditions = (
            priority_1 | priority_2 | priority_3 | priority_4 | priority_5 | priority_6
        )
        
        similar_products = Product.objects.filter(
            similar_conditions
        ).exclude(
            id=product.id
        ).select_related(
            'fabric_product',
            'category'
        ).prefetch_related(
            'images'
        ).order_by(
            # Ordre par priorité : même catégorie d'abord, puis sous-catégories
            'category__id',  # Même catégorie en premier
            '-created_at'    # Puis par date de création
        )[:8]  # Augmenter le nombre pour avoir plus de choix
        
        # Ajouter les avis et la note moyenne
        reviews = product.reviews.all()
        if reviews:
            context['average_rating'] = sum(review.rating for review in reviews) / len(reviews)
            context['review_count'] = len(reviews)
        
        context['similar_products'] = similar_products
        context['reviews'] = reviews
        context['images'] = product.images.all()
        context['category_slug'] = product.category.slug  # Ajouter le slug de la catégorie
        
        return context


class CategoryListView(ListView):
    """Vue pour afficher la liste des catégories principales"""
    model = Category
    template_name = 'suppliers/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        # Récupérer uniquement les catégories principales
        return Category.objects.filter(
            is_main=True
        ).prefetch_related(
            'children',
            'children__children',
            'products'
        ).annotate(
            available_products_count=Count(
                'products',
                filter=Q(products__is_available=True)
            )
        ).order_by('order', 'name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Nos catégories principales',
            'main_categories': self.get_queryset()
        })
        return context


class ProductDetailView(DetailView):
    """Vue pour afficher les détails d'un produit générique"""
    model = Product
    template_name = 'suppliers/product_detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Product.objects.filter(
            is_available=True
        ).select_related(
            'category',
            'supplier'
        ).prefetch_related(
            'reviews',
            'images'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Récupérer les avis et la note moyenne
        reviews = product.reviews.all()
        average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        average_rating = round(average_rating, 1)
        
        # Récupérer les produits similaires avec cache et priorité
        cache_key = f'similar_products_{product.id}'
        similar_products = cache.get(cache_key)
        
        if similar_products is None:
            # Récupérer toutes les catégories liées (catégorie actuelle + sous-catégories)
            category_ids = [product.category.id]
            
            # Ajouter les sous-catégories directes
            direct_children = product.category.children.all()
            category_ids.extend(direct_children.values_list('id', flat=True))
            
            # Ajouter les sous-sous-catégories
            for child in direct_children:
                grand_children = child.children.all()
                category_ids.extend(grand_children.values_list('id', flat=True))
            
            # Construire la requête avec priorité
            # Priorité 1: Même catégorie exacte
            priority_1 = Q(category=product.category)
            
            # Priorité 2: Sous-catégories
            priority_2 = Q(category__in=direct_children)
            
            # Priorité 3: Sous-sous-catégories
            grand_children_ids = []
            for child in direct_children:
                grand_children_ids.extend(child.children.values_list('id', flat=True))
            priority_3 = Q(category__id__in=grand_children_ids)
            
            # Combiner toutes les priorités
            similar_conditions = priority_1 | priority_2 | priority_3
            
            similar_products = Product.objects.filter(
                similar_conditions,
                is_available=True,
            ).exclude(id=product.id).select_related(
                'category',
                'supplier',
                'phone',
                'phone__color',
                'fabric_product',
                'clothing_product',
                'cultural_product'
            ).prefetch_related(
                'clothing_product__size',
                'clothing_product__color',
                'fabric_product__color',
                'images'
            ).order_by(
                # Ordre par priorité : même catégorie d'abord, puis sous-catégories
                'category__id',  # Même catégorie en premier
                '-created_at'    # Puis par date de création
            )[:8]  # Augmenter le nombre pour avoir plus de choix
            
            # Mettre en cache pour 1 heure
            cache.set(cache_key, similar_products, 3600)
        
        # Récupérer les images
        images = product.images.all().order_by('ordre')
        
        context.update({
            'reviews': reviews,
            'average_rating': average_rating,
            'similar_products': similar_products,
            'breadcrumbs': self.get_breadcrumbs(product),
            'images': images,
            'category_slug': product.category.slug,
        })
        
        return context
    
    def get_breadcrumbs(self, product):
        """Génère les fil d'Ariane pour la navigation"""
        breadcrumbs = [
            {'name': 'Accueil', 'url': reverse('suppliers:supplier_index')}
        ]
        
        # Ajouter toutes les catégories parentes
        current = product.category
        parent_categories = []
        while current:
            parent_categories.insert(0, {
                'name': current.name,
                'url': reverse('suppliers:category_detail', args=[current.slug])
            })
            current = current.parent
        
        breadcrumbs.extend(parent_categories)
        
        # Ajouter le produit actuel
        breadcrumbs.append({
            'name': product.title,
            'url': None
        })
        
        return breadcrumbs


@login_required
def add_review(request, slug):
    product = get_object_or_404(Product, slug=slug)
    
    # Vérifier que l'utilisateur a acheté ce produit
    from cart.models import OrderItem
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        product=product,
        order__is_paid=True
    ).exists()
    
    if not has_purchased:
        messages.error(request, 'Vous devez avoir acheté ce produit pour pouvoir laisser un avis.')
        return redirect('suppliers:product_detail', slug=product.slug)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Vérifier qu'il n'a pas déjà laissé un avis
            from product.models import Review
            existing_review = Review.objects.filter(user=request.user, product=product).first()
            if existing_review:
                messages.error(request, 'Vous avez déjà laissé un avis pour ce produit.')
                return redirect('suppliers:product_detail', slug=product.slug)
            
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Votre avis a été ajouté avec succès.')
            return redirect('suppliers:product_detail', slug=product.slug)
        else:
            messages.error(request, 'Une erreur est survenue lors de l\'ajout de votre avis.')
    
    return redirect('suppliers:product_detail', slug=product.slug)


@login_required
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
    
    if not created:
        favorite.delete()
        action = "removed"
    else:
        action = "added"
    
    # Invalider le cache
    cache_key = f"favorite_{request.user.id}_{product.id}"
    cache.delete(cache_key)
    
    # Rendre le template avec le bon état
    context = {
        'product': product,
        'user': request.user,
        'action': action,
        'is_detail': request.GET.get('template') == 'button'
    }
    
    # Déterminer quel template utiliser en fonction du paramètre
    template_name = request.GET.get('template', 'card')
    if template_name == 'button':
        favorite_button_html = render_to_string('suppliers/components/_favorite_button.html', context, request=request)
    else:
        favorite_button_html = render_to_string('suppliers/components/_favorite_card_button.html', context, request=request)
    
    # Rendre le compteur de favoris
    favorite_count_html = render_to_string('suppliers/components/_favorite_count.html', context, request=request)
    
    # Si l'action est "removed", mettre à jour la liste des favoris
    if action == "removed":
        # Récupérer la liste mise à jour des favoris (non paginée pour HTMX)
        favorites = Favorite.objects.filter(
            user=request.user
        ).select_related(
            'product',
            'product__category',
            'product__phone',
            'product__clothing_product',
            'product__fabric_product',
            'product__cultural_product'
        ).prefetch_related(
            'product__images'
        ).order_by('-created_at')
        
        # Rendre le template de la liste des favoris (sans pagination pour HTMX)
        favorites_list_html = render_to_string('suppliers/components/_favorites_list.html', {
            'favorites': favorites,
            'user': request.user,
            # Ne pas passer page_obj pour éviter la pagination dans HTMX
        }, request=request)
        
        # Combiner toutes les réponses
        response = favorite_button_html + favorite_count_html + favorites_list_html
    else:
        # Combiner les réponses sans la liste des favoris
        response = favorite_button_html + favorite_count_html
    
    return HttpResponse(response)


class FavoriteListView(LoginRequiredMixin, ListView):
    """Vue pour afficher la liste des favoris de l'utilisateur"""
    model = Favorite
    template_name = 'suppliers/favorite_list.html'
    context_object_name = 'favorites'
    paginate_by = 12

    def get_queryset(self):
        return Favorite.objects.filter(
            user=self.request.user
        ).select_related(
            'product',
            'product__category',
            'product__phone',
            'product__clothing_product',
            'product__fabric_product',
            'product__cultural_product'
        ).prefetch_related(
            'product__images'
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Mes favoris'
        return context


def search(request):
    query = request.GET.get('q', '').strip()
    products = None  # None au lieu d'une liste vide pour distinguer "pas de recherche" de "aucun résultat"
    
    if query:
        # Utiliser la nouvelle fonction de recherche améliorée
        search_query = create_search_query(query)
        products = Product.objects.filter(search_query).select_related('category', 'supplier').prefetch_related('images')
    
    # Tracking de la recherche
    track_search(
        request=request,
        search_term=query,
        results_count=products.count() if products else 0
    )
    
    context = {
        'query': query,
        'products': products,
        'has_searched': bool(query)  # Indique si une recherche a été effectuée
    }
    
    if request.htmx:
        return render(request, 'search_results.html', context)
    return render(request, 'suppliers/search_results.html', context)


def search_suggestions(request):
    """Vue pour les suggestions de recherche"""
    query = request.GET.get('q', '').strip()
    suggestions = None  # None au lieu d'une liste vide pour distinguer "pas de recherche" de "aucun résultat"
    
    if query:
        suggestions = []
        # Utiliser la nouvelle fonction de recherche améliorée
        search_query = create_search_query(query)
        products = Product.objects.filter(search_query).select_related('category').distinct()[:10]
        
        # Créer des suggestions basées sur les produits trouvés
        for product in products:
            # Suggestion basée sur le titre (plus précise)
            normalized_title = normalize_search_term(product.title)
            normalized_query = normalize_search_term(query)
            if normalized_query in normalized_title:
                suggestions.append({
                    'type': 'product',
                    'text': product.title,
                    'url': f'/search/results/?text={product.title}&keywords={product.title}',
                    'icon': 'product',
                    'relevance': normalized_title.count(normalized_query)  # Score de pertinence
                })
            # Suggestion basée sur la catégorie
            if product.category:
                normalized_category = normalize_search_term(product.category.name)
                if normalized_query in normalized_category:
                    # Éviter les doublons de catégories
                    if not any(s['type'] == 'category' and s['text'] == product.category.name for s in suggestions):
                        suggestions.append({
                            'type': 'category',
                            'text': product.category.name,
                            'url': f'/search/results/?text={product.category.name}&keywords={product.category.name}',
                            'icon': 'category',
                            'relevance': 5  # Score de pertinence pour les catégories
                        })
        # Ajouter des suggestions populaires si pas assez de résultats
        if len(suggestions) < 5:
            popular_keywords = [
                'iPhone', 'Samsung', 'Téléphone', 'Ordinateur', 'Laptop',
                'Vêtements', 'Chaussures', 'Accessoires', 'Électronique',
                'Smartphone', 'Tablette', 'Écouteurs', 'Montre'
            ]
            normalized_query = normalize_search_term(query)
            for keyword in popular_keywords:
                normalized_keyword = normalize_search_term(keyword)
                if normalized_query in normalized_keyword:
                    # Éviter les doublons
                    if not any(s['text'] == keyword for s in suggestions):
                        suggestions.append({
                            'type': 'keyword',
                            'text': keyword,
                            'url': f'/search/results/?text={keyword}&keywords={keyword}',
                            'icon': 'search',
                            'relevance': 3  # Score de pertinence pour les mots-clés
                        })
        # Trier par pertinence et limiter à 8 suggestions maximum
        suggestions.sort(key=lambda x: x.get('relevance', 0), reverse=True)
        suggestions = suggestions[:8]
        # Nettoyer les suggestions (enlever le score de pertinence)
        for suggestion in suggestions:
            suggestion.pop('relevance', None)
    context = {
        'suggestions': suggestions,
        'query': query,
        'has_searched': bool(query)  # Indique si une recherche a été effectuée
    }
    if request.htmx:
        return render(request, 'search_suggestions.html', context)
    return JsonResponse({'suggestions': suggestions})


def search_results_page(request):
    """Page dédiée aux résultats de recherche avec paramètres text et keywords"""
    text = request.GET.get('text', '').strip()
    keywords = request.GET.get('keywords', '').strip()
    
    # Utiliser text comme requête principale, keywords comme contexte
    search_query = text or keywords
    
    # Initialiser avec tous les produits disponibles
    products = Product.objects.filter(is_available=True).select_related('category', 'supplier').prefetch_related('images')
    
    # Appliquer la recherche si un terme est fourni
    if search_query:
        # Utiliser la nouvelle fonction de recherche améliorée
        search_filter = create_search_query(search_query)
        products = products.filter(search_filter)
    
    # Appliquer les filtres si présents
    # Filtres de prix
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    
    logger.info(f"Filtres de prix - min: {price_min}, max: {price_max}")
    
    if price_min and price_min.strip():
        try:
            min_price = float(price_min)
            products = products.filter(price__gte=min_price)
            logger.info(f"Filtre prix min appliqué: {min_price}")
        except (ValueError, TypeError) as e:
            logger.warning(f"Valeur invalide pour prix min: {price_min}, erreur: {e}")
    
    if price_max and price_max.strip():
        try:
            max_price = float(price_max)
            products = products.filter(price__lte=max_price)
            logger.info(f"Filtre prix max appliqué: {max_price}")
        except (ValueError, TypeError) as e:
            logger.warning(f"Valeur invalide pour prix max: {price_max}, erreur: {e}")
    
    # Filtre de condition
    condition = request.GET.get('condition')
    logger.info(f"Filtre de condition: {condition}")
    if condition and condition.strip():
        products = products.filter(condition=condition)
        logger.info(f"Filtre condition appliqué: {condition}")
        logger.info(f"Nombre de produits après filtre condition: {products.count()}")
    
    # Filtre de garantie
    warranty = request.GET.get('warranty')
    logger.info(f"Filtre de garantie: {warranty}")
    if warranty and warranty.strip():
        if warranty == 'yes':
            products = products.filter(has_warranty=True)
        elif warranty == 'no':
            products = products.filter(has_warranty=False)
        logger.info(f"Filtre garantie appliqué: {warranty}")
        logger.info(f"Nombre de produits après filtre garantie: {products.count()}")
    
    # Filtre de promotion
    promotion = request.GET.get('promotion')
    if promotion and promotion.strip():
        if promotion == 'yes':
            products = products.filter(discount_price__isnull=False)
        elif promotion == 'no':
            products = products.filter(discount_price__isnull=True)
    
    # Filtre de marque
    brand = request.GET.get('brand')
    if brand and brand.strip():
        products = products.filter(brand__icontains=brand)
    
    # Log final du nombre de produits
    final_count = products.count()
    logger.info(f"Nombre final de produits après tous les filtres: {final_count}")
    
    # Récupérer les valeurs sélectionnées pour les filtres
    selected_price_min = request.GET.get('price_min', '')
    selected_price_max = request.GET.get('price_max', '')
    selected_condition = request.GET.get('condition', '')
    selected_warranty = request.GET.get('warranty', '')
    selected_promotion = request.GET.get('promotion', '')
    selected_brand = request.GET.get('brand', '')
    
    # Créer les breadcrumbs pour la recherche
    breadcrumbs = [
        {'name': 'Accueil', 'url': '/'},
        {'name': 'Recherche', 'url': '#'},
        {'name': f'"{search_query}"', 'url': None}
    ]
    
    context = {
        'products': products,
        'query': search_query,
        'text': text,
        'keywords': keywords,
        'total_results': len(products),
        'breadcrumbs': breadcrumbs,
        # Données pour les filtres
        'selected_price_min': selected_price_min,
        'selected_price_max': selected_price_max,
        'selected_condition': selected_condition,
        'selected_warranty': selected_warranty,
        'selected_promotion': selected_promotion,
        'selected_brand': selected_brand,
    }
    
    return TemplateResponse(request, 'suppliers/search_results_page.html', context)


def category_subcategories(request, category_id):
    """Vue pour récupérer les sous-catégories d'une catégorie (pour le menu mobile)"""
    try:
        category = Category.objects.get(id=category_id)
        subcategories = category.children.all().order_by('order', 'name')
        
        context = {
            'category': category,
            'subcategories': subcategories,
        }
        
        return render(request, 'components/_subcategories_menu.html', context)
    except Category.DoesNotExist:
        return HttpResponse('Catégorie non trouvée', status=404)


def category_tree(request):
    """Vue pour récupérer l'arbre des catégories (pour le menu mobile)"""
    categories = Category.objects.filter(
        parent__isnull=True,
        is_main=True
    ).prefetch_related('children').order_by('order', 'name')
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'components/_subcategories_menu.html', context)





