from .models import Cart


def cart_context(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.cart_items.all().select_related('product')
        return {
            'cart_items': cart_items,
            'cart_count': sum(item.quantity for item in cart.cart_items.all()),
            'Order_total': cart.get_total_price(),
            'cart': cart

        }
    return {'cart_items': [], 'Order_total': 0, 'cart': None, 'cart_count': 0}
