from django import template

register = template.Library()

@register.filter
def get_brand_name(full_name):
    """
    Extrait le nom de la marque depuis un nom complet "Marque Série"
    Exemple: "TECNO POVA" -> "TECNO"
    """
    if not full_name:
        return ""
    
    parts = full_name.split()
    if len(parts) >= 2:
        return parts[0]
    return full_name

@register.filter
def get_series_name(full_name):
    """
    Extrait le nom de la série depuis un nom complet "Marque Série"
    Exemple: "TECNO POVA" -> "POVA"
    """
    if not full_name:
        return ""
    
    parts = full_name.split()
    if len(parts) >= 2:
        return parts[1]
    return full_name 