from django.template.loader import render_to_string
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Cart, CartItem
from django.db import transaction

def render_cart_updates(request, cart, cart_item=None, include_payment_summary=False):
    """
    Fonction utilitaire pour générer toutes les mises à jour nécessaires du panier
    """
    updates = []
    
    # 1. Mise à jour du contenu du panier
    cart_items = cart.cart_items.all().select_related('product')
    cart_content_html = render_to_string(
        'cart/components/_cart_content.html',
        {
            'cart': cart,
            'cart_items': cart_items
        },
        request=request
    )
    updates.append(f'<div id="cart-content" hx-swap-oob="true">{cart_content_html}</div>')
    
    # 2. Mise à jour du compteur
    cart_count = sum(item.quantity for item in cart_items)
    cart_count_html = (
        f'<span id="cart-count" hx-swap-oob="true" '
        f'class="absolute -top-2 -right-2 bg-red-500 text-white text-xs '
        f'font-bold rounded-full h-5 w-5 flex items-center justify-center">'
        f'{cart_count}</span>'
    )
    updates.append(cart_count_html)
    
    # 3. Mise à jour des totaux
    if include_payment_summary:
        order_total = cart.get_total_price()
        shipping_cost = 2000
        total_with_shipping = order_total + shipping_cost
        
        payment_summary_html = render_to_string(
            'cart/components/_payment_summary.html',
            {
                'order_total': order_total,
                'shipping_cost': shipping_cost,
                'total_with_shipping': total_with_shipping
            },
            request=request
        )
        updates.append(f'<div id="payment-summary" hx-swap-oob="true">{payment_summary_html}</div>')
    
    # 4. Mise à jour du total du panier
    cart_total_html = render_to_string(
        'cart/components/_cart_total.html',
        {
            'cart': cart,
            'cart_items': cart_items,
            'total': cart.get_total_price()
        },
        request=request
    )
    updates.append(f'<div id="cart-total" hx-swap-oob="true">{cart_total_html}</div>')
    
    return ''.join(updates)


def render_cart_item(request, cart_item):
    """Rendu d'un article individuel."""
    print(cart_item, 'cart_item')
    item_html = render_to_string('cart/components/_cart_item.html', {'item': cart_item}, request=request)
    return f'<li id="cart-item-{cart_item.id}" hx-swap-oob="true">{item_html}</li>'


def render_cart_count(cart):
    """Rendu du compteur d'articles."""
    cart_count = sum(item.quantity for item in cart.cart_items.all())
    return (
        f'<span id="cart-count" hx-swap-oob="true" '
        f'class="absolute -top-2 -right-2 bg-red-500 text-white text-xs '
        f'font-bold rounded-full h-5 w-5 flex items-center justify-center">'
        f'{cart_count}</span>'
    )


def render_payment_summary(request, cart, cart_items):
    """Rendu du résumé de paiement."""
    context = {
        'order_total': cart.get_total_price(),
        'shipping_cost': 2000,
        'total_with_shipping': cart.get_total_price() + 2000,
        'cart': cart,
        'cart_items': cart_items
    }
    summary_html = render_to_string('cart/components/_payment_summary.html', context, request=request)
    return f'<div id="payment-summary" hx-swap-oob="true">{summary_html}</div>'


def render_cart_total(request, cart, cart_items):
    """Rendu du total du panier."""
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total': cart.get_total_price()
    }
    total_html = render_to_string('cart/components/_cart_total.html', context, request=request)
    return f'<div id="cart-total" hx-swap-oob="true">{total_html}</div>'


@receiver(user_logged_in)
def migrate_anonymous_cart(sender, user, **kwargs):
    """
    Migre le panier d'un utilisateur anonyme vers son compte lors de la connexion.
    """
    try:
        # Récupérer la session_key du signal
        session_key = kwargs.get('request').session.session_key
        
        if session_key:
            # Récupérer le panier anonyme
            anonymous_cart = Cart.objects.filter(session_key=session_key).first()
            
            if anonymous_cart:
                # Récupérer ou créer le panier de l'utilisateur
                user_cart, created = Cart.objects.get_or_create(user=user)
                
                if created:
                    # Si c'est un nouveau panier, copier tous les items
                    for item in anonymous_cart.items.all():
                        CartItem.objects.create(
                            cart=user_cart,
                            product=item.product,
                            quantity=item.quantity,
                            color=item.color,
                            size=item.size
                        )
                else:
                    # Si le panier existe déjà, fusionner les items
                    for anonymous_item in anonymous_cart.items.all():
                        # Vérifier si l'item existe déjà dans le panier utilisateur
                        existing_item = user_cart.items.filter(
                            product=anonymous_item.product,
                            color=anonymous_item.color,
                            size=anonymous_item.size
                        ).first()
                        
                        if existing_item:
                            # Mettre à jour la quantité
                            existing_item.quantity += anonymous_item.quantity
                            existing_item.save()
                        else:
                            # Créer un nouvel item
                            CartItem.objects.create(
                                cart=user_cart,
                                product=anonymous_item.product,
                                quantity=anonymous_item.quantity,
                                color=anonymous_item.color,
                                size=anonymous_item.size
                            )
                
                # Supprimer le panier anonyme
                anonymous_cart.delete()
                
    except Exception as e:
        # Log l'erreur mais ne pas bloquer la connexion
        print(f"Erreur lors de la migration du panier: {str(e)}")
