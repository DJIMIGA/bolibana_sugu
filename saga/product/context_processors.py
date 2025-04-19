from .models import Category



def categories_processor(request):
    # Récupérer les catégories principales avec leurs sous-catégories en une seule requête
    categories = Category.objects.filter(parent__isnull=True).prefetch_related(
        'children__children'  # Optimisation des requêtes avec prefetch_related
    )
    
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
                'subsubcategories': list(subcategory.children.all())
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


# def categories_processor(request):
#     # Récupérer les catégories principales (sans parent), exclure certains IDs
#     categories = Category.objects.filter(parent__isnull=True)
#     categories = categories.filter(id__in=[1, 4, 5])
#
#     # Récupérer la catégorie "Vêtements" (parent)
#     vetements_category = Category.objects.filter(name="Vêtements").first()
#     # Si la catégorie "Vêtements" existe, récupérer ses enfants associés au genre "Femme"
#     if vetements_category:
#         clovings_women = Category.objects.filter(parent=vetements_category, genders__name="F")
#         clovings_men = Category.objects.filter(parent=vetements_category, genders__name="H")
#     else:
#         clovings_women = Category.objects.none()  # Retourner un queryset vide si "Vêtements" n'existe pas
#         clovings_men = Category.objects.none()
#
#     accessoires_category = Category.objects.filter(name="Accessoires").first()
#     if accessoires_category:
#         accessoires_womens = Category.objects.filter(parent=accessoires_category, genders__name="F")
#         accessoires_mens = Category.objects.filter(parent=accessoires_category, genders__name="H")
#
#     else:
#         accessoires_womens = Category.objects.none()
#         accessoires_mens = Category.objects.none()
#
#     marque_category = Category.objects.filter(name="Marques Vêtement").first()
#     if marque_category:
#         brands_womens = Category.objects.filter(parent=marque_category, genders__name="F")
#         brands_mens = Category.objects.filter(parent=marque_category, genders__name="H")
#     else:
#         brands_womens = Category.objects.none()
#         brands_mens = Category.objects.none()
#
#     return {
#         "categories": categories,
#         "clovings_women": clovings_women,
#         "clovings_men": clovings_men,
#         "accessoires_women": accessoires_womens,
#         "acce
#
#         ssoires_mens": accessoires_mens,
#         "brands_women": brands_womens,
#         "brands_mens": brands_mens,
#
#     }


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

