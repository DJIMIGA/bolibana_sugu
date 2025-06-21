from django import template
from django.contrib.contenttypes.models import ContentType
from product.models import Phone, Clothing, CulturalItem, Fabric, Product, Favorite
from django.utils import timezone
from django.urls import reverse
import logging
from datetime import timedelta, datetime
from django.template.defaultfilters import stringfilter
from django.template.loader import render_to_string
from django.core.cache import cache

register = template.Library()
logger = logging.getLogger(__name__)

@register.simple_tag
def get_product_detail_url(product):
    """
    Retourne l'URL appropriée pour le détail d'un produit en fonction de son type.
    """
    try:
        # Si c'est un objet Product
        if isinstance(product, Product):
            if hasattr(product, 'phone'):
                logger.debug(f"Produit trouvé: Téléphone - {product.title}")
                return reverse('suppliers:phone_detail', args=[product.slug])
            elif hasattr(product, 'clothing_product'):
                logger.debug(f"Produit trouvé: Vêtement - {product.title}")
                return reverse('suppliers:clothing_detail', args=[product.slug])
            elif hasattr(product, 'cultural_product'):
                logger.debug(f"Produit trouvé: Article culturel - {product.title}")
                return reverse('suppliers:cultural_detail', args=[product.slug])
            elif hasattr(product, 'fabric_product'):
                logger.debug(f"Produit trouvé: Tissu - {product.title}")
                return reverse('suppliers:fabric_detail', args=[product.slug])
            else:
                # Cas par défaut pour les produits sans modèle spécifique
                logger.debug(f"Produit trouvé: Produit générique - {product.title}")
                return reverse('suppliers:product_detail', args=[product.slug])
        
        # Si c'est un objet spécifique (Phone, Clothing, etc.)
        elif isinstance(product, Phone):
            logger.debug(f"Téléphone trouvé: {product.product.title}")
            return reverse('suppliers:phone_detail', args=[product.product.slug])
        elif isinstance(product, Clothing):
            logger.debug(f"Vêtement trouvé: {product.product.title}")
            return reverse('suppliers:clothing_detail', args=[product.product.slug])
        elif isinstance(product, CulturalItem):
            logger.debug(f"Article culturel trouvé: {product.product.title}")
            return reverse('suppliers:cultural_detail', args=[product.product.slug])
        elif isinstance(product, Fabric):
            logger.debug(f"Tissu trouvé: {product.product.title}")
            return reverse('suppliers:fabric_detail', args=[product.product.slug])
        
        logger.warning(f"Type de produit non reconnu pour {getattr(product, 'title', 'Sans titre')}")
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la génération de l'URL pour {getattr(product, 'title', 'Sans titre')}: {str(e)}")
        return None

@register.filter
def days_since(value):
    """Calcule le nombre de jours depuis une date donnée."""
    if not value:
        return 0
    return (datetime.now().date() - value).days

@register.filter
def split_path(value, separator=' > '):
    """Découpe une chaîne de caractères selon un séparateur."""
    if not value:
        return []
    return value.split(separator)

@register.inclusion_tag('suppliers/components/phone_card.html', takes_context=True)
def render_phone_card(context, product):
    """
    Affiche une carte pour un téléphone.
    """
    # Si c'est un dictionnaire
    if isinstance(product, dict):
        if 'product' in product:
            product = product['product']
    
    return {
        'product': product,
        'phone': product.phone,
        'request': context['request'],
        'user': context['request'].user
    }

@register.inclusion_tag('suppliers/components/clothing_card.html', takes_context=True)
def render_clothing_card(context, product):
    """
    Affiche une carte pour un vêtement.
    """
    # Si c'est un dictionnaire
    if isinstance(product, dict):
        if 'product' in product:
            product_obj = product['product']
            clothing_product = product.get('clothing_product', product_obj.clothing_product)
        else:
            # Si c'est un dictionnaire sans clé 'product', on suppose que c'est l'objet Product
            product_obj = product
            clothing_product = product_obj.clothing_product
    else:
        # Si c'est un objet Product
        product_obj = product
        clothing_product = product_obj.clothing_product
    
    return {
        'product': product_obj,
        'clothing_product': clothing_product,
        'request': context['request'],
        'user': context['request'].user
    }

@register.inclusion_tag('suppliers/components/cultural_card.html', takes_context=True)
def render_cultural_card(context, product):
    """
    Affiche une carte pour un article culturel.
    """
    # Si c'est un dictionnaire
    if isinstance(product, dict):
        if 'product' in product:
            product = product['product']
    
    return {
        'product': product,
        'cultural_product': product.cultural_product,
        'request': context['request'],
        'user': context['request'].user
    }

@register.inclusion_tag('suppliers/components/fabric_card.html', takes_context=True)
def render_fabric_card(context, product):
    """
    Affiche une carte pour un tissu.
    """
    # Si c'est un dictionnaire
    if isinstance(product, dict):
        if 'product' in product:
            product = product['product']
    
    return {
        'product': product,
        'fabric_product': product.fabric_product,
        'request': context['request'],
        'user': context['request'].user
    }

@register.inclusion_tag('suppliers/components/product_card.html', takes_context=True)
def render_product_card(context, product):
    """
    Template tag pour afficher une carte produit avec le bon template selon le type
    """
    # Si c'est un dictionnaire
    if isinstance(product, dict):
        if 'product' in product:
            product_obj = product['product']
            # Récupérer les objets spécifiques du dictionnaire
            phone = product.get('phone', getattr(product_obj, 'phone', None))
            clothing_product = product.get('clothing_product', getattr(product_obj, 'clothing_product', None))
            fabric_product = product.get('fabric_product', getattr(product_obj, 'fabric_product', None))
            cultural_product = product.get('cultural_product', getattr(product_obj, 'cultural_product', None))
        else:
            # Si c'est un dictionnaire sans clé 'product', on suppose que c'est l'objet Product
            product_obj = product
            phone = getattr(product_obj, 'phone', None)
            clothing_product = getattr(product_obj, 'clothing_product', None)
            fabric_product = getattr(product_obj, 'fabric_product', None)
            cultural_product = getattr(product_obj, 'cultural_product', None)
    else:
        # Si c'est un objet Product
        product_obj = product
        phone = getattr(product_obj, 'phone', None)
        clothing_product = getattr(product_obj, 'clothing_product', None)
        fabric_product = getattr(product_obj, 'fabric_product', None)
        cultural_product = getattr(product_obj, 'cultural_product', None)
    
    # Déterminer le type de produit et retourner les bonnes variables
    if phone:
        return {
            'product': product_obj,
            'phone': phone,
            'request': context['request'],
            'user': context['request'].user
        }
    elif clothing_product:
        return {
            'product': product_obj,
            'clothing_product': clothing_product,
            'request': context['request'],
            'user': context['request'].user
        }
    elif fabric_product:
        return {
            'product': product_obj,
            'fabric_product': fabric_product,
            'request': context['request'],
            'user': context['request'].user
        }
    elif cultural_product:
        return {
            'product': product_obj,
            'cultural_product': cultural_product,
            'request': context['request'],
            'user': context['request'].user
        }
    else:
        return {
            'product': product_obj,
            'request': context['request'],
            'user': context['request'].user
        }

@register.simple_tag
def get_product_details(product_id):
    """Récupère les détails d'un produit."""
    try:
        product = Product.objects.select_related(
            'phone',
            'phone__color',
            'category',
            'category__parent',
            'category__parent__parent'
        ).get(id=product_id)
        return product
    except Product.DoesNotExist:
        return None

@register.filter
def filter_by_category(products, category_id):
    """Filtre les produits par ID de catégorie"""
    filtered_products = []
    for product in products:
        # Si c'est un dictionnaire
        if isinstance(product, dict):
            if 'product' in product:
                product_obj = product['product']
                if hasattr(product_obj, 'category_id') and product_obj.category_id == category_id:
                    filtered_products.append(product)  # On garde le dictionnaire complet
        # Si c'est un objet Product
        elif hasattr(product, 'category_id') and product.category_id == category_id:
            filtered_products.append(product)
    return filtered_products

@register.filter
def is_favorite(user, product):
    logger.debug(f"Checking favorite for user {user} and product {product}")
    if not user or not user.is_authenticated:
        logger.debug("User not authenticated")
        return False
    cache_key = f"favorite_{user.id}_{product.id}"
    cached = cache.get(cache_key)
    if cached is not None:
        logger.debug(f"Cache hit: {cached}")
        return cached
    result = Favorite.objects.filter(user=user, product=product).exists()
    logger.debug(f"Database check result: {result}")
    cache.set(cache_key, result, 60*15)
    return result

@register.filter
def format_dimension(value):
    """
    Formate une dimension en supprimant les zéros inutiles.
    Ex: 3.00 devient 3, 1.50 devient 1.5
    """
    if value is None:
        return ""
    
    # Convertir en string et remplacer le point par une virgule
    str_value = str(value).replace('.', ',')
    
    # Supprimer les zéros inutiles à la fin
    if ',' in str_value:
        # Supprimer les zéros à la fin après la virgule
        while str_value.endswith('0') and ',' in str_value:
            str_value = str_value[:-1]
        
        # Si on se retrouve avec juste une virgule, la supprimer
        if str_value.endswith(','):
            str_value = str_value[:-1]
    
    return str_value


