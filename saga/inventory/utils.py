"""
Utilitaires pour exploiter les catégories et produits synchronisés depuis B2B
"""
from typing import List, Optional
from django.db.models import Q
from product.models import Category, Product
from .models import ExternalCategory, ExternalProduct


def get_synced_categories() -> List[Category]:
    """
    Récupère toutes les catégories synchronisées depuis B2B
    
    Returns:
        Liste des catégories Category synchronisées
    """
    external_categories = ExternalCategory.objects.all()
    category_ids = external_categories.values_list('category_id', flat=True)
    return Category.objects.filter(id__in=category_ids).select_related('parent').prefetch_related('children')


def get_category_by_external_id(external_id: int) -> Optional[Category]:
    """
    Récupère une catégorie par son ID externe (B2B)
    
    Args:
        external_id: ID de la catégorie dans B2B
    
    Returns:
        Instance de Category ou None
    """
    try:
        external_category = ExternalCategory.objects.get(
            external_id=external_id
        )
        return external_category.category
    except ExternalCategory.DoesNotExist:
        return None


def get_products_in_synced_category(category: Category) -> List[Product]:
    """
    Récupère tous les produits d'une catégorie synchronisée
    
    Args:
        category: Instance de Category
    
    Returns:
        Liste des produits dans cette catégorie
    """
    # Vérifier si la catégorie est synchronisée
    is_synced = ExternalCategory.objects.filter(category=category).exists()
    
    if is_synced:
        # Si synchronisée, récupérer les produits synchronisés de cette catégorie
        external_products = ExternalProduct.objects.filter(
            external_category_id__isnull=False
        )
        
        # Récupérer les catégories externes correspondantes
        external_categories = ExternalCategory.objects.filter(
            category=category
        )
        
        external_category_ids = external_categories.values_list('external_id', flat=True)
        
        # Filtrer les produits par external_category_id
        matching_products = external_products.filter(
            external_category_id__in=external_category_ids
        )
        
        product_ids = matching_products.values_list('product_id', flat=True)
        return Product.objects.filter(id__in=product_ids).select_related('category', 'supplier')
    
    # Si pas synchronisée, utiliser le comportement normal
    return Product.objects.filter(category=category).select_related('category', 'supplier')


def get_category_tree_from_b2b() -> List[dict]:
    """
    Construit l'arbre hiérarchique des catégories depuis B2B
    
    Returns:
        Liste de dictionnaires représentant l'arbre des catégories
    """
    external_categories = ExternalCategory.objects.all().select_related('category')
    
    # Créer un mapping par external_id
    categories_by_id = {}
    root_categories = []
    
    for ext_cat in external_categories:
        cat_data = {
            'id': ext_cat.category.id,
            'external_id': ext_cat.external_id,
            'name': ext_cat.category.name,
            'slug': ext_cat.category.slug,
            'parent_id': ext_cat.external_parent_id,
            'category': ext_cat.category,
            'children': []
        }
        categories_by_id[ext_cat.external_id] = cat_data
        
        # Si pas de parent, c'est une catégorie racine
        if not ext_cat.external_parent_id:
            root_categories.append(cat_data)
    
    # Construire l'arbre
    for ext_cat in external_categories:
        if ext_cat.external_parent_id and ext_cat.external_parent_id in categories_by_id:
            parent = categories_by_id[ext_cat.external_parent_id]
            child = categories_by_id[ext_cat.external_id]
            parent['children'].append(child)
    
    return root_categories


def is_category_synced_from_b2b(category: Category) -> bool:
    """
    Vérifie si une catégorie est synchronisée depuis B2B
    
    Args:
        category: Instance de Category
    
    Returns:
        True si la catégorie est synchronisée
    """
    return ExternalCategory.objects.filter(category=category).exists()


def get_synced_categories_for_user(user) -> List[Category]:
    """
    Récupère les catégories synchronisées (toutes les catégories synchronisées)
    
    Note: Cette fonction a été simplifiée car il n'y a plus de connexion par utilisateur.
    Elle retourne maintenant toutes les catégories synchronisées.
    
    Args:
        user: Utilisateur (paramètre conservé pour compatibilité)
    
    Returns:
        Liste des catégories synchronisées
    """
    return get_synced_categories()


def get_b2b_products(limit: Optional[int] = None) -> List[Product]:
    """
    Récupère les produits B2B synchronisés depuis l'API externe avec toutes leurs informations
    
    Args:
        limit: Nombre maximum de produits à retourner (optionnel)
    
    Returns:
        Liste des produits B2B synchronisés et disponibles avec toutes leurs relations
    """
    # Récupérer les produits avec ExternalProduct et sync_status='synced'
    # Inclure toutes les relations nécessaires pour avoir toutes les informations
    external_products = ExternalProduct.objects.filter(
        sync_status='synced'
    ).select_related(
        'product',
        'product__category',
        'product__supplier',
        'product__phone',
        'product__phone__color',
        'product__clothing_product',
        'product__fabric_product',
        'product__cultural_product'
    ).prefetch_related(
        'product__images',
        'product__clothing_product__size',
        'product__clothing_product__color',
        'product__fabric_product__color'
    )
    
    # Filtrer uniquement les produits disponibles et récupérer les objets Product
    products = Product.objects.filter(
        id__in=[ep.product.id for ep in external_products if ep.product],
        is_available=True
    ).select_related(
        'category',
        'supplier',
        'phone',
        'phone__color',
        'clothing_product',
        'fabric_product',
        'cultural_product'
    ).prefetch_related(
        'images',
        'clothing_product__size',
        'clothing_product__color',
        'fabric_product__color'
    ).order_by('-id')
    
    # Limiter le nombre si demandé
    if limit:
        products = products[:limit]
    
    return list(products)
