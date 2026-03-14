from django import template
from cart.models import Cart

register = template.Library()

@register.simple_tag(takes_context=True)
def get_cart(context):
    request = context['request']
    user = request.user
    print(f"Utilisateur récupéré dans le tag : {user}")  # Debug

    cart_items = []
    order_total = 0
    quantities = list(range(1, 10))  # Liste de quantités de 1 à 9

    if user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=user)
        cart_items = cart.cart_items.all().select_related('product')
        order_total = cart.get_total_price()
    else:
        cart = None  # Gérer les utilisateurs non connectés ici

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'order_total': order_total,
        'quantities': quantities,
    }
    print('context', context)
    return context

@register.inclusion_tag('cart/components/_product_image.html')
def product_image(product, size_class="w-full h-full", alt_text=None, fallback_icon_size="w-8 h-8"):
    """
    Template tag pour afficher une image de produit avec fallback.
    
    Usage:
    {% product_image product size_class="w-20 h-20" alt_text="Nom du produit" %}
    """
    has_image = product.image and product.image.url
    return {
        'product': product,
        'has_image': has_image,
        'size_class': size_class,
        'alt_text': alt_text or product.title,
        'fallback_icon_size': fallback_icon_size,
    }

@register.filter
def filter_classic_products(cart_items):
    """
    Filtre pour récupérer uniquement les produits classiques (non Salam).
    
    Usage:
    {% with classic_items=cart.cart_items.all|filter_classic_products %}
    """
    return [item for item in cart_items if not item.product.is_salam]

@register.filter
def filter_salam_products(cart_items):
    """
    Filtre pour récupérer uniquement les produits Salam.
    
    Usage:
    {% with salam_items=cart.cart_items.all|filter_salam_products %}
    """
    return [item for item in cart_items if item.product.is_salam]

@register.filter
def format_price(value):
    """
    Filtre pour formater les prix avec des espaces comme séparateurs de milliers.
    
    Usage:
    {{ price|format_price }}
    """
    if value is None:
        return "0 FCFA"
    
    try:
        # Convertir en entier et formater avec des espaces
        int_value = int(float(value))
        formatted = f"{int_value:,}".replace(',', ' ')
        return f"{formatted} FCFA"
    except (ValueError, TypeError):
        return "0 FCFA"
