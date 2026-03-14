"""
Utilitaires pour gérer la hiérarchie des catégories B2B
"""
from typing import List, Dict, Optional
from django.db.models import Q
from inventory.models import ExternalCategory
from product.models import Category


def build_category_hierarchy(categories_data: List[Dict]) -> Dict:
    """
    Construit une hiérarchie de catégories à partir des données B2B.
    
    Args:
        categories_data: Liste de dictionnaires contenant les données des catégories B2B
        
    Returns:
        Dictionnaire avec les catégories principales et leurs sous-catégories
    """
    # Séparer les catégories par niveau
    main_categories = []  # level 0
    sub_categories = []   # level 1+
    
    for cat in categories_data:
        if cat.get('level') == 0 and cat.get('parent') is None:
            main_categories.append(cat)
        else:
            sub_categories.append(cat)
    
    # Trier les catégories principales par ordre
    main_categories.sort(key=lambda x: x.get('order', 0))
    
    # Organiser les sous-catégories par parent
    categories_by_parent = {}
    for sub_cat in sub_categories:
        parent_id = sub_cat.get('parent')
        if parent_id:
            if parent_id not in categories_by_parent:
                categories_by_parent[parent_id] = []
            categories_by_parent[parent_id].append(sub_cat)
    
    # Trier les sous-catégories par ordre
    for parent_id in categories_by_parent:
        categories_by_parent[parent_id].sort(key=lambda x: x.get('order', 0))
    
    # Construire la hiérarchie finale
    hierarchy = []
    for main_cat in main_categories:
        main_cat_id = main_cat.get('id')
        main_cat_dict = {
            'id': main_cat_id,
            'name': main_cat.get('name'),
            'slug': main_cat.get('slug'),
            'description': main_cat.get('description'),
            'image_url': main_cat.get('image_url'),
            'level': main_cat.get('level', 0),
            'order': main_cat.get('order', 0),
            'is_rayon': main_cat.get('is_rayon', False),
            'rayon_type': main_cat.get('rayon_type'),
            'children': categories_by_parent.get(main_cat_id, [])
        }
        hierarchy.append(main_cat_dict)
    
    return {
        'main_categories': hierarchy,
        'total_main': len(hierarchy),
        'total_sub': len(sub_categories)
    }


def get_b2b_categories_hierarchy() -> Dict:
    """
    Récupère la hiérarchie des catégories B2B depuis la base de données.
    Utilise les catégories externes (ExternalCategory) pour mapper avec les catégories locales.
    
    Returns:
        Dictionnaire avec la hiérarchie des catégories B2B
    """
    # Récupérer toutes les catégories externes avec leurs catégories associées
    external_categories = ExternalCategory.objects.select_related(
        'category'
    ).prefetch_related(
        'category__children',
        'category__children__external_category'
    ).all()
    
    # Construire la structure hiérarchique
    main_categories = []
    categories_by_external_id = {}
    
    # Mapper les catégories externes
    for ext_cat in external_categories:
        categories_by_external_id[ext_cat.external_id] = {
            'external_id': ext_cat.external_id,
            'external_parent_id': ext_cat.external_parent_id,
            'category': ext_cat.category,
            'last_synced_at': ext_cat.last_synced_at
        }
    
    # Organiser en hiérarchie
    for ext_cat in external_categories:
        if ext_cat.external_parent_id is None:
            # Catégorie principale
            children = []
            # Trouver les sous-catégories
            for child_ext_id, child_data in categories_by_external_id.items():
                if child_data['external_parent_id'] == ext_cat.external_id:
                    children.append({
                        'id': child_data['category'].id,
                        'external_id': child_data['external_id'],
                        'name': child_data['category'].name,
                        'slug': child_data['category'].slug,
                        'description': child_data['category'].description,
                        'image_url': child_data['category'].image.url if child_data['category'].image else None,
                        'level': 1,
                        'order': child_data['category'].order,
                    })
            
            main_categories.append({
                'id': ext_cat.category.id,
                'external_id': ext_cat.external_id,
                'name': ext_cat.category.name,
                'slug': ext_cat.category.slug,
                'description': ext_cat.category.description,
                'image_url': ext_cat.category.image.url if ext_cat.category.image else None,
                'level': 0,
                'order': ext_cat.category.order,
                'children': sorted(children, key=lambda x: x.get('order', 0))
            })
    
    # Trier les catégories principales par ordre
    main_categories.sort(key=lambda x: x.get('order', 0))
    
    return {
        'main_categories': main_categories,
        'total_main': len(main_categories),
        'total_sub': sum(len(cat['children']) for cat in main_categories)
    }


def sync_b2b_categories_to_local(categories_data: List[Dict]) -> Dict:
    """
    Synchronise les catégories B2B avec les catégories locales.
    Crée ou met à jour les catégories et les mappings ExternalCategory.
    
    Args:
        categories_data: Liste de dictionnaires contenant les données des catégories B2B
        
    Returns:
        Dictionnaire avec les statistiques de synchronisation
    """
    from django.utils import timezone
    
    created_count = 0
    updated_count = 0
    
    for cat_data in categories_data:
        external_id = cat_data.get('id')
        parent_id = cat_data.get('parent')
        external_parent_id = parent_id if parent_id else None
        
        # Créer ou mettre à jour la catégorie locale
        category, created = Category.objects.get_or_create(
            slug=cat_data.get('slug'),
            defaults={
                'name': cat_data.get('name'),
                'description': cat_data.get('description'),
                'order': cat_data.get('order', 0),
                'is_main': cat_data.get('level', 0) == 0,
            }
        )
        
        # Mettre à jour si nécessaire
        if not created:
            category.name = cat_data.get('name', category.name)
            category.description = cat_data.get('description', category.description)
            category.order = cat_data.get('order', category.order)
            category.is_main = cat_data.get('level', 0) == 0
            category.save()
            updated_count += 1
        else:
            created_count += 1
        
        # Gérer le parent si nécessaire
        if external_parent_id:
            try:
                parent_ext_cat = ExternalCategory.objects.get(external_id=external_parent_id)
                category.parent = parent_ext_cat.category
                category.save()
            except ExternalCategory.DoesNotExist:
                pass
        
        # Créer ou mettre à jour le mapping ExternalCategory
        ExternalCategory.objects.update_or_create(
            external_id=external_id,
            defaults={
                'category': category,
                'external_parent_id': external_parent_id,
                'last_synced_at': timezone.now()
            }
        )
    
    return {
        'created': created_count,
        'updated': updated_count,
        'total': len(categories_data)
    }


