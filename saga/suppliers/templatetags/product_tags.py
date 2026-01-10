from django import template

from django.contrib.contenttypes.models import ContentType
from django.conf import settings
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

def debug_log(message: str) -> None:
    """
    Log uniquement lorsque le DEBUG est activé *et* que l'on a explicitement autorisé
    les logs de tags (pour éviter l'inondation dans dev par défaut).
    """
    enabled = getattr(settings, 'PRODUCT_TAGS_DEBUG_LOGGING', False)
    if enabled and settings.DEBUG and logger.isEnabledFor(logging.DEBUG):
        logger.debug(message)

@register.simple_tag
def get_product_detail_url(product):
    """
    Retourne l'URL appropriée pour le détail d'un produit en fonction de son type.
    """
    try:
        # Si c'est un objet Product
        if isinstance(product, Product):
            if hasattr(product, 'phone'):
                debug_log(f"Produit trouvé: Téléphone - {product.title}")
                return reverse('suppliers:phone_detail', args=[product.slug])
            elif hasattr(product, 'clothing_product'):
                debug_log(f"Produit trouvé: Vêtement - {product.title}")
                return reverse('suppliers:clothing_detail', args=[product.slug])
            elif hasattr(product, 'cultural_product'):
                debug_log(f"Produit trouvé: Article culturel - {product.title}")
                return reverse('suppliers:cultural_detail', args=[product.slug])
            elif hasattr(product, 'fabric_product'):
                debug_log(f"Produit trouvé: Tissu - {product.title}")
                return reverse('suppliers:fabric_detail', args=[product.slug])
            else:
                # Cas par défaut pour les produits sans modèle spécifique
                debug_log(f"Produit trouvé: Produit générique - {product.title}")
                return reverse('suppliers:product_detail', args=[product.slug])
        
        # Si c'est un objet spécifique (Phone, Clothing, etc.)
        elif isinstance(product, Phone):
            debug_log(f"Téléphone trouvé: {product.product.title}")
            return reverse('suppliers:phone_detail', args=[product.product.slug])
        elif isinstance(product, Clothing):
            debug_log(f"Vêtement trouvé: {product.product.title}")
            return reverse('suppliers:clothing_detail', args=[product.product.slug])
        elif isinstance(product, CulturalItem):
            debug_log(f"Article culturel trouvé: {product.product.title}")
            return reverse('suppliers:cultural_detail', args=[product.product.slug])
        elif isinstance(product, Fabric):
            debug_log(f"Tissu trouvé: {product.product.title}")
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
    # Vérifier que le produit existe et a un ID valide
    if not product or not hasattr(product, 'id') or not product.id or product.id == '' or product.id is None:
        return {
            'product': None,
            'request': context['request'],
            'user': context['request'].user
        }
    
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
    debug_log(f"Checking favorite for user {user} and product {product}")
    if not user or not user.is_authenticated:
        debug_log("User not authenticated")
        return False
    cache_key = f"favorite_{user.id}_{product.id}"
    cached = cache.get(cache_key)
    if cached is not None:
        debug_log(f"Cache hit: {cached}")
        return cached
    result = Favorite.objects.filter(user=user, product=product).exists()
    debug_log(f"Database check result: {result}")
    cache.set(cache_key, result, 60*15)
    return result

@register.filter
def format_dimension(value):
    """Formate une dimension avec l'unité appropriée."""
    if value is None:
        return "Non spécifié"
    return f"{value} cm"

@register.simple_tag
def get_phone_colors():
    """
    Retourne un dictionnaire des couleurs de téléphones disponibles.
    """
    try:
        from product.models import PhoneColor
        colors = PhoneColor.objects.all()
        return {color.name: color.code for color in colors}
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des couleurs: {str(e)}")
        return {}

@register.filter
def get_brand_name(brand):
    """
    Extrait le nom de la marque depuis un dict, une chaîne JSON/Python ou retourne la string directement.
    Gère les formats: dict, JSON string, Python dict string representation.
    """
    if not brand:
        return None
    
    # Si c'est déjà un dict
    if isinstance(brand, dict):
        return brand.get('name', str(brand))
    
    # Si c'est une chaîne
    if isinstance(brand, str):
        brand_str = brand.strip()
        
        # Vérifier si c'est une représentation de dict (commence par {)
        if brand_str.startswith('{'):
            # Essayer d'abord JSON
            try:
                import json
                parsed = json.loads(brand_str)
                if isinstance(parsed, dict):
                    return parsed.get('name', brand)
            except (json.JSONDecodeError, ValueError):
                pass
            
            # Essayer d'évaluer comme représentation Python (avec sécurité)
            # Format: {'id': 10, 'name': 'Bara mousso'}
            try:
                # Remplacer les guillemets simples par des doubles pour JSON
                # ou utiliser ast.literal_eval pour plus de sécurité
                import ast
                parsed = ast.literal_eval(brand_str)
                if isinstance(parsed, dict):
                    return parsed.get('name', brand)
            except (ValueError, SyntaxError):
                pass
            
            # Si c'est une chaîne qui ressemble à un dict mais ne peut pas être parsée,
            # essayer d'extraire le nom avec regex
            import re
            match = re.search(r"'name':\s*['\"]([^'\"]+)['\"]", brand_str)
            if match:
                return match.group(1)
        
        # Sinon, retourner la chaîne telle quelle
        return brand
    
    return str(brand)

@register.filter
def format_specification_key(key):
    """
    Formate les clés de spécifications pour un affichage plus lisible.
    """
    # Mapping des clés pour un affichage plus lisible
    key_mapping = {
        'ean': 'Code EAN',
        'barcode': 'Code-barres',
        'unit_display': 'Unité de vente',
        'formatted_quantity': 'Quantité disponible',
        'b2b_category_name': 'Catégorie B2B',
        'b2b_slug': 'Slug B2B',
        'b2b_image_url': 'URL Image B2B',
        'b2b_created_at': 'Date de création B2B',
        'b2b_updated_at': 'Date de mise à jour B2B',
    }
    
    # Remplacer les underscores par des espaces et capitaliser
    formatted = key_mapping.get(key, key.replace('_', ' ').title())
    return formatted

@register.filter
def is_b2b_technical_field(key):
    """
    Détermine si un champ est technique B2B et ne doit pas être affiché dans les spécifications principales.
    """
    technical_fields = [
        'b2b_slug',
        'b2b_image_url',
        'b2b_created_at',
        'b2b_updated_at',
        'alert_threshold',  # Seuil d'alerte - champ technique interne
    ]
    return key in technical_fields

@register.filter
def is_important_spec(key):
    """
    Détermine si une spécification est importante et doit être affichée en premier.
    """
    important_fields = [
        'ean',
        'barcode',
        'unit_display',
        'formatted_quantity',
        'b2b_category_name',
    ]
    return key in important_fields


