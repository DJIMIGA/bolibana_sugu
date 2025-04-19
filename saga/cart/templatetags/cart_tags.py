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
