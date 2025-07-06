from django.template.loader import render_to_string
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Cart, CartItem
from django.db import transaction
import re

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
    # Rendre seulement le contenu intérieur, sans le <li>
    # car HTMX va remplacer l'élément complet avec outerHTML
    item_html = render_to_string('cart/components/_cart_item.html', {'item': cart_item}, request=request)
    # Extraire le contenu intérieur du <li>
    # Supprimer les balises <li> et </li>
    content = re.sub(r'^<li[^>]*>', '', item_html)
    content = re.sub(r'</li>$', '', content)
    return content


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
def migrate_anonymous_cart(sender, request, user, **kwargs):
    """
    Migre le panier d'un utilisateur anonyme vers son compte lors de la connexion.
    """
    try:
        # Récupérer la session key actuelle avant qu'elle ne soit modifiée
        current_session_key = request.session.session_key
        
        if current_session_key:
            # Récupérer le panier anonyme avec la session key actuelle
            anonymous_cart = Cart.objects.filter(session_key=current_session_key).first()
            
            if anonymous_cart and anonymous_cart.cart_items.exists():
                print(f"🔄 Migration du panier anonyme vers le compte utilisateur {user.email}")
                print(f"📦 {anonymous_cart.cart_items.count()} articles à migrer")
                
                # Récupérer ou créer le panier de l'utilisateur
                user_cart, created = Cart.objects.get_or_create(user=user)
                
                # Copier tous les items du panier anonyme vers le panier utilisateur
                migrated_items = 0
                for anonymous_item in anonymous_cart.cart_items.all():
                    # Vérifier si l'item existe déjà dans le panier utilisateur
                    existing_item = None
                    user_cart_items = user_cart.cart_items.filter(product=anonymous_item.product)
                    
                    for item in user_cart_items:
                        # Vérifier les couleurs
                        colors_match = (
                            set(item.colors.all().values_list('id', flat=True)) == 
                            set(anonymous_item.colors.all().values_list('id', flat=True))
                        )
                        # Vérifier les tailles
                        sizes_match = (
                            set(item.sizes.all().values_list('id', flat=True)) == 
                            set(anonymous_item.sizes.all().values_list('id', flat=True))
                        )
                        
                        if colors_match and sizes_match:
                            existing_item = item
                            break
                    
                    if existing_item:
                        # Mettre à jour la quantité
                        old_quantity = existing_item.quantity
                        existing_item.quantity += anonymous_item.quantity
                        existing_item.save()
                        print(f"  ✅ Quantité mise à jour pour {anonymous_item.product.title}: {old_quantity} + {anonymous_item.quantity} = {existing_item.quantity}")
                    else:
                        # Créer un nouvel item
                        new_item = CartItem.objects.create(
                            cart=user_cart,
                            product=anonymous_item.product,
                            quantity=anonymous_item.quantity
                        )
                        # Copier les couleurs et tailles
                        if anonymous_item.colors.exists():
                            new_item.colors.set(anonymous_item.colors.all())
                        if anonymous_item.sizes.exists():
                            new_item.sizes.set(anonymous_item.sizes.all())
                        print(f"  ✅ Nouvel article ajouté: {anonymous_item.product.title} x{anonymous_item.quantity}")
                    
                    migrated_items += 1
                
                # Supprimer le panier anonyme seulement si la migration a réussi
                if migrated_items > 0:
                    anonymous_cart.delete()
                    print(f"✅ Migration terminée: {migrated_items} articles migrés, panier anonyme supprimé")
                else:
                    print("⚠️ Aucun article migré, panier anonyme conservé")
            else:
                print("ℹ️ Aucun panier anonyme à migrer")
                
    except Exception as e:
        # Log l'erreur mais ne pas bloquer la connexion
        print(f"❌ Erreur lors de la migration du panier: {str(e)}")
        import traceback
        print(traceback.format_exc())
