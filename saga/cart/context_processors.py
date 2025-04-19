from .models import Cart


def cart_context(request):
    try:
        cart = Cart.get_or_create_cart(request)
        cart_items = cart.cart_items.all().select_related('product')
        return {
            'cart_items': cart_items,
            'cart_count': sum(item.quantity for item in cart.cart_items.all()),
            'Order_total': cart.get_total_price(),
            'cart': cart
        }
    except Exception:
        return {'cart_items': [], 'Order_total': 0, 'cart': None, 'cart_count': 0}
