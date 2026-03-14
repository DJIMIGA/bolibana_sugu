from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from django.db.models import Count, Q
from product.models import Category, Product, Clothing, ShippingMethod
import logging
from django.utils import timezone
from datetime import timedelta
from django.db.models import Prefetch
from core.facebook_conversions import facebook_conversions
from django.db import models
import re

logger = logging.getLogger(__name__)

def convert_french_date_to_db_format(french_date_str):
    """
    Convertit une date française (ex: "1 janvier 2019") en format de base de données (YYYY-MM-DD)
    """
    if not french_date_str:
        return None
    
    # Mapping des mois français vers les numéros
    mois_mapping = {
        'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
        'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
        'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
    }
    
    try:
        # Nettoyer la chaîne
        date_str = french_date_str.strip()
        
        # Pattern pour "1 janvier 2019" ou "01 janvier 2019"
        pattern = r'(\d{1,2})\s+(\w+)\s+(\d{4})'
        match = re.match(pattern, date_str)
        
        if match:
            jour, mois_fr, annee = match.groups()
            mois_num = mois_mapping.get(mois_fr.lower())
            
            if mois_num:
                # Formater en YYYY-MM-DD
                jour_formate = jour.zfill(2)  # Ajouter un zéro si nécessaire
                return f"{annee}-{mois_num}-{jour_formate}"
        
        return None
    except Exception as e:
        print(f"Erreur lors de la conversion de la date '{french_date_str}': {e}")
        return None

class BaseCategoryView(TemplateView):
    """Vue de base pour toutes les catégories"""
    template_name = 'suppliers/category_detail.html'
    
    def get_category(self):
        """Récupère la catégorie à partir du slug"""
        category_slug = self.kwargs.get('slug')
        return get_object_or_404(Category, slug=category_slug)
    
    def get_base_queryset(self):
        """Retourne le queryset de base avec les relations communes"""
        queryset = Product.objects.all().select_related(
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
        
        return queryset
    
    def apply_generic_filters(self, queryset):
        """Applique les filtres génériques pour tous les produits"""
        print("\n=== DEBUG GENERIC FILTERS ===")
        print(f"Nombre de produits avant filtres: {queryset.count()}")
        
        # Filtre par nom du produit (recherche insensible à la casse)
        name = self.request.GET.get('name')
        if name:
            queryset = queryset.filter(title__icontains=name)
            print(f"Filtre nom: {name} - Produits restants: {queryset.count()}")

        # Filtre par marque (recherche insensible à la casse)
        brand = self.request.GET.get('brand')
        if brand:
            queryset = queryset.filter(
                Q(brand__icontains=brand) |  # Pour les produits génériques
                Q(phone__brand__icontains=brand) |  # Pour les téléphones
                Q(fabric_product__fabric_type__icontains=brand)  # Pour les tissus
            )
            print(f"Filtre marque: {brand} - Produits restants: {queryset.count()}")

        # Filtre par catégorie (recherche insensible à la casse)
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__name__icontains=category)
            print(f"Filtre catégorie: {category} - Produits restants: {queryset.count()}")

        # Filtre par fournisseur (recherche insensible à la casse)
        supplier = self.request.GET.get('supplier')
        if supplier:
            queryset = queryset.filter(supplier__name__icontains=supplier)
            print(f"Filtre fournisseur: {supplier} - Produits restants: {queryset.count()}")

        # Filtre par état du produit (neuf, occasion, reconditionné)
        condition = self.request.GET.get('condition')
        if condition:
            queryset = queryset.filter(condition=condition)
            print(f"Filtre condition: {condition} - Produits restants: {queryset.count()}")

        # Filtre par garantie (avec ou sans garantie)
        warranty = self.request.GET.get('warranty')
        if warranty:
            if warranty == 'yes':
                queryset = queryset.filter(has_warranty=True)
            elif warranty == 'no':
                queryset = queryset.filter(has_warranty=False)
            print(f"Filtre garantie: {warranty} - Produits restants: {queryset.count()}")

        # Filtre par note moyenne (minimum 1 à 5 étoiles)
        rating = self.request.GET.get('rating')
        if rating:
            try:
                rating_value = float(rating)
                if 1 <= rating_value <= 5:
                    queryset = queryset.filter(average_rating__gte=rating_value)
                    print(f"Filtre note: {rating_value} - Produits restants: {queryset.count()}")
            except (ValueError, TypeError):
                pass

        # Filtre par promotion (en promotion ou non)
        promotion = self.request.GET.get('promotion')
        if promotion:
            if promotion == 'yes':
                queryset = queryset.filter(discount_price__isnull=False)
            elif promotion == 'no':
                queryset = queryset.filter(discount_price__isnull=True)
            print(f"Filtre promotion: {promotion} - Produits restants: {queryset.count()}")

        # Filtre par méthode de livraison
        shipping = self.request.GET.get('shipping')
        if shipping:
            queryset = queryset.filter(shipping_methods__name=shipping)
            print(f"Filtre livraison: {shipping} - Produits restants: {queryset.count()}")

        # Filtre par poids (min et max)
        weight_min = self.request.GET.get('weight_min')
        if weight_min:
            try:
                queryset = queryset.filter(weight__gte=float(weight_min))
                print(f"Filtre poids min: {weight_min} - Produits restants: {queryset.count()}")
            except (ValueError, TypeError):
                pass

        weight_max = self.request.GET.get('weight_max')
        if weight_max:
            try:
                queryset = queryset.filter(weight__lte=float(weight_max))
                print(f"Filtre poids max: {weight_max} - Produits restants: {queryset.count()}")
            except (ValueError, TypeError):
                pass

        # Filtre par dimensions
        dimensions = self.request.GET.get('dimensions')
        if dimensions:
            queryset = queryset.filter(dimensions__icontains=dimensions)
            print(f"Filtre dimensions: {dimensions} - Produits restants: {queryset.count()}")

        # Filtre par couleur (commun à tous les produits)
        color = self.request.GET.get('color')
        if color:
            queryset = queryset.filter(
                Q(phone__color__name__icontains=color) |
                Q(clothing_product__color__name__icontains=color) |
                Q(fabric_product__color__name__icontains=color)
            )
            print(f"Filtre couleur: {color} - Produits restants: {queryset.count()}")

        # Filtre par qualité (pour les tissus)
        quality = self.request.GET.get('quality')
        if quality:
            queryset = queryset.filter(
                Q(fabric_product__quality__icontains=quality)
            )
            print(f"Filtre qualité: {quality} - Produits restants: {queryset.count()}")

        # Filtre par type de tissu
        fabric_type = self.request.GET.get('fabric_type')
        if fabric_type:
            queryset = queryset.filter(fabric_product__fabric_type__icontains=fabric_type)
            print(f"Filtre type tissu: {fabric_type} - Produits restants: {queryset.count()}")

        # Filtre par auteur (pour les articles culturels)
        author = self.request.GET.get('author')
        if author:
            queryset = queryset.filter(cultural_product__author__icontains=author)
            print(f"Filtre auteur: {author} - Produits restants: {queryset.count()}")

        # Filtre par date de publication (pour les articles culturels)
        publication_date = self.request.GET.get('publication_date')
        if publication_date:
            queryset = queryset.filter(cultural_product__date=publication_date)
            print(f"Filtre date publication: {publication_date} - Produits restants: {queryset.count()}")

        sort = self.request.GET.get('sort')
        if sort == 'price_asc':
            queryset = queryset.order_by('-is_available', 'price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-is_available', '-price')
        elif sort == 'new':
            queryset = queryset.order_by('-is_available', '-created_at')
        elif sort == 'best_selling':
            queryset = queryset.order_by('-is_available', '-sales_count')

        print(f"Nombre final de produits après tous les filtres: {queryset.count()}")
        print("=== FIN DEBUG GENERIC FILTERS ===\n")
        return queryset

    def get_queryset(self):
        print(f"[DEBUG] Paramètres GET reçus dans get_queryset : {self.request.GET}")
        category = self.get_category()
        queryset = self.get_base_queryset()

        # Appliquer le filtre de garantie
        warranty = self.request.GET.get('warranty')
        if warranty:
            if warranty == 'yes':
                queryset = queryset.filter(has_warranty=True)
            elif warranty == 'no':
                queryset = queryset.filter(has_warranty=False)

        # Appliquer le filtre de méthode de livraison en premier
        shipping = self.request.GET.get('shipping')
        if shipping:
            queryset = queryset.filter(shipping_methods__name=shipping)

        # Si c'est "Tous les produits" ou une de ses sous-catégories (jusqu'au niveau 3)
        if (category.slug == 'tous-les-produits' or 
            (category.parent and category.parent.slug == 'tous-les-produits') or
            (category.parent and category.parent.parent and category.parent.parent.slug == 'tous-les-produits')):
            # Appliquer le filtre de catégorie principale
            main_category = self.request.GET.get('main_category')
            if main_category:
                cat = Category.objects.filter(slug=main_category).first()
                print(f"[DEBUG] main_category param: {main_category}, cat found: {cat}")
                if cat:
                    all_ids = cat.get_all_children_ids()
                    print(f"[DEBUG] IDs filtrés pour la catégorie '{cat.name}': {all_ids}")
                    queryset = queryset.filter(category_id__in=all_ids)

        # Si c'est "Téléphones" ou une de ses sous-catégories (jusqu'au niveau 3)
        elif (category.slug == 'telephones' or 
              (category.parent and category.parent.slug == 'telephones') or
              (category.parent and category.parent.parent and category.parent.parent.slug == 'telephones')):
            queryset = queryset.filter(phone__isnull=False)
            
            # Appliquer les filtres spécifiques pour les sous-catégories et petits-fils de téléphones
            is_phone_subcategory = (category.parent and category.parent.slug == 'telephones') or \
                                 (category.parent and category.parent.parent and category.parent.parent.slug == 'telephones')
            
            if is_phone_subcategory:
                brand = self.request.GET.get('brand')
                if brand:
                    queryset = queryset.filter(phone__brand=brand)

                model = self.request.GET.get('model')
                if model:
                    queryset = queryset.filter(phone__model=model)

                storage = self.request.GET.get('storage')
                if storage:
                    queryset = queryset.filter(phone__storage=storage)

                ram = self.request.GET.get('ram')
                if ram:
                    queryset = queryset.filter(phone__ram=ram)

        # Si c'est "Vêtements" ou une de ses sous-catégories (jusqu'au niveau 3)
        elif (category.slug == 'vetements' or 
              (category.parent and category.parent.slug == 'vetements') or
              (category.parent and category.parent.parent and category.parent.parent.slug == 'vetements')):
            queryset = queryset.filter(clothing_product__isnull=False)
            
            gender = self.request.GET.get('gender')
            if gender:
                queryset = queryset.filter(clothing_product__gender=gender)

            size = self.request.GET.get('size')
            if size:
                queryset = queryset.filter(clothing_product__size__name=size)

            color = self.request.GET.get('color')
            if color:
                queryset = queryset.filter(clothing_product__color__name=color)

            material = self.request.GET.get('material')
            if material:
                queryset = queryset.filter(clothing_product__material=material)

            style = self.request.GET.get('style')
            if style:
                queryset = queryset.filter(clothing_product__style=style)

            season = self.request.GET.get('season')
            if season:
                queryset = queryset.filter(clothing_product__season=season)

        # Si c'est "Tissus" ou une de ses sous-catégories (jusqu'au niveau 3)
        elif (category.slug == 'tissus' or 
              (category.parent and category.parent.slug == 'tissus') or
              (category.parent and category.parent.parent and category.parent.parent.slug == 'tissus')):
            queryset = queryset.filter(fabric_product__isnull=False)
            
            fabric_type = self.request.GET.get('fabric_type')
            if fabric_type:
                queryset = queryset.filter(fabric_product__fabric_type=fabric_type)

            color = self.request.GET.get('color')
            if color:
                queryset = queryset.filter(fabric_product__color__name=color)

            quality = self.request.GET.get('quality')
            if quality:
                queryset = queryset.filter(fabric_product__quality=quality)

        # Si c'est "Articles culturels" ou une de ses sous-catégories (jusqu'au niveau 3)
        elif (category.slug in ['culture', 'articles-culturels'] or 
              (category.parent and category.parent.slug in ['culture', 'articles-culturels']) or
              (category.parent and category.parent.parent and category.parent.parent.slug in ['culture', 'articles-culturels'])):
            queryset = queryset.filter(cultural_product__isnull=False)
            
            author = self.request.GET.get('author')
            if author:
                queryset = queryset.filter(cultural_product__author__icontains=author)

            isbn = self.request.GET.get('isbn')
            if isbn:
                queryset = queryset.filter(cultural_product__isbn=isbn)

            date = self.request.GET.get('date')
            if date:
                queryset = queryset.filter(cultural_product__date=date)

        # Appliquer les filtres de prix pour toutes les catégories
        queryset = self.get_price_filters(queryset)

        # Appliquer les filtres génériques
        queryset = self.apply_generic_filters(queryset)

        return queryset
    
    def get_price_filters(self, queryset):
        """Applique les filtres de prix communs"""
        print("\n=== DEBUG PRICE FILTERS ===")
        print(f"Nombre de produits avant filtres de prix: {queryset.count()}")
        
        price_min = self.request.GET.get('price_min')
        if price_min:
            try:
                price_min = float(price_min)
                queryset = queryset.filter(price__gte=price_min)
                print(f"Filtre prix min: {price_min} - Produits restants: {queryset.count()}")
            except (ValueError, TypeError):
                print(f"Erreur de conversion du prix min: {price_min}")
        
        price_max = self.request.GET.get('price_max')
        if price_max:
            try:
                price_max = float(price_max)
                queryset = queryset.filter(price__lte=price_max)
                print(f"Filtre prix max: {price_max} - Produits restants: {queryset.count()}")
            except (ValueError, TypeError):
                print(f"Erreur de conversion du prix max: {price_max}")
        
        print(f"Nombre final de produits après filtres de prix: {queryset.count()}")
        print("=== FIN DEBUG PRICE FILTERS ===\n")
        return queryset
    
    def get_breadcrumbs(self, category):
        """Construit le fil d'Ariane"""
        breadcrumbs = []
        current = category
        while current and current.slug:  # Vérifier que le slug n'est pas vide
            breadcrumbs.insert(0, {
                'name': current.name,
                'url': reverse('suppliers:category_detail', kwargs={'slug': current.slug})
            })
            current = current.parent
        return breadcrumbs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_category()
        queryset = self.get_queryset()
        
        # Pagination
        page = self.request.GET.get('page', 1)
        paginator = Paginator(queryset, 12)  # 12 produits par page
        products = paginator.get_page(page)
        
        # Récupérer les marques pour la section téléphones (seulement si pas déjà fait par PhoneCategoryView)
        brands = []
        if category.slug == 'telephones' and not hasattr(self, 'phone_brands_processed'):
            brands = queryset.filter(phone__isnull=False).values('phone__brand').annotate(count=Count('id')).order_by('phone__brand')
        
        # Récupérer les méthodes de livraison
        shipping_methods = ShippingMethod.objects.all()
        
        # Récupérer les catégories enfants
        child_categories = category.children.all()
        has_child_categories = child_categories.exists()
        
        # Message pour les sous-catégories
        child_categories_message = "Produits des sous-catégories"
        
        # Vérifier si les produits sont filtrés
        is_filtered = any(key in self.request.GET for key in ['name', 'brand', 'category', 'supplier', 'condition', 'warranty', 'rating', 'promotion', 'shipping', 'popularity', 'weight_min', 'weight_max', 'dimensions', 'color', 'quality', 'fabric_type', 'author', 'publication_date'])
        
        context.update({
            'category': category,
            'products': products,
            'brands': brands,
            'shipping_methods': shipping_methods,
            'child_categories': child_categories,
            'has_child_categories': has_child_categories,
            'child_categories_message': child_categories_message,
            'is_filtered': is_filtered,
            'breadcrumbs': self.get_breadcrumbs(category),
        })
        
        # Envoyer l'événement PageView à Facebook
        category = self.get_category()
        if self.request.user.is_authenticated:
            user_data = {
                "email": self.request.user.email,
                "phone": getattr(self.request.user, 'phone', '')
            }
            
            facebook_conversions.send_pageview_event(
                user_data=user_data,
                content_name=f"Page Catégorie - {category.name}",
                content_category=category.name
            )
        else:
            # Pour les utilisateurs anonymes, envoyer sans données utilisateur
            facebook_conversions.send_pageview_event(
                content_name=f"Page Catégorie - {category.name}",
                content_category=category.name
            )
        
        return context
    
    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['suppliers/components/_product_grid.html']
        return [self.template_name]


class ClothingCategoryView(BaseCategoryView):
    """Vue spécialisée pour les catégories de vêtements"""
    
    def get_queryset(self):
        category = self.get_category()
        queryset = self.get_base_queryset()
        
        # Appliquer le filtre de garantie
        warranty = self.request.GET.get('warranty')
        if warranty:
            if warranty == 'yes':
                queryset = queryset.filter(has_warranty=True)
            elif warranty == 'no':
                queryset = queryset.filter(has_warranty=False)
        
        print("\n=== DEBUG CLOTHING CATEGORY ===")
        print(f"Catégorie: {category.name} (slug: {category.slug})")
        print(f"Parent: {category.parent.name if category.parent else 'None'}")
        print(f"Grand-parent: {category.parent.parent.name if category.parent and category.parent.parent else 'None'}")
        
        # Debug des types existants
        existing_materials = Product.objects.filter(
            clothing_product__isnull=False
        ).values_list('clothing_product__material', flat=True).distinct()
        print(f"Matériaux existants dans la base: {list(existing_materials)}")
        
        # Récupérer les IDs des catégories enfants
        child_ids = list(category.get_all_children_ids())
        print(f"IDs des catégories enfants: {child_ids}")
        
        # Appliquer les filtres selon le type de catégorie
        if category.slug == 'vetements':
            print("Cas 1: Catégorie principale (Vêtements)")
            # Pour la catégorie principale, on inclut tous les enfants
            category_ids = set([category.id] + child_ids)
            print(f"IDs des catégories concernées: {category_ids}")
            queryset = queryset.filter(
                clothing_product__isnull=False,
                category_id__in=category_ids
            )
        elif category.parent and category.parent.slug == 'vetements':
            # Vérifier si c'est un genre (H, F, U) ou un type de vêtement (Veste, Pantalon)
            if category.name in ['H', 'F', 'U']:
                print("Cas 2: Sous-catégorie genre (H, F, U)")
                # Pour les genres, on inclut tous les enfants
                category_ids = set([category.id] + child_ids)
                print(f"IDs des catégories concernées: {category_ids}")
                queryset = queryset.filter(
                    clothing_product__isnull=False,
                    clothing_product__gender=category.name,
                    category_id__in=category_ids
                )
            else:
                print("Cas 2bis: Sous-catégorie type (Veste, Pantalon, etc.)")
                # Pour les types, on inclut tous les enfants
                category_ids = set([category.id] + child_ids)
                print(f"IDs des catégories concernées: {category_ids}")
                queryset = queryset.filter(
                    clothing_product__isnull=False,
                    category_id__in=category_ids
                )
                print(f"Requête SQL: {queryset.query}")
        else:
            print("Cas 3: Autre catégorie")
            # Pour les autres catégories, on inclut la catégorie et ses enfants
            category_ids = set([category.id] + child_ids)
            print(f"IDs des catégories concernées: {category_ids}")
            queryset = queryset.filter(
                clothing_product__isnull=False,
                category_id__in=category_ids
            )
        
        print(f"Nombre de produits trouvés: {queryset.count()}")
        print("=== FIN DEBUG ===\n")
            
        # Appliquer les filtres supplémentaires
        queryset = self.apply_clothing_filters(queryset)
        return self.get_price_filters(queryset)
    
    def apply_clothing_filters(self, queryset):
        """Applique les filtres spécifiques aux vêtements"""
        gender = self.request.GET.get('gender')
        size = self.request.GET.get('size')
        color = self.request.GET.get('color')
        material = self.request.GET.get('material')
        style = self.request.GET.get('style')
        season = self.request.GET.get('season')
        
        print("\n=== DEBUG CLOTHING FILTERS ===")
        print(f"Filtres appliqués:")
        print(f"- Genre: {gender}")
        print(f"- Taille: {size}")
        print(f"- Couleur: {color}")
        print(f"- Matériau: {material}")
        print(f"- Style: {style}")
        print(f"- Saison: {season}")
        
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
            
        print(f"Nombre de produits après filtres: {queryset.count()}")
        print("=== FIN DEBUG FILTERS ===\n")
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        print("\n=== DEBUG CONTEXT DATA ===")
        
        # Récupérer tous les produits pour les filtres avec toutes les relations nécessaires
        all_products = Product.objects.all().select_related(
            'clothing_product'
        ).prefetch_related(
            'clothing_product__size',
            'clothing_product__color'
        ).distinct()
        
        print(f"Nombre de produits récupérés: {all_products.count()}")
        
        # Récupérer les genres disponibles et les formater
        gender_list = list(all_products.values_list('clothing_product__gender', flat=True).distinct())
        gender_mapping = {
            'H': 'Homme',
            'F': 'Femme',
            'U': 'Unisexe'
        }
        context['genders'] = [
            {
                'gender': g,
                'display_name': gender_mapping.get(g, g)
            } for g in sorted(set(filter(None, gender_list)))
        ]
        print(f"Genres disponibles: {context['genders']}")
        
        # Récupérer les tailles disponibles
        size_list = list(all_products.values_list(
            'clothing_product__size__name', 
            flat=True
        ).distinct())
        context['sizes'] = [{'size': s} for s in sorted(set(filter(None, size_list)))]
        print(f"Tailles disponibles: {context['sizes']}")
        
        # Récupérer les couleurs disponibles
        colors_list = all_products.values_list(
            'clothing_product__color__name', 
            'clothing_product__color__code'
        ).distinct()
        context['colors'] = [
            {
                'name': c[0],
                'code': c[1]
            } for c in sorted(set(filter(lambda x: x[0] is not None, colors_list)))
        ]
        print(f"Couleurs disponibles: {context['colors']}")
        
        # Récupérer les types disponibles
        material_list = list(all_products.values_list('clothing_product__material', flat=True).distinct())
        context['materials'] = [{'material': m} for m in sorted(set(filter(None, material_list)))]
        print(f"Matériaux disponibles: {context['materials']}")
        
        style_list = list(all_products.values_list('clothing_product__style', flat=True).distinct())
        context['styles'] = [{'style': s} for s in sorted(set(filter(None, style_list)))]
        print(f"Styles disponibles: {context['styles']}")
        
        season_list = list(all_products.values_list('clothing_product__season', flat=True).distinct())
        context['seasons'] = [{'season': s} for s in sorted(set(filter(None, season_list)))]
        print(f"Saisons disponibles: {context['seasons']}")
        
        # Filtres sélectionnés
        context['selected_gender'] = self.request.GET.get('gender', '')
        context['selected_size'] = self.request.GET.get('size', '')
        context['selected_color'] = self.request.GET.get('color', '')
        context['selected_material'] = self.request.GET.get('material', '')
        context['selected_style'] = self.request.GET.get('style', '')
        context['selected_season'] = self.request.GET.get('season', '')
        
        # Ajouter les informations sur les sous-catégories
        category = self.get_category()
        child_categories = category.children.all()
        if child_categories.exists():
            context['has_child_categories'] = True
            context['child_categories'] = child_categories
            context['child_categories_message'] = "Produits des sous-catégories :"
        
        # Formater les produits pour le template
        products = self.get_queryset()
        formatted_products = []
        for product in products:
            if hasattr(product, 'clothing_product'):
                formatted_products.append({
                    'product': product,
                    'clothing_product': product.clothing_product
                })
            else:
                formatted_products.append({
                    'product': product
                })
        context['products'] = formatted_products
        print(f"Nombre de produits formatés pour le template : {len(formatted_products)}")
        print("=== FIN DEBUG CONTEXT DATA ===\n")
        return context


class PhoneCategoryView(BaseCategoryView):
    """Vue spécialisée pour les catégories de téléphones"""
    
    def get_queryset(self):
        category = self.get_category()
        queryset = self.get_base_queryset()
        
        # Appliquer le filtre de garantie
        warranty = self.request.GET.get('warranty')
        if warranty:
            if warranty == 'yes':
                queryset = queryset.filter(has_warranty=True)
            elif warranty == 'no':
                queryset = queryset.filter(has_warranty=False)
        
        print("\n=== DEBUG PHONE CATEGORY ===")
        print(f"Catégorie: {category.name} (slug: {category.slug})")
        print(f"Parent: {category.parent.name if category.parent else 'None'}")
        print(f"Grand-parent: {category.parent.parent.name if category.parent and category.parent.parent else 'None'}")
        
        # Debug des marques existantes
        existing_brands = Product.objects.filter(
            phone__isnull=False
        ).values_list('phone__brand', flat=True).distinct()
        print(f"Marques existantes dans la base: {list(existing_brands)}")
        
        # Récupérer les IDs des catégories enfants
        child_ids = list(category.get_all_children_ids())
        print(f"IDs des catégories enfants: {child_ids}")
        
        # Appliquer les filtres selon le type de catégorie
        if category.slug == 'telephones':
            print("Cas 1: Catégorie principale (Téléphones)")
            # Pour la catégorie principale, on inclut tous les enfants
            category_ids = set([category.id] + child_ids)
            print(f"IDs des catégories concernées: {category_ids}")
            queryset = queryset.filter(
                phone__isnull=False,
                category_id__in=category_ids
            )
        elif category.parent and category.parent.slug == 'telephones':
            print("Cas 2: Sous-catégorie directe")
            # Pour les sous-catégories directes, on inclut tous les enfants
            category_ids = set([category.id] + child_ids)
            print(f"IDs des catégories concernées: {category_ids}")
            queryset = queryset.filter(
                phone__isnull=False,
                category_id__in=category_ids
            )
        elif category.parent and category.parent.parent and category.parent.parent.slug == 'telephones':
            print("Cas 3: Petit-fils")
            # Pour les petits-fils, on inclut uniquement la catégorie actuelle
            queryset = queryset.filter(
                phone__isnull=False,
                category=category
            )
        
        print(f"Nombre de produits trouvés: {queryset.count()}")
        print("=== FIN DEBUG ===\n")
            
        # Appliquer les filtres supplémentaires
        queryset = self.apply_phone_filters(queryset)
        return self.get_price_filters(queryset)
    
    def apply_phone_filters(self, queryset):
        """Applique les filtres spécifiques aux téléphones"""
        brand = self.request.GET.get('brand')
        model = self.request.GET.get('model')
        storage = self.request.GET.get('storage')
        ram = self.request.GET.get('ram')
        condition = self.request.GET.get('condition')
        promotion = self.request.GET.get('promotion')
        shipping = self.request.GET.get('shipping')
        sort = self.request.GET.get('sort')
        
        if brand:
            queryset = queryset.filter(phone__brand=brand)
        if model:
            queryset = queryset.filter(phone__model=model)
        if storage:
            queryset = queryset.filter(phone__storage=storage)
        if ram:
            queryset = queryset.filter(phone__ram=ram)
        if condition:
            queryset = queryset.filter(condition=condition)
        if promotion == 'yes':
            queryset = queryset.filter(discount_price__isnull=False, discount_price__lt=models.F('price'))
        elif promotion == 'no':
            queryset = queryset.filter(models.Q(discount_price__isnull=True) | models.Q(discount_price__gte=models.F('price')))
        if shipping:
            queryset = queryset.filter(shipping_methods__name=shipping)
        # Nouveau tri global
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'new':
            queryset = queryset.order_by('-created_at')
        elif sort == 'best_selling':
            queryset = queryset.order_by('-sales_count')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Marquer que les marques ont été traitées pour éviter les doublons
        self.phone_brands_processed = True
        
        print("\n=== DEBUG CONTEXT DATA ===")
        
        # Récupérer tous les produits pour les filtres avec toutes les relations nécessaires
        all_products = Product.objects.all().select_related(
            'phone',
            'phone__color'
        ).distinct()
        
        print(f"Nombre de produits récupérés: {all_products.count()}")
        
        # Récupérer les marques disponibles (normalisées)
        brands_list = list(all_products.values_list('phone__brand', flat=True).distinct())
        context['brands'] = [{'phone__brand': b} for b in sorted(set(filter(None, brands_list)))]
        print(f"Marques disponibles: {context['brands']}")
        
        # Récupérer les modèles disponibles
        models_list = list(all_products.values_list('phone__model', flat=True).distinct())
        context['models'] = [{'phone__model': m} for m in sorted(set(filter(None, models_list)))]
        print(f"Modèles disponibles: {context['models']}")
        
        # Récupérer les stockages disponibles
        storages_list = list(all_products.values_list('phone__storage', flat=True).distinct())
        context['storages'] = [{'phone__storage': s} for s in sorted(set(filter(None, storages_list)))]
        print(f"Stockages disponibles: {context['storages']}")
        
        # Récupérer les RAM disponibles
        rams_list = list(all_products.values_list('phone__ram', flat=True).distinct())
        context['rams'] = [{'phone__ram': str(r)} for r in sorted(set(filter(None, rams_list)))]
        print(f"RAM disponibles: {context['rams']}")
        
        # Récupérer les couleurs disponibles avec leurs codes
        colors_list = all_products.values_list(
            'phone__color__name',
            'phone__color__code'
        ).distinct()
        context['colors'] = [
            {
                'name': c[0],
                'code': c[1]
            } for c in sorted(set(filter(lambda x: x[0] is not None, colors_list)))
        ]
        print(f"Couleurs disponibles: {context['colors']}")
        
        # Filtres sélectionnés
        context['selected_brand'] = self.request.GET.get('brand', '')
        context['selected_model'] = self.request.GET.get('model', '')
        context['selected_storage'] = str(self.request.GET.get('storage', '')) if self.request.GET.get('storage') is not None else ''
        context['selected_ram'] = str(self.request.GET.get('ram', '')) if self.request.GET.get('ram') is not None else ''
        context['selected_price_min'] = self.request.GET.get('price_min', '')
        context['selected_price_max'] = self.request.GET.get('price_max', '')
        context['selected_condition'] = self.request.GET.get('condition', '')
        context['selected_warranty'] = self.request.GET.get('warranty', '')
        context['selected_promotion'] = self.request.GET.get('promotion', '')
        context['selected_sort'] = self.request.GET.get('sort', '')
        context['selected_shipping'] = self.request.GET.get('shipping', '')
        
        # Ajouter les informations sur les sous-catégories
        category = self.get_category()
        child_categories = category.children.all()
        if child_categories.exists():
            context['has_child_categories'] = True
            context['child_categories'] = child_categories
            context['child_categories_message'] = "Produits des sous-catégories :"
        
        # Formater les produits pour le template
        products = self.get_queryset()
        formatted_products = []
        for product in products:
            formatted_products.append({
                'product': product,
                'phone': product.phone
            })
        
        # Pagination
        paginator = Paginator(formatted_products, 20)  # 20 produits par page
        page = self.request.GET.get('page')
        try:
            products_page = paginator.page(page)
        except PageNotAnInteger:
            products_page = paginator.page(1)
        except EmptyPage:
            products_page = paginator.page(paginator.num_pages)
        
        context['products'] = products_page
        context['is_paginated'] = paginator.num_pages > 1
        context['page_obj'] = products_page
        
        print(f"Nombre de produits formatés pour le template : {len(formatted_products)}")
        print(f"Pagination : page {products_page.number} sur {paginator.num_pages}")
        print("=== FIN DEBUG CONTEXT DATA ===\n")
        return context


class FabricCategoryView(BaseCategoryView):
    """Vue spécialisée pour les catégories de tissus"""
    
    def get_queryset(self):
        print(f"[DEBUG] Paramètres GET reçus dans FabricCategoryView.get_queryset : {self.request.GET}")
        queryset = self.get_base_queryset().filter(fabric_product__isnull=False)
        
        print(f"Nombre initial de produits tissus: {queryset.count()}")
        
        # Appliquer le filtre de garantie
        warranty = self.request.GET.get('warranty')
        if warranty:
            if warranty == 'yes':
                queryset = queryset.filter(has_warranty=True)
            elif warranty == 'no':
                queryset = queryset.filter(has_warranty=False)
            print(f"Filtre garantie: {warranty} - Produits restants: {queryset.count()}")

        # Appliquer le filtre de condition
        condition = self.request.GET.get('condition')
        if condition:
            queryset = queryset.filter(condition=condition)
            print(f"Filtre condition: {condition} - Produits restants: {queryset.count()}")

        # Appliquer le filtre de promotion
        promotion = self.request.GET.get('promotion')
        if promotion == 'yes':
            queryset = queryset.filter(discount_price__isnull=False, discount_price__lt=models.F('price'))
            print(f"Filtre promotion: oui - Produits restants: {queryset.count()}")
        elif promotion == 'no':
            queryset = queryset.filter(models.Q(discount_price__isnull=True) | models.Q(discount_price__gte=models.F('price')))
            print(f"Filtre promotion: non - Produits restants: {queryset.count()}")

        # Appliquer le filtre de livraison
        shipping = self.request.GET.get('shipping')
        if shipping:
            queryset = queryset.filter(shipping_methods__name=shipping)
            print(f"Filtre livraison: {shipping} - Produits restants: {queryset.count()}")

        # Appliquer les filtres spécifiques aux tissus
        queryset = self.apply_fabric_filters(queryset)
        
        # Appliquer le tri global
        sort = self.request.GET.get('sort')
        if sort == 'price_asc':
            queryset = queryset.order_by('-is_available', 'price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-is_available', '-price')
        elif sort == 'new':
            queryset = queryset.order_by('-is_available', '-created_at')
        elif sort == 'best_selling':
            queryset = queryset.order_by('-is_available', '-sales_count')
        
        # Appliquer les filtres de prix
        queryset = self.get_price_filters(queryset)
        
        print(f"Nombre final de produits tissus: {queryset.count()}")
        return queryset
    
    def apply_fabric_filters(self, queryset):
        """Applique les filtres spécifiques aux tissus"""
        fabric_type = self.request.GET.get('fabric_type')
        color = self.request.GET.get('color')
        quality = self.request.GET.get('quality')
        
        if fabric_type:
            queryset = queryset.filter(fabric_product__fabric_type=fabric_type)
            print(f"Filtre type tissu: {fabric_type} - Produits restants: {queryset.count()}")
        if color:
            queryset = queryset.filter(fabric_product__color__name=color)
            print(f"Filtre couleur: {color} - Produits restants: {queryset.count()}")
        if quality:
            queryset = queryset.filter(fabric_product__quality=quality)
            print(f"Filtre qualité: {quality} - Produits restants: {queryset.count()}")
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Récupérer tous les produits pour les filtres avec toutes les relations nécessaires
        all_products = Product.objects.all().select_related(
            'fabric_product',
            'fabric_product__color'
        ).distinct()
        
        # Récupérer les types de tissus disponibles
        fabric_type_list = list(all_products.values_list('fabric_product__fabric_type', flat=True).distinct())
        context['fabric_types'] = [{'fabric_type': ft} for ft in sorted(set(filter(None, fabric_type_list)))]
        
        # Récupérer les couleurs disponibles avec leurs codes
        colors_list = all_products.values_list(
            'fabric_product__color__name',
            'fabric_product__color__code'
        ).distinct()
        context['colors'] = [
            {
                'name': c[0],
                'code': c[1]
            } for c in sorted(set(filter(lambda x: x[0] is not None, colors_list)))
        ]
        
        # Récupérer les qualités disponibles
        quality_list = list(all_products.values_list('fabric_product__quality', flat=True).distinct())
        context['qualities'] = [{'quality': q} for q in sorted(set(filter(None, quality_list)))]
        
        # Ajouter les méthodes de livraison
        context['shipping_methods'] = ShippingMethod.objects.all()
        
        # Persistance des sélections
        context['selected_fabric_type'] = self.request.GET.get('fabric_type', '')
        context['selected_color'] = self.request.GET.get('color', '')
        context['selected_quality'] = self.request.GET.get('quality', '')
        context['selected_price_min'] = self.request.GET.get('price_min', '')
        context['selected_price_max'] = self.request.GET.get('price_max', '')
        context['selected_condition'] = self.request.GET.get('condition', '')
        context['selected_warranty'] = self.request.GET.get('warranty', '')
        context['selected_promotion'] = self.request.GET.get('promotion', '')
        context['selected_sort'] = self.request.GET.get('sort', '')
        context['selected_shipping'] = self.request.GET.get('shipping', '')
        
        return context


class CulturalCategoryView(BaseCategoryView):
    """Vue spécialisée pour les catégories d'articles culturels"""
    
    def get_queryset(self):
        print(f"[DEBUG] Paramètres GET reçus dans CulturalCategoryView.get_queryset : {self.request.GET}")
        queryset = self.get_base_queryset().filter(cultural_product__isnull=False)
        
        print(f"Nombre initial de produits culturels: {queryset.count()}")
        
        # Appliquer le filtre de garantie
        warranty = self.request.GET.get('warranty')
        if warranty:
            if warranty == 'yes':
                queryset = queryset.filter(has_warranty=True)
            elif warranty == 'no':
                queryset = queryset.filter(has_warranty=False)
            print(f"Filtre garantie: {warranty} - Produits restants: {queryset.count()}")

        # Appliquer le filtre de condition
        condition = self.request.GET.get('condition')
        if condition:
            queryset = queryset.filter(condition=condition)
            print(f"Filtre condition: {condition} - Produits restants: {queryset.count()}")

        # Appliquer le filtre de promotion
        promotion = self.request.GET.get('promotion')
        if promotion == 'yes':
            queryset = queryset.filter(discount_price__isnull=False, discount_price__lt=models.F('price'))
            print(f"Filtre promotion: oui - Produits restants: {queryset.count()}")
        elif promotion == 'no':
            queryset = queryset.filter(models.Q(discount_price__isnull=True) | models.Q(discount_price__gte=models.F('price')))
            print(f"Filtre promotion: non - Produits restants: {queryset.count()}")

        # Appliquer le filtre de livraison
        shipping = self.request.GET.get('shipping')
        if shipping:
            queryset = queryset.filter(shipping_methods__name=shipping)
            print(f"Filtre livraison: {shipping} - Produits restants: {queryset.count()}")

        # Appliquer les filtres spécifiques aux articles culturels
        queryset = self.apply_cultural_filters(queryset)
        
        # Appliquer le tri global
        sort = self.request.GET.get('sort')
        if sort == 'price_asc':
            queryset = queryset.order_by('-is_available', 'price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-is_available', '-price')
        elif sort == 'new':
            queryset = queryset.order_by('-is_available', '-created_at')
        elif sort == 'best_selling':
            queryset = queryset.order_by('-is_available', '-sales_count')
        
        # Appliquer les filtres de prix
        queryset = self.get_price_filters(queryset)
        
        print(f"Nombre final de produits culturels: {queryset.count()}")
        return queryset
    
    def apply_cultural_filters(self, queryset):
        """Applique les filtres spécifiques aux articles culturels"""
        author = self.request.GET.get('author')
        isbn = self.request.GET.get('isbn')
        date = self.request.GET.get('date')
        
        if author:
            queryset = queryset.filter(cultural_product__author__icontains=author)
            print(f"Filtre auteur: {author} - Produits restants: {queryset.count()}")
        if isbn:
            queryset = queryset.filter(cultural_product__isbn=isbn)
            print(f"Filtre ISBN: {isbn} - Produits restants: {queryset.count()}")
        if date:
            # Convertir la date française en format de base de données
            db_date = convert_french_date_to_db_format(date)
            if db_date:
                queryset = queryset.filter(cultural_product__date=db_date)
                print(f"Filtre date: {date} -> {db_date} - Produits restants: {queryset.count()}")
            else:
                print(f"Impossible de convertir la date: {date}")
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Récupérer tous les produits pour les filtres
        all_products = Product.objects.all().select_related(
            'cultural_product'
        )
        
        # Récupérer les auteurs disponibles
        author_list = list(all_products.values_list('cultural_product__author', flat=True).distinct())
        context['authors'] = [{'author': a} for a in sorted(set(filter(None, author_list)))]
        
        # Récupérer les ISBN disponibles
        isbn_list = list(all_products.values_list('cultural_product__isbn', flat=True).distinct())
        context['isbns'] = [{'isbn': i} for i in sorted(set(filter(None, isbn_list)))]
        
        # Récupérer les dates disponibles
        date_list = list(all_products.values_list('cultural_product__date', flat=True).distinct())
        # Formater les dates au format français pour l'affichage
        formatted_dates = []
        for date_obj in sorted(set(filter(None, date_list))):
            if date_obj:
                # Formater la date au format français
                french_date = date_obj.strftime("%d %B %Y")
                # Remplacer les mois anglais par les mois français
                mois_mapping = {
                    'January': 'janvier', 'February': 'février', 'March': 'mars', 'April': 'avril',
                    'May': 'mai', 'June': 'juin', 'July': 'juillet', 'August': 'août',
                    'September': 'septembre', 'October': 'octobre', 'November': 'novembre', 'December': 'décembre'
                }
                for eng, fr in mois_mapping.items():
                    french_date = french_date.replace(eng, fr)
                formatted_dates.append({'date': french_date})
        context['dates'] = formatted_dates
        
        # Ajouter les méthodes de livraison
        context['shipping_methods'] = ShippingMethod.objects.all()
        
        # Persistance des sélections
        context['selected_author'] = self.request.GET.get('author', '')
        context['selected_isbn'] = self.request.GET.get('isbn', '')
        context['selected_date'] = self.request.GET.get('date', '')
        context['selected_price_min'] = self.request.GET.get('price_min', '')
        context['selected_price_max'] = self.request.GET.get('price_max', '')
        context['selected_condition'] = self.request.GET.get('condition', '')
        context['selected_warranty'] = self.request.GET.get('warranty', '')
        context['selected_promotion'] = self.request.GET.get('promotion', '')
        context['selected_sort'] = self.request.GET.get('sort', '')
        context['selected_shipping'] = self.request.GET.get('shipping', '')
        
        return context


class GenericCategoryView(BaseCategoryView):
    """Vue spécialisée pour les catégories génériques comme 'Tous les produits' et 'Bricolage'"""
    
    def get_queryset(self):
        print(f"[DEBUG] Paramètres GET reçus dans GenericCategoryView.get_queryset : {self.request.GET}")
        category = self.get_category()
        queryset = self.get_base_queryset()
        
        print("\n=== DEBUG GENERIC CATEGORY ===")
        print(f"Catégorie: {category.name} (slug: {category.slug})")
        print(f"Nombre initial de produits: {queryset.count()}")
        
        # Appliquer les filtres selon le type de catégorie
        if category.slug == 'tous-les-produits':
            print("Cas 1: Catégorie principale (Tous les produits)")
            # Pour la catégorie principale, on inclut tous les produits
            queryset = queryset
            print(f"Nombre de produits après filtres de base: {queryset.count()}")
            
            # Appliquer le filtre de catégorie principale
            main_category = self.request.GET.get('main_category')
            if main_category:
                cat = Category.objects.filter(slug=main_category).first()
                print(f"[DEBUG] main_category param: {main_category}, cat found: {cat}")
                if cat:
                    all_ids = cat.get_all_children_ids()
                    print(f"[DEBUG] IDs filtrés pour la catégorie '{cat.name}': {all_ids}")
                    queryset = queryset.filter(category_id__in=all_ids)
                    print(f"Nombre de produits après filtre main_category: {queryset.count()}")
        else:
            print("Cas 2: Catégorie générique (ex: Bricolage)")
            # Pour les autres catégories génériques, on inclut la catégorie et ses enfants
            child_ids = list(category.get_all_children_ids())
            category_ids = set([category.id] + child_ids)
            print(f"IDs des catégories concernées: {category_ids}")
            queryset = queryset.filter(
                category_id__in=category_ids
            )
            print(f"Nombre de produits après filtres de catégorie: {queryset.count()}")
        
        # Appliquer les filtres génériques
        queryset = self.apply_generic_filters(queryset)
        print(f"Nombre de produits après filtres génériques: {queryset.count()}")
        
        # Appliquer les filtres de prix
        queryset = self.get_price_filters(queryset)
        print(f"Nombre final de produits: {queryset.count()}")
        print("=== FIN DEBUG ===\n")
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_category()
        queryset = self.get_queryset()
        
        print("\n=== DEBUG GENERIC CONTEXT DATA ===")
        print(f"Catégorie: {category.name} (slug: {category.slug})")
        print(f"Nombre total de produits avant pagination: {queryset.count()}")
        
        # Pagination
        page = self.request.GET.get('page', 1)
        try:
            page = int(page)
        except (TypeError, ValueError):
            page = 1
            
        paginator = Paginator(queryset, 12)  # 12 produits par page
        try:
            products = paginator.page(page)
        except:
            products = paginator.page(1)
            
        print(f"Page actuelle: {page}")
        print(f"Nombre de pages: {paginator.num_pages}")
        print(f"Produits sur la page actuelle: {len(products)}")
        
        # Récupérer les catégories principales avec leurs sous-catégories
        main_categories = Category.objects.filter(
            is_main=True,
            parent__isnull=True
        ).annotate(
            available_products_count=Count('products')
        ).order_by('order', 'name')
        
        # Construire la hiérarchie des catégories
        categories_hierarchy = {}
        for main_cat in main_categories:
            categories_hierarchy[main_cat.id] = {
                'category': main_cat,
                'subcategories': []
            }
            
            for subcat in main_cat.children.all():
                subcategory_data = {
                    'subcategory': subcat,
                    'subsubcategories': list(subcat.children.all())
                }
                categories_hierarchy[main_cat.id]['subcategories'].append(subcategory_data)
        
        # Ajouter les catégories et leur hiérarchie au contexte
        context.update({
            'category': category,
            'products': products,
            'main_categories': main_categories,
            'categories_hierarchy': categories_hierarchy,
            'paginator': paginator,
            'is_paginated': products.has_other_pages(),
            'page_obj': products,
        })
        
        # Récupérer tous les produits pour les filtres
        all_products = Product.objects.all().select_related(
            'category'
        ).distinct()
        
        # Récupérer les marques disponibles
        brands_list = list(all_products.values_list('brand', flat=True).distinct())
        context['brands'] = [{'brand': b} for b in sorted(set(filter(None, brands_list)))]
        
        # Récupérer les catégories disponibles pour les filtres
        categories_list = Category.objects.all().values_list('name', flat=True).distinct()
        context['filter_categories'] = [{'name': c} for c in sorted(set(filter(None, categories_list)))]
        
        # Récupérer les conditions disponibles
        conditions_list = list(all_products.values_list('condition', flat=True).distinct())
        context['conditions'] = [{'condition': c} for c in sorted(set(filter(None, conditions_list)))]
        
        # Filtres sélectionnés
        context['selected_brand'] = self.request.GET.get('brand', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_condition'] = self.request.GET.get('condition', '')
        context['selected_warranty'] = self.request.GET.get('warranty', '')
        context['selected_promotion'] = self.request.GET.get('promotion', '')
        context['selected_sort'] = self.request.GET.get('sort', '')
        
        # Ajouter les sous-catégories si c'est une catégorie principale
        if category.is_main:
            context['subcategories'] = category.children.all().prefetch_related('children')
        
        # Si c'est la catégorie "Tous les produits" ou une de ses sous-catégories
        if category.slug == 'tous-les-produits' or (category.parent and category.parent.slug == 'tous-les-produits'):
            context.update({
                'selected_main_category': self.request.GET.get('main_category', ''),
                'main_categories': Category.objects.filter(is_main=True, parent__isnull=True).exclude(slug='tous-les-produits')
            })
            print("Mode: Tous les produits ou sous-catégorie")
            print("Filtres disponibles: catégorie principale")
        
        context['shipping_methods'] = ShippingMethod.objects.all()
        context['selected_shipping'] = self.request.GET.get('shipping', '')
        context['main_categories'] = Category.objects.filter(is_main=True, parent__isnull=True).exclude(slug='tous-les-produits')
        context['selected_main_category'] = self.request.GET.get('main_category', '')
        
        print("=== FIN DEBUG CONTEXT DATA ===\n")
        return context


class CategoryListView(TemplateView):
    template_name = 'suppliers/category_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nos catégories'
        
        # Récupérer les catégories principales (is_main=True)
        main_categories = Category.objects.filter(
            is_main=True
        ).annotate(
            available_products_count=Count('products')
        ).order_by('order', 'name')

        # Récupérer les sous-catégories (non principales)
        sub_categories = Category.objects.filter(
            is_main=False
        ).annotate(
            available_products_count=Count('products')
        ).order_by('order', 'name')

        context['main_categories'] = main_categories
        context['sub_categories'] = sub_categories
        
        # Envoyer l'événement PageView à Facebook
        if self.request.user.is_authenticated:
            user_data = {
                "email": self.request.user.email,
                "phone": getattr(self.request.user, 'phone', '')
            }
            
            facebook_conversions.send_pageview_event(
                user_data=user_data,
                content_name="Page Liste des Catégories BoliBana",
                content_category="Navigation"
            )
        else:
            # Pour les utilisateurs anonymes, envoyer sans données utilisateur
            facebook_conversions.send_pageview_event(
                content_name="Page Liste des Catégories BoliBana",
                content_category="Navigation"
            )
        
        return context


class CategoryViewFactory:
    """Factory pour créer la vue appropriée selon le type de catégorie"""
    
    @staticmethod
    def get_view(request, *args, **kwargs):
        category_slug = kwargs.get('slug')
        category = get_object_or_404(Category, slug=category_slug)
        
        print("\n=== DEBUG CATEGORY VIEW FACTORY ===")
        print(f"Catégorie: {category.name} (slug: {category.slug})")
        print(f"Parent: {category.parent.name if category.parent else 'None'}")
        print(f"Grand-parent: {category.parent.parent.name if category.parent and category.parent.parent else 'None'}")
        
        # Déterminer le type de catégorie
        if category.slug in ['tous-les-produits', 'bricolage']:
            print("Vue: GenericCategoryView")
            return GenericCategoryView.as_view()(request, *args, **kwargs)
            
        # Vérifier si c'est une catégorie de vêtements
        if (category.slug == 'vetements' or 
            (category.parent and category.parent.slug == 'vetements') or
            (category.parent and category.parent.parent and category.parent.parent.slug == 'vetements')):
            print("Vue: ClothingCategoryView")
            return ClothingCategoryView.as_view()(request, *args, **kwargs)
            
        # Vérifier si c'est une catégorie de téléphones
        if (category.slug == 'telephones' or 
            (category.parent and category.parent.slug == 'telephones') or
            (category.parent and category.parent.parent and category.parent.parent.slug == 'telephones')):
            print("Vue: PhoneCategoryView")
            return PhoneCategoryView.as_view()(request, *args, **kwargs)
            
        # Vérifier si c'est une catégorie de tissus
        if (category.slug == 'tissus' or 
            (category.parent and category.parent.slug == 'tissus') or
            (category.parent and category.parent.parent and category.parent.parent.slug == 'tissus')):
            print("Vue: FabricCategoryView")
            return FabricCategoryView.as_view()(request, *args, **kwargs)
            
        # Vérifier si c'est une catégorie culturelle
        if (category.slug == 'culture' or 
            category.slug == 'articles-culturels' or
            (category.parent and category.parent.slug == 'culture') or
            (category.parent and category.parent.parent and category.parent.parent.slug == 'culture')):
            print("Vue: CulturalCategoryView")
            return CulturalCategoryView.as_view()(request, *args, **kwargs)
            
        # Par défaut, utiliser la vue générique
        print("Vue: GenericCategoryView (par défaut)")
        print("=== FIN DEBUG CATEGORY VIEW FACTORY ===\n")
        return GenericCategoryView.as_view()(request, *args, **kwargs) 