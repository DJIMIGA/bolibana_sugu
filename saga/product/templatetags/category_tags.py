from django import template

register = template.Library()

@register.filter
def get_values(dictionary):
    return dictionary.values() 

@register.filter
def get_item(dictionary, key):
    """Récupère un élément d'un dictionnaire par sa clé"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def format_rayon_type(rayon_type):
    """Formate le type de rayon pour l'affichage (remplace les underscores par des espaces)"""
    if not rayon_type:
        return ''
    return rayon_type.replace('_', ' ').title()

@register.simple_tag
def find_category_with_children(categories, hierarchy):
    """Trouve la première catégorie qui a des sous-catégories"""
    if not categories or not hierarchy:
        return None
    for category in categories:
        if hasattr(category, 'id'):
            category_data = hierarchy.get(category.id)
            if category_data and category_data.get('subcategories'):
                return category
    return None 