from django.shortcuts import render, get_object_or_404, redirect
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

logger = logging.getLogger(__name__)


class SupplierListView(ListView):
    model = Product
    template_name = 'suppliers/supplier_list.html'
    context_object_name = 'products'
    paginate_by = 12
    def get_queryset(self):
        queryset = Product.objects.filter(
            is_available=True,
            is_salam=True
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
            type_clothing = self.request.GET.get('type')

            if gender:
                queryset = queryset.filter(clothing_product__gender=gender)
            if size:
                queryset = queryset.filter(clothing_product__size=size)
            if color:
                queryset = queryset.filter(clothing_product__color__name=color)
            if type_clothing:
                queryset = queryset.filter(clothing_product__type=type_clothing)

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
            is_available=True,
            is_salam=True
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
        context['clothing_types'] = [{'clothing_product__type': t} for t in sorted(filter(None, active_products.filter(clothing_product__isnull=False).values_list('clothing_product__type', flat=True).distinct()))]

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
        context['selected_type'] = self.request.GET.get('type', '')
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

        # Ajouter les produits par type au contexte
        context['products'] = products.filter(phone__isnull=False)[:4]
        context['clothing_products'] = products.filter(clothing_product__isnull=False)[:4]
        context['fabric_products'] = products.filter(fabric_product__isnull=False)[:4]
        context['cultural_products'] = products.filter(cultural_product__isnull=False)[:4]
        
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
            is_available=True,
            is_salam=True
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
                # Si c'est une sous-catégorie de vêtements, filtrer par type
                if category.parent and category.parent.slug == 'vetements':
                    queryset = queryset.filter(clothing_product__type__iexact=category.name)
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
            type_clothing = self.request.GET.get('type')
            
            if gender:
                queryset = queryset.filter(clothing_product__gender=gender)
            if size:
                queryset = queryset.filter(clothing_product__size=size)
            if color:
                queryset = queryset.filter(clothing_product__color__name=color)
            if type_clothing:
                queryset = queryset.filter(clothing_product__type=type_clothing)
                
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
            is_available=True,
            is_salam=True
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
        
        # Ajouter les produits similaires avec optimisation
        similar_products = Product.objects.filter(
            Q(phone__isnull=False) &  # S'assurer que ce sont des téléphones
            (
                Q(phone__brand=phone.brand) |  # Même marque
                Q(phone__model=phone.model) |  # Même modèle
                Q(category=product.category) |  # Même catégorie
                Q(phone__storage=phone.storage) |  # Même capacité de stockage
                Q(phone__ram=phone.ram)  # Même RAM
            ),
            is_available=True,  # Uniquement les produits disponibles
            is_salam=True  # Uniquement les produits Salam
        ).exclude(
            id=product.id
        ).select_related(
            'phone',
            'phone__color',
            'category'
        ).prefetch_related(
            'images'
        ).order_by(
            '-created_at'  # Les plus récents en premier
        )[:4]
        
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
        
        # Ajouter les avis avec optimisation
        reviews = product.reviews.select_related('user').all()
        context['reviews'] = reviews
        if reviews:
            context['average_rating'] = sum(review.rating for review in reviews) / len(reviews)
            context['review_count'] = len(reviews)
        
        # Ajouter les produits similaires avec optimisation
        similar_products = Product.objects.filter(
            Q(clothing_product__isnull=False) &
            (
                Q(clothing_product__type=clothing.type) |  # Même type
                Q(clothing_product__gender=clothing.gender) |  # Même genre
                Q(category=product.category)  # Même catégorie
            ),
            is_available=True,  # Uniquement les produits disponibles
            is_salam=True  # Uniquement les produits Salam
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
            '-created_at'
        )[:4]
        
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
        
        # Ajouter les produits similaires
        similar_products = Product.objects.filter(
            Q(category=product.category) |  # Même catégorie
            Q(cultural_product__author=cultural_item.author) |  # Même auteur
            Q(title__icontains=product.title.split()[0]),  # Titre similaire
            cultural_product__isnull=False,
            is_available=True,  # Uniquement les produits disponibles
            is_salam=True  # Uniquement les produits Salam
        ).exclude(
            id=product.id
        ).select_related(
            'cultural_product',
            'category'
        ).prefetch_related(
            'images'
        ).order_by(
            '-created_at'  # Les plus récents en premier
        )[:4]
        
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
        
        # Récupérer les produits similaires
        similar_products = Product.objects.filter(
            Q(fabric_product__isnull=False) &
            (
                Q(fabric_product__fabric_type=product.fabric_product.fabric_type) |  # Même type de tissu
                Q(category=product.category) |  # Même catégorie
                Q(fabric_product__quality=product.fabric_product.quality)  # Même qualité
            )
        ).exclude(
            id=product.id
        ).select_related(
            'fabric_product',
            'category'
        ).prefetch_related(
            'images'
        ).order_by(
            '-created_at'  # Les plus récents en premier
        )[:4]
        
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
                filter=Q(products__is_available=True, products__is_salam=True)
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
            is_available=True,
            is_salam=True
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
        
        # Récupérer les produits similaires avec cache
        cache_key = f'similar_products_{product.id}'
        similar_products = cache.get(cache_key)
        
        if similar_products is None:
            similar_products = Product.objects.filter(
                category=product.category,
                is_available=True,
                is_salam=True
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
            )[:4]
            
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
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
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
        # Récupérer la liste mise à jour des favoris
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
        
        # Rendre le template de la liste des favoris
        favorites_list_html = render_to_string('suppliers/components/_favorites_list.html', {
            'favorites': favorites,
            'user': request.user
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


