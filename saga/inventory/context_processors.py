"""
Context processors pour rendre les catégories synchronisées disponibles dans les templates
"""
from .utils import get_synced_categories


def synced_categories_context(request):
    """
    Ajoute les catégories synchronisées depuis B2B au contexte des templates
    
    Usage dans settings.py:
    TEMPLATES[0]['OPTIONS']['context_processors'].append(
        'inventory.context_processors.synced_categories_context'
    )
    """
    context = {}
    
    # Récupérer toutes les catégories synchronisées
    synced_categories = get_synced_categories()
    context['synced_categories'] = synced_categories
    context['has_synced_categories'] = len(synced_categories) > 0
    
    return context
