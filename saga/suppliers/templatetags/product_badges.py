# Ce fichier gère les badges des produits
from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.inclusion_tag('suppliers/components/badges.html')
def product_badges(product):
    """
    Tag pour afficher les badges d'un produit
    """
    badges = []
    
    # Si c'est un dictionnaire, on récupère l'objet product
    if isinstance(product, dict):
        product_obj = product.get('product')
        if not product_obj:
            return {'badges': badges}
        product = product_obj
    
    # Badge SALAM/CLASSIQUE (priorité haute)
    if hasattr(product, 'is_salam') and product.is_salam:
        badges.append({
            'type': 'salam',
            'text': 'SALAM',
            'color': 'salam',
            'icon': 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z'
        })
    else:
        badges.append({
            'type': 'classic',
            'text': 'CLASSIQUE',
            'color': 'classic',
            'icon': 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'
        })
    
    # Badge Nouveau (produit ajouté dans les 7 derniers jours)
    if hasattr(product, 'created_at') and product.created_at and (timezone.now() - product.created_at) <= timedelta(days=7):
        badges.append({
            'type': 'new',
            'text': 'Nouveau',
            'color': 'new',
            'icon': 'M13 10V3L4 14h7v7l9-11h-7z'
        })
    
    # Badge Promo (si le produit a un prix réduit)
    if hasattr(product, 'discount_price') and product.discount_price and product.discount_price < product.price:
        try:
            discount = int(((product.price - product.discount_price) / product.price) * 100)
            if discount > 0:
                badges.append({
                    'type': 'promo',
                    'text': f'Promo -{discount}%',
                    'color': 'promo',
                    'icon': 'M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z'
                })
        except (TypeError, ZeroDivisionError):
            # En cas d'erreur dans le calcul, on affiche juste "Promo"
            badges.append({
                'type': 'promo',
                'text': 'Promo',
                'color': 'promo',
                'icon': 'M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z'
            })
    
    # Badge Stock limité (moins de 5 unités)
    if hasattr(product, 'stock') and product.stock and product.stock <= 5:
        badges.append({
            'type': 'stock',
            'text': 'Stock limité',
            'color': 'stock',
            'icon': 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z'
        })

    # Badges spécifiques aux téléphones (garantie uniquement)
    if hasattr(product, 'phone') and product.phone:
        # Badge Garantie (si le téléphone a une garantie)
        if hasattr(product.phone, 'warranty_period') and product.phone.warranty_period:
            badges.append({
                'type': 'warranty',
                'text': f'Garantie {product.phone.warranty_period} mois',
                'color': 'warranty',
                'icon': 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z'
            })
    
    # Badge Produit populaire (si le produit a plus de 100 vues)
    if hasattr(product, 'views_count') and product.views_count and product.views_count > 100:
        badges.append({
            'type': 'popular',
            'text': 'Populaire',
            'color': 'popular',
            'icon': 'M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z'
        })
    
    return {'badges': badges} 