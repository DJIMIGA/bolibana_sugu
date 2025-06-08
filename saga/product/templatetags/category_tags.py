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