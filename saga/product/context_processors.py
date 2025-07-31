from .models import Category
from django.db.models import Prefetch



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
    Optimisé pour charger toutes les catégories en une seule requête.
    """
    from product.models import Phone
    
    # Récupérer toutes les catégories principales avec leurs sous-catégories en une seule requête
    main_categories = Category.objects.filter(
        parent__isnull=True
    ).prefetch_related(
        Prefetch(
            'children',
            queryset=Category.objects.all().prefetch_related(
                Prefetch(
                    'children',
                    queryset=Category.objects.all()
                )
            )
        )
    ).order_by('order', 'name')

    # Construire la hiérarchie des catégories
    categories_hierarchy = {}
    for main_cat in main_categories:
        categories_hierarchy[main_cat.id] = {
            'category': main_cat,
            'subcategories': []
        }
        
        # Si c'est la catégorie Téléphones, utiliser les marques au lieu des sous-catégories
        if main_cat.slug == 'telephones':
            # Récupérer les marques de téléphones avec leurs modèles populaires
            phone_brands_data = Phone.objects.values('brand', 'model').distinct().order_by('brand', 'model')
            
            # Grouper par marque
            brands_dict = {}
            for phone_data in phone_brands_data:
                brand = phone_data['brand']
                model = phone_data['model']
                
                if brand and brand != 'Inconnu':
                    if brand not in brands_dict:
                        brands_dict[brand] = []
                    if model and model != 'Inconnu':
                        brands_dict[brand].append(model)
            
            # Créer la structure pour chaque marque
            for brand, models in brands_dict.items():
                # Limiter à 5 modèles les plus populaires par marque
                popular_models = models[:5]
                
                brand_data = {
                    'subcategory': type('Brand', (), {
                        'name': brand,
                        'slug': brand.lower().replace(' ', '-'),
                        'is_brand': True
                    })(),
                    'subsubcategories': [
                        type('Model', (), {
                            'name': model,
                            'slug': f"{brand.lower().replace(' ', '-')}-{model.lower().replace(' ', '-')}",
                            'is_model': True
                        })() for model in popular_models
                    ],
                    'is_brand': True
                }
                categories_hierarchy[main_cat.id]['subcategories'].append(brand_data)
        else:
            # Pour les autres catégories, utiliser les sous-catégories normales
            for subcat in main_cat.children.all():
                subcategory_data = {
                    'subcategory': subcat,
                    'subsubcategories': list(subcat.children.all().order_by('order', 'name')),
                    'is_brand': False
                }
                categories_hierarchy[main_cat.id]['subcategories'].append(subcategory_data)

    return {
        'dropdown_categories': main_categories,
        'dropdown_categories_hierarchy': categories_hierarchy
    }

