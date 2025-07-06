from django import template
from product.models import Product

register = template.Library()

@register.inclusion_tag('product/components/_stock_status.html')
def stock_status(product):
    """
    Template tag pour afficher le statut de stock d'un produit
    
    Usage:
    {% load product_tags %}
    {% stock_status product %}
    """
    status = product.get_stock_status()
    
    return {
        'product': product,
        'status': status,
        'status_type': status['status'],
        'available': status['available'],
        'delivery_days': status['delivery_days'],
        'stock_type': status['stock_type']
    } 