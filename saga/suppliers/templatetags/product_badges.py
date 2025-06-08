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
                    'icon': 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
                })
        except (TypeError, ZeroDivisionError):
            # En cas d'erreur dans le calcul, on affiche juste "Promo"
            badges.append({
                'type': 'promo',
                'text': 'Promo',
                'color': 'promo',
                'icon': 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
            })
    
    # Badge Stock limité (moins de 5 unités)
    if hasattr(product, 'stock') and product.stock and product.stock <= 5:
        badges.append({
            'type': 'stock',
            'text': 'Stock limité',
            'color': 'stock',
            'icon': 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z'
        })

    # Badges spécifiques aux téléphones
    if hasattr(product, 'phone') and product.phone:
        badges.append({
            'type': 'phone',
            'text': 'Téléphone',
            'color': 'phone',
            'icon': 'M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z'
        })
        
        # Badge Garantie (si le téléphone a une garantie)
        if hasattr(product.phone, 'warranty_period') and product.phone.warranty_period:
            badges.append({
                'type': 'warranty',
                'text': f'Garantie {product.phone.warranty_period} mois',
                'color': 'phone',
                'icon': 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z'
            })

    # Badges spécifiques aux vêtements
    if hasattr(product, 'clothing_product') and product.clothing_product:
        badges.append({
            'type': 'clothing',
            'text': 'Vêtement',
            'color': 'clothing',
            'icon': 'M20 16.58V18a2 2 0 01-2 2H6a2 2 0 01-2-2v-1.42a2 2 0 01.77-1.58l7-5.25a2 2 0 012.46 0l7 5.25a2 2 0 01.77 1.58z'
        })

    # Badges spécifiques aux tissus
    if hasattr(product, 'fabric_product') and product.fabric_product:
        # Badge pour les types de tissus
        if product.fabric_product.fabric_type:
            badges.append({
                'type': 'fabric_type',
                'text': f'{product.fabric_product.get_fabric_type_display()}',
                'color': 'fabric',
                'icon': 'M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z'
            })

    # Badges spécifiques aux produits culturels
    if hasattr(product, 'cultural_product') and product.cultural_product:
        badges.append({
            'type': 'cultural',
            'text': 'Livre & Culture',
            'color': 'cultural',
            'icon': 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253'
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