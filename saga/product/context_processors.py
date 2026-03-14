from .models import Category
from django.db.models import Prefetch
import logging

logger = logging.getLogger(__name__)



def categories_processor(request):
    # Récupérer les catégories principales avec leurs sous-catégories en une seule requête
    categories = Category.objects.filter(parent__isnull=True).prefetch_related(
        'children__children'  # Optimisation des requêtes avec prefetch_related
    ).order_by('order', 'name')
    
    # Créer un dictionnaire pour stocker la hiérarchie par ID
    categories_hierarchy = {}
    
    # Pour chaque catégorie principale
    for category in categories:
        categories_hierarchy[category.id] = {
            'category': category,
            'subcategories': {},
            'subsubcategories': {}
        }
        
        # Récupérer les sous-catégories
        for subcategory in category.children.all():
            categories_hierarchy[category.id]['subcategories'][subcategory.id] = {
                'subcategory': subcategory,
                'subsubcategories': list(subcategory.children.all().order_by('order', 'name'))
            }
    
    return {
        "categories": categories,
        "categories_hierarchy": categories_hierarchy,
    }


def subcategories_processor(request):
    # Récupérer les catégories principales
    main_categories = Category.objects.filter(parent__isnull=True)
    
    # Créer un dictionnaire pour stocker les sous-catégories par parent
    subcategories_by_parent = {}
    
    # Pour chaque catégorie principale, récupérer ses sous-catégories
    for category in main_categories:
        subcategories = Category.objects.filter(parent=category)
        subcategories_by_parent[category.slug] = {
            'category': category,
            'subcategories': subcategories,
            'subsubcategories': {}
        }
        
        # Pour chaque sous-catégorie, récupérer ses sous-sous-catégories
        for subcategory in subcategories:
            subsubcategories = Category.objects.filter(parent=subcategory)
            subcategories_by_parent[category.slug]['subsubcategories'][subcategory.slug] = subsubcategories
    
    return {
        "subcategories_by_parent": subcategories_by_parent,
    }




def categories_processor_high_tech(request):
    # Liste des noms des catégories parentales
    parent_categories = ["Sous-catégories High Tech", "Accessoires High Tech", "Marques High Tech"]

    # Récupérer les catégories parentales en une seule requête
    parents = {cat.name: cat for cat in Category.objects.filter(name__in=parent_categories)}

    # Fonction utilitaire pour récupérer les enfants d'une catégorie donnée
    def get_children(category_name):
        parent = parents.get(category_name)
        return Category.objects.filter(parent=parent) if parent else Category.objects.none()

    # Générer les sous-catégories
    return {
        "subcategory_ht": get_children("Sous-catégories High Tech"),
        "accessoires_ht": get_children("Accessoires High Tech"),
        "brands_ht": get_children("Marques High Tech"),
    }


def category_processor_maison(request):
    # Liste des noms des catégories parentales
    parent_categories = ["Sous-catégories Maison", "Accessoires Maison", "Marques Maison"]

    # Récupérer les catégories parentales en une seule requête
    parents = {cat.name: cat for cat in Category.objects.filter(name__in=parent_categories)}

    # Fonction utilitaire pour récupérer les enfants d'une catégorie donnée
    def get_children(category_name):
        parent = parents.get(category_name)
        return Category.objects.filter(parent=parent) if parent else Category.objects.none()

    # Générer les sous-catégories
    return {
        "subcategory_maison": get_children("Sous-catégories Maison"),
        "accessoires_maison": get_children("Accessoires Maison"),
        "brands_maison": get_children("Marques Maison"),
    }


def categories_processor_quincaillerie(request):
    # Liste des noms des catégories parentales
    parent_categories = ["Sous-catégories Quincaillerie", "Marques Quincaillerie"]

    # Récupérer les catégories parentales en une seule requête
    parents = {cat.name: cat for cat in Category.objects.filter(name__in=parent_categories)}

    # Fonction utilitaire pour récupérer les enfants d'une catégorie donnée
    def get_children(category_name):
        parent = parents.get(category_name)
        return Category.objects.filter(parent=parent) if parent else Category.objects.none()

    # Générer les sous-catégories
    return {
        "subcategory_quincaillerie": get_children("Sous-catégories Quincaillerie"),
        "brands_quincaillerie": get_children("Marques Quincaillerie"),
    }


def categrpies_processor_espace_culturel(request):
    # Liste des noms des catégories parentales
    parent_categories = ["Sous-catégories Espace Culturel", "E-learning"]

    # Récupérer les catégories parentales en une seule requête
    parents = {cat.name: cat for cat in Category.objects.filter(name__in=parent_categories)}

    # Fonction utilitaire pour récupérer les enfants d'une catégorie donnée
    def get_children(category_name):
        parent = parents.get(category_name)
        return Category.objects.filter(parent=parent) if parent else Category.objects.none()

    # Générer les sous-catégories
    return {
        "subcategory_espace_culturel": get_children("Sous-catégories Espace Culturel"),
        "e_learning_espace_culturel": get_children("E-learning"),
    }


def dropdown_categories_processor(request):
    """
    Context processor pour gérer les catégories dans le menu déroulant.
    Affiche uniquement les catégories de niveau 0 (premier niveau), organisées par rayon_type.
    """
    from product.models import Phone
    from product.utils import extract_phone_series, normalize_phone_series
    from inventory.models import ExternalCategory
    
    from django.db.models import Q
    
    # Fonction de tri personnalisée pour les catégories B2B
    def get_sort_key(category):
        """Retourne une clé de tri : (rayon_type, level, order, name)"""
        rayon_type = category.rayon_type or ''
        level = category.level if category.level is not None else 999
        order = category.order if category.order is not None else 999
        name = category.name or ''
        return (rayon_type, level, order, name)
    
    # Récupérer UNIQUEMENT les catégories réellement synchronisées (mapping ExternalCategory)
    # Filtrer par level=0 OU (level is None ET external_parent_id is None)
    main_categories = Category.objects.filter(
        external_category__isnull=False
    ).filter(
        Q(level=0) | (Q(level__isnull=True) & Q(external_category__external_parent_id__isnull=True))
    ).select_related('external_category').order_by('rayon_type', 'order', 'name')
    
    # Trier les catégories principales selon rayon_type, level, order, name
    main_categories = sorted(main_categories, key=get_sort_key)
    
    # Récupérer toutes les catégories B2B réellement synchronisées pour trouver les enfants
    all_b2b_categories = Category.objects.filter(
        external_category__isnull=False
    ).select_related('external_category')
    
    # Fonction récursive pour construire la hiérarchie complète (tous les niveaux)
    def build_category_hierarchy(category, all_categories, parent_external_id=None, current_level=0, max_depth=10):
        """
        Construit récursivement la hiérarchie des catégories.
        Gère tous les niveaux (1, 2, 3, etc.)
        """
        if current_level >= max_depth:
            return []
        
        # S'assurer que la catégorie a un slug
        if not category.slug:
            from django.utils.text import slugify
            base_slug = slugify(category.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exclude(id=category.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            category.slug = slug
            category.save(update_fields=['slug'])
        
        # Trouver les enfants de cette catégorie
        children = []
        category_external_id = None
        
        if hasattr(category, 'external_category') and category.external_category:
            category_external_id = category.external_category.external_id
        
        # Méthode 1: Vérifier par external_parent_id
        if category_external_id is not None:
            for cat in all_categories:
                if cat.id == category.id:
                    continue
                if hasattr(cat, 'external_category') and cat.external_category:
                    if cat.external_category.external_parent_id == category_external_id:
                        children.append(cat)
        
        # Méthode 2: Si aucune trouvée, vérifier par level et rayon_type
        if not children and category.level is not None:
            expected_level = category.level + 1
            for cat in all_categories:
                if cat.id == category.id:
                    continue
                if cat.level == expected_level and cat.rayon_type == category.rayon_type:
                    # Vérifier aussi par external_parent_id si disponible
                    if category_external_id and hasattr(cat, 'external_category') and cat.external_category:
                        if cat.external_category.external_parent_id == category_external_id:
                            if cat not in children:
                                children.append(cat)
                    elif cat not in children:
                        children.append(cat)
        
        # Trier les enfants
        children = sorted(children, key=get_sort_key)
        
        # Construire récursivement la structure pour chaque enfant
        subcategories_data = []
        for child in children:
            child_data = {
                'subcategory': child,
                'subsubcategories': build_category_hierarchy(
                    child, 
                    all_categories, 
                    category_external_id if hasattr(category, 'external_category') and category.external_category else None,
                    current_level + 1,
                    max_depth
                ),
                'is_brand': False,
                'level': child.level if child.level is not None else current_level + 1
            }
            subcategories_data.append(child_data)
        
        return subcategories_data
    
    # Construire la hiérarchie avec les enfants (tous les niveaux)
    categories_hierarchy = {}
    
    for main_cat in main_categories:
        categories_hierarchy[main_cat.id] = {
            'category': main_cat,
            'subcategories': []
        }
        
        # Si c'est la catégorie Téléphones, utiliser les séries au lieu des modèles individuels
        if main_cat.slug == 'telephones':
            from django.db.models import Count
            
            # Récupérer les marques avec le nombre de produits par marque
            brands_with_count = Phone.objects.values('brand').annotate(
                product_count=Count('product')
            ).filter(
                brand__isnull=False
            ).exclude(
                brand='Inconnu'
            ).order_by('-product_count', 'brand')
            
            # Limiter à 8 marques les plus populaires pour éviter la surcharge
            top_brands = brands_with_count[:8]
            
            for brand_data in top_brands:
                brand = brand_data['brand']
                product_count = brand_data['product_count']
                
                # Récupérer tous les modèles pour cette marque
                all_models = Phone.objects.filter(
                    brand=brand
                ).values('model').filter(
                    model__isnull=False
                ).exclude(
                    model='Inconnu'
                )
                
                # Grouper les modèles par série
                series_groups = {}
                for model_data in all_models:
                    model_name = model_data['model']
                    series = extract_phone_series(model_name)
                    
                    if series:
                        if series not in series_groups:
                            series_groups[series] = []
                        series_groups[series].append(model_name)
                
                # Créer la structure pour chaque série de cette marque
                for series_name, models in series_groups.items():
                    normalized_series = normalize_phone_series(series_name)
                    
                    # Compter le nombre total de produits pour cette série
                    series_product_count = Phone.objects.filter(
                        brand=brand,
                        model__in=models
                    ).count()
                    
                    # Créer la structure pour cette série
                    series_data = {
                        'subcategory': type('Series', (), {
                            'name': f"{brand} {normalized_series}",
                            'slug': f"{brand.lower().replace(' ', '-')}-{series_name.lower()}",
                            'is_brand': True,
                            'is_series': True,
                            'product_count': series_product_count
                        })(),
                        'subsubcategories': [
                            type('Model', (), {
                                'name': model_name,
                                'slug': f"{brand.lower().replace(' ', '-')}-{model_name.lower().replace(' ', '-')}",
                                'is_model': True,
                                'product_count': Phone.objects.filter(
                                    brand=brand,
                                    model=model_name
                                ).count()
                            })() for model_name in sorted(models)[:4]  # Limiter à 4 modèles par série
                        ],
                        'is_brand': True,
                        'is_series': True,
                        'total_models': len(models)
                    }
                    categories_hierarchy[main_cat.id]['subcategories'].append(series_data)
        else:
            # Pour les catégories B2B, utiliser la fonction récursive pour construire toute la hiérarchie
            main_external_id = None
            if hasattr(main_cat, 'external_category') and main_cat.external_category:
                main_external_id = main_cat.external_category.external_id
            
            # Construire récursivement toute la hiérarchie (niveaux 1, 2, 3, etc.)
            subcategories_data = build_category_hierarchy(
                main_cat,
                all_b2b_categories,
                main_external_id,
                current_level=0,
                max_depth=10  # Limite de profondeur pour éviter les boucles infinies
            )
            
            categories_hierarchy[main_cat.id]['subcategories'] = subcategories_data

    # Grouper les catégories B2B par rayon_type pour l'affichage dans le dropdown
    # Toutes les catégories sont déjà de niveau 0
    categories_by_rayon = {}
    
    # Séparer les catégories avec rayon_type et celles sans
    categories_with_rayon = []
    categories_without_rayon = []
    
    for category in main_categories:
        if category.rayon_type:
            categories_with_rayon.append(category)
        else:
            categories_without_rayon.append(category)
    
    # Grouper les catégories avec rayon_type
    # Éviter les duplications en utilisant distinct() sur le rayon_type
    seen_rayon_types = set()
    for category in categories_with_rayon:
        rayon_type = category.rayon_type.strip() if category.rayon_type else ''
        # Normaliser le rayon_type (première lettre en majuscule)
        if rayon_type:
            rayon_type_normalized = ' '.join(word.capitalize() for word in rayon_type.split('_'))
        else:
            rayon_type_normalized = 'Autres'
        
        # Vérifier si le nom de la catégorie correspond au rayon_type (pour éviter duplication)
        category_name_normalized = category.name.strip()
        rayon_type_from_name = ' '.join(word.capitalize() for word in category_name_normalized.lower().replace(' ', '_').split('_'))
        
        if rayon_type_normalized not in categories_by_rayon:
            categories_by_rayon[rayon_type_normalized] = []
        categories_by_rayon[rayon_type_normalized].append(category)
    
    # Pour les catégories sans rayon_type, les grouper par leur parent ou créer un groupe "Autres"
    # Mais d'abord, vérifier si elles ont des enfants pour créer une hiérarchie
    if categories_without_rayon:
        # Si toutes les catégories sans rayon_type sont au même niveau (sans parent),
        # les mettre dans "Autres"
        # Sinon, organiser par hiérarchie
        
        # Mettre toutes dans "Autres" pour l'instant, mais organisées hiérarchiquement
        if 'Autres' not in categories_by_rayon:
            categories_by_rayon['Autres'] = []
        categories_by_rayon['Autres'].extend(sorted(categories_without_rayon, key=get_sort_key))
    
    # Trier les catégories dans chaque rayon_type selon level, order, name
    for rayon_type in categories_by_rayon:
        categories_by_rayon[rayon_type] = sorted(
            categories_by_rayon[rayon_type],
            key=get_sort_key
        )

    return {
        'dropdown_categories': main_categories,
        'dropdown_categories_hierarchy': categories_hierarchy,
        'categories_by_rayon': categories_by_rayon
    }

