"""
Vues pour exploiter les catégories synchronisées depuis B2B
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from product.models import Category
from .models import ExternalCategory
from .utils import (
    get_synced_categories,
    get_category_by_external_id,
    get_products_in_synced_category,
    get_category_tree_from_b2b,
    is_category_synced_from_b2b
)


def category_list_synced(request):
    """
    Affiche la liste des catégories synchronisées depuis B2B
    """
    # Récupérer les catégories synchronisées
    synced_categories = get_synced_categories()
    category_tree = get_category_tree_from_b2b()
    
    # Séparer les catégories principales et les sous-catégories
    main_categories = [cat for cat in synced_categories if not cat.parent]
    sub_categories = [cat for cat in synced_categories if cat.parent]
    
    # Trier les catégories principales par ordre
    main_categories = sorted(main_categories, key=lambda x: (x.order, x.name))
    sub_categories = sorted(sub_categories, key=lambda x: x.name)
    
    return render(request, 'inventory/category_list.html', {
        'synced_categories': synced_categories,
        'main_categories': main_categories,
        'sub_categories': sub_categories,
        'category_tree': category_tree,
        'title': 'Catégories Synchronisées',
    })


def category_detail_synced(request, category_slug):
    """
    Affiche les détails d'une catégorie synchronisée et ses produits
    """
    category = get_object_or_404(Category, slug=category_slug)
    
    # Vérifier si la catégorie est synchronisée
    is_synced = is_category_synced_from_b2b(category)
    
    # Récupérer les produits de cette catégorie
    if is_synced:
        products = get_products_in_synced_category(category)
    else:
        # Comportement normal si pas synchronisée
        products = category.products.filter(is_available=True)
    
    # Récupérer les informations de synchronisation
    external_category = None
    try:
        external_category = ExternalCategory.objects.get(
            category=category
        )
    except ExternalCategory.DoesNotExist:
        pass
    
    return render(request, 'inventory/category_detail.html', {
        'category': category,
        'products': products,
        'is_synced': is_synced,
        'external_category': external_category,
    })


@login_required
def category_tree_json(request):
    """
    API JSON pour récupérer l'arbre des catégories synchronisées
    """
    category_tree = get_category_tree_from_b2b()
    
    # Convertir en format JSON
    def serialize_category(cat):
        return {
            'id': cat['id'],
            'external_id': cat['external_id'],
            'name': cat['name'],
            'slug': cat['slug'],
            'parent_id': cat['parent_id'],
            'children': [serialize_category(child) for child in cat['children']]
        }
    
    tree_json = [serialize_category(cat) for cat in category_tree]
    
    return JsonResponse({'categories': tree_json})


def category_products_json(request, category_id):
    """
    API JSON pour récupérer les produits d'une catégorie synchronisée
    """
    category = get_object_or_404(Category, id=category_id)
    
    is_synced = is_category_synced_from_b2b(category)
    
    if is_synced:
        products = get_products_in_synced_category(category)
    else:
        products = category.products.filter(is_available=True)
    
    products_data = [{
        'id': p.id,
        'title': p.title,
        'slug': p.slug,
        'price': float(p.price),
        'image_url': p.get_main_image_url(),
        'stock': p.stock,
        'is_available': p.is_available,
    } for p in products[:50]]  # Limiter à 50 produits
    
    return JsonResponse({
        'category': {
            'id': category.id,
            'name': category.name,
            'slug': category.slug,
        },
        'is_synced': is_synced,
        'products': products_data,
        'count': products.count()
    })
