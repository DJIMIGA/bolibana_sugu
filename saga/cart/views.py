from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from product.models import Product

from cart.models import Cart, CartItem, Order, OrderItem
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from product.models import ShippingMethod, Size
from product.models import Clothing
from product.services import ProductAttributeValidator
from .utils import render_cart_updates, render_cart_item, render_cart_count, render_payment_summary, render_cart_total
from accounts.forms import ShippingAddressForm
from accounts.models import ShippingAddress
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.db import transaction
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def add_to_cart(request, product_id):
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, id=product_id)
            
            # Vérifier si le produit est un vêtement
            is_clothing = hasattr(product, 'clothing_product')
            
            color_id = request.POST.get('color_id')
            size_id = request.POST.get('size_id')
            quantity = int(request.POST.get('quantity', 1))

            # Validation des attributs uniquement si c'est un vêtement
            if is_clothing:
                validator = ProductAttributeValidator(product)
                validator.validate_attributes(attributes={'color_id': color_id, 'size_id': size_id})

            # Récupérer ou créer le panier
            cart = Cart.get_or_create_cart(request)

            # Vérifier si l'article existe déjà dans le panier avec les mêmes attributs
            existing_item = None
            cart_items = cart.cart_items.filter(product=product)
            
            for item in cart_items:
                # Pour les vêtements, vérifier les attributs
                if is_clothing:
                    # Vérifier si les couleurs correspondent exactement
                    item_colors = set(item.colors.values_list('id', flat=True))
                    request_colors = {int(color_id)} if color_id else set()
                    colors_match = item_colors == request_colors
                    
                    # Vérifier si les tailles correspondent exactement
                    item_sizes = set(item.sizes.values_list('id', flat=True))
                    request_sizes = {int(size_id)} if size_id else set()
                    sizes_match = item_sizes == request_sizes
                    
                    if colors_match and sizes_match:
                        existing_item = item
                        break
                else:
                    # Pour les produits non-vêtements, vérifier uniquement le produit
                    existing_item = item
                    break

            if existing_item:
                # Mettre à jour la quantité
                existing_item.quantity += quantity
                existing_item.save()
                cart_item = existing_item
            else:
                # Créer un nouvel article
                cart_item = CartItem.objects.create(
                    cart=cart,
                    product=product,
                    quantity=quantity
                )
                # Ajouter les couleurs et tailles uniquement si c'est un vêtement
                if is_clothing:
                    if color_id:
                        cart_item.colors.add(color_id)
                    if size_id:
                        cart_item.sizes.add(size_id)

            # Générer la réponse
            response = HttpResponse()
            response['HX-Trigger'] = 'cartUpdated'
            response.write(render_cart_updates(request, cart, cart_item))
            return response

        except ValidationError as e:
            messages.error(request, str(e))
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            messages.error(request, _("Une erreur est survenue lors de l'ajout au panier."))
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)


def cart(request):
    cart = Cart.get_or_create_cart(request)
    cart_items = cart.cart_items.all().select_related('product')

    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    html = render_to_string('cart/components/_cart_content.html', context, request=request)
    return HttpResponse(html)   


def checkout(request):
    cart = Cart.get_or_create_cart(request)
    cart_items = cart.cart_items.all()
    product = Product.objects.all()
    shipping_method = ShippingMethod.objects.all()

    context = {
        'product': product,
        'shipping_method': shipping_method,
        'cart_items': cart_items,
    }
    return render(request, 'checkout.html',context)


def delete_cart(request):
    cart = Cart.get_or_create_cart(request)
    cart.delete()
    
    cart_content_html = render_to_string('cart/components/_cart_content.html', {
        'cart': None,
        'cart_items': [],
    }, request=request)
    
    cart_total_html = f'<div id="cart-total" hx-swap-oob="true">' + render_to_string('cart/components/_cart_total.html', {
        'cart': None,
        'cart_items': [],
    }, request=request) + '</div>'
    
    cart_count_html = f'<span id="cart-count" hx-swap-oob="true" class="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center animate-pulse">0</span>'
    
    return HttpResponse(cart_content_html + cart_total_html + cart_count_html)


def increase_quantity(request, cartitem_id):
    if request.method == 'POST':
        cart = Cart.get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=cartitem_id, cart=cart)
        cart_item.quantity += 1
        cart_item.save()
        
        return HttpResponse(render_cart_updates(request, cart, cart_item))



def decrease_quantity(request, cartitem_id):
    if request.method == 'POST':
        cart = Cart.get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=cartitem_id, cart=cart)
        
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            return HttpResponse(render_cart_updates(request, cart, cart_item))
        else:
            cart_item.delete()
            return HttpResponse(render_cart_updates(request, cart))


@login_required
def payment_online(request):
    print("\n=== Début de payment_online ===")
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.cart_items.all().select_related('product')
    print(f"Panier trouvé pour l'utilisateur {request.user.email} avec {cart_items.count()} articles")
    
    # Récupérer la méthode de paiement depuis l'URL
    payment_method = request.GET.get('payment_method', 'online_payment')
    print(f"Méthode de paiement sélectionnée: {payment_method}")
    
    if request.method == 'POST':
        print("\n=== Traitement du formulaire POST ===")
        form = ShippingAddressForm(request.POST)
        shipping_method_id = request.POST.get('shipping_method')
        address_choice = request.POST.get('address_choice')
        
        # Ne valider le formulaire que si on crée une nouvelle adresse
        if address_choice == 'new':
            print("Validation du formulaire pour nouvelle adresse")
            # Ajouter le type d'adresse pour la nouvelle adresse
            if not request.POST.get('address_type'):
                form.data = form.data.copy()
                form.data['address_type'] = 'shipping'
            
            if not form.is_valid():
                print("\n=== Formulaire invalide ===")
                print(f"Erreurs du formulaire: {form.errors}")
                # ... reste du code pour GET ...
                return render(request, 'payment_online.html', context)
        
        if shipping_method_id:
            print("\n=== Création de la commande ===")
            try:
                # Créer ou récupérer l'adresse
                if address_choice == 'default':
                    print("Utilisation de l'adresse par défaut")
                    address = ShippingAddress.objects.get(user=request.user, is_default=True)
                else:
                    print("Création d'une nouvelle adresse")
                    address = form.save(commit=False)
                    address.user = request.user
                    address.save()
                    
                    if request.POST.get('is_default'):
                        print("Définition comme adresse par défaut")
                        ShippingAddress.objects.filter(user=request.user).update(is_default=False)
                        address.is_default = True
                        address.save()
                
                # Créer la commande
                shipping_method = ShippingMethod.objects.get(id=shipping_method_id)
                print(f"\nCréation de la commande:")
                print(f"- Total panier: {cart.get_total_price()}")
                print(f"- Frais de livraison: {shipping_method.price}")
                print(f"- Méthode de paiement: {payment_method}")
                
                order = Order.objects.create(
                    user=request.user,
                    shipping_address=address,
                    shipping_method=shipping_method,
                    payment_method=payment_method,
                    subtotal=cart.get_total_price(),
                    shipping_cost=shipping_method.price,
                    total=cart.get_total_price() + shipping_method.price
                )
                print(f"Commande créée avec ID: {order.id}")
                
                # Créer les éléments de la commande
                print("\nCréation des éléments de la commande:")
                for item in cart_items:
                    print(f"- Article: {item.product.title} x{item.quantity}")
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price
                    )
                    if item.colors.exists():
                        print(f"  - Couleurs: {', '.join(c.name for c in item.colors.all())}")
                        order_item.colors.set(item.colors.all())
                    if item.sizes.exists():
                        print(f"  - Tailles: {', '.join(s.name for s in item.sizes.all())}")
                        order_item.sizes.set(item.sizes.all())
                
                # Vider le panier
                print("\nSuppression du panier")
                cart.delete()
                
                # Envoyer l'email de confirmation
                print("Envoi de l'email de confirmation")
                send_order_confirmation_email(order)
                
                print("\n=== Redirection vers la confirmation ===")
                return redirect('cart:order_confirmation', order_id=order.id)
                
            except Exception as e:
                print(f"\n!!! ERREUR lors de la création de la commande: {str(e)}")
                raise
        else:
            print("\n=== Formulaire invalide ===")
            print(f"Erreurs du formulaire: {form.errors}")
            print(f"Méthode de livraison manquante: {not shipping_method_id}")
    
    # GET request
    print("\n=== Affichage du formulaire (GET) ===")
    default_address = ShippingAddress.objects.filter(user=request.user, is_default=True).first()
    form = ShippingAddressForm(instance=default_address) if default_address else ShippingAddressForm()
    
    # Calculer le total de la commande
    order_total = cart.get_total_price()
    shipping_cost = 1000
    total_with_shipping = order_total + shipping_cost
    
    print(f"Total panier: {order_total}")
    print(f"Frais de livraison: {shipping_cost}")
    print(f"Total avec livraison: {total_with_shipping}")
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'order_total': order_total,
        'shipping_cost': shipping_cost,
        'total_with_shipping': total_with_shipping,
        'shipping_methods': ShippingMethod.objects.all(),
        'form': form,
        'default_address': default_address,
        'is_checkout': True,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'selected_payment_method': payment_method
    }
    
    print("=== Fin de payment_online ===\n")
    return render(request, 'payment_online.html', context)


def send_order_confirmation_email(order):
    # Récupérer le domain_url
    domain_url = "https://a7d6-2a02-842a-3cca-9501-5d98-6d31-91ad-1bbd.ngrok-free.app"
    
    subject = f'Confirmation de votre commande {order.order_number}'
    html_message = render_to_string('cart/emails/order_confirmation.html', {
        'order': order,
        'domain_url': domain_url
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email],
        html_message=html_message
    )


@login_required
def payment_delivery(request):
    print("\n=== Début de payment_delivery ===")
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.cart_items.all().select_related('product')
    print(f"Panier trouvé pour l'utilisateur {request.user.email} avec {cart_items.count()} articles")
    
    if request.method == 'POST':
        print("\n=== Traitement du formulaire POST ===")
        form = ShippingAddressForm(request.POST)
        shipping_method_id = request.POST.get('shipping_method')
        address_choice = request.POST.get('address_choice')
        
        # Ne valider le formulaire que si on crée une nouvelle adresse
        if address_choice == 'new':
            print("Validation du formulaire pour nouvelle adresse")
            # Ajouter le type d'adresse pour la nouvelle adresse
            if not request.POST.get('address_type'):
                form.data = form.data.copy()
                form.data['address_type'] = 'shipping'
            
            if not form.is_valid():
                print("\n=== Formulaire invalide ===")
                print(f"Erreurs du formulaire: {form.errors}")
                # ... reste du code pour GET ...
                return render(request, 'cart/payment_delivery.html', context)
        
        if shipping_method_id:
            print("\n=== Création de la commande ===")
            try:
                # Créer ou récupérer l'adresse
                if address_choice == 'default':
                    print("Utilisation de l'adresse par défaut")
                    address = ShippingAddress.objects.get(user=request.user, is_default=True)
                else:
                    print("Création d'une nouvelle adresse")
                    address = form.save(commit=False)
                    address.user = request.user
                    address.save()
                    
                    if request.POST.get('is_default'):
                        print("Définition comme adresse par défaut")
                        ShippingAddress.objects.filter(user=request.user).update(is_default=False)
                        address.is_default = True
                        address.save()
                
                # Créer la commande
                shipping_method = ShippingMethod.objects.get(id=shipping_method_id)
                print(f"\nCréation de la commande:")
                print(f"- Total panier: {cart.get_total_price()}")
                print(f"- Frais de livraison: {shipping_method.price}")
                
                order = Order.objects.create(
                    user=request.user,
                    shipping_address=address,
                    shipping_method=shipping_method,
                    subtotal=cart.get_total_price(),
                    shipping_cost=shipping_method.price,
                    total=cart.get_total_price() + shipping_method.price
                )
                print(f"Commande créée avec ID: {order.id}")
                
                # Créer les éléments de la commande
                print("\nCréation des éléments de la commande:")
                for item in cart_items:
                    print(f"- Article: {item.product.title} x{item.quantity}")
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price
                    )
                    if item.colors.exists():
                        print(f"  - Couleurs: {', '.join(c.name for c in item.colors.all())}")
                        order_item.colors.set(item.colors.all())
                    if item.sizes.exists():
                        print(f"  - Tailles: {', '.join(s.name for s in item.sizes.all())}")
                        order_item.sizes.set(item.sizes.all())
                
                # Vider le panier
                print("\nSuppression du panier")
                cart.delete()
                
                # Envoyer l'email de confirmation
                print("Envoi de l'email de confirmation")
                send_order_confirmation_email(order)
                
                print("\n=== Redirection vers la confirmation ===")
                return redirect('cart:order_confirmation', order_id=order.id)
                
            except Exception as e:
                print(f"\n!!! ERREUR lors de la création de la commande: {str(e)}")
                raise
        else:
            print("\n=== Formulaire invalide ===")
            print(f"Erreurs du formulaire: {form.errors}")
            print(f"Méthode de livraison manquante: {not shipping_method_id}")
    
    # GET request
    print("\n=== Affichage du formulaire (GET) ===")
    default_address = ShippingAddress.objects.filter(user=request.user, is_default=True).first()
    form = ShippingAddressForm(instance=default_address) if default_address else ShippingAddressForm()
    
    # Calculer le total de la commande
    order_total = cart.get_total_price()
    shipping_cost = 1000
    total_with_shipping = order_total + shipping_cost
    
    print(f"Total panier: {order_total}")
    print(f"Frais de livraison: {shipping_cost}")
    print(f"Total avec livraison: {total_with_shipping}")
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'order_total': order_total,
        'shipping_cost': shipping_cost,
        'total_with_shipping': total_with_shipping,
        'shipping_methods': ShippingMethod.objects.all(),
        'form': form,
        'default_address': default_address,
        'is_checkout': True
    }
    
    print("=== Fin de payment_delivery ===\n")
    return render(request, 'cart/payment_delivery.html', context)



def get_product_options(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    clothing = getattr(product, 'clothing_product', None)
    
    if clothing:
        colors = clothing.color.all() if clothing.color.exists() else []
        product_sizes = clothing.size.all() if clothing.size.exists() else []
    else:
        colors = []
        product_sizes = []
    
    context = {
        'product': product,
        'colors': colors,
        'product_sizes': product_sizes,
        'is_clothing': clothing is not None
    }
    
    # Renvoyer uniquement le composant des options
    return render(request, 'cart/components/_product_options.html', context)



def remove_from_cart(request, cartitem_id):
    if request.method == 'DELETE' and request.htmx:
        cart = Cart.get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=cartitem_id, cart=cart)
        cart_item.delete()
        
        return HttpResponse(render_cart_updates(request, cart))
    
    return HttpResponse("Méthode non autorisée", status=400)


@login_required
def update_shipping(request):
    if request.method == 'POST':
        shipping_method_id = request.POST.get('shipping_method')
        payment_method = request.POST.get('payment_method', 'online_payment')
        shipping_method = get_object_or_404(ShippingMethod, id=shipping_method_id)
        
        cart = Cart.objects.get(user=request.user)
        order_total = cart.get_total_price()
        total_with_shipping = order_total + shipping_method.price
        
        context = {
            'cart': cart,
            'cart_items': cart.cart_items.all(),
            'order_total': order_total,
            'selected_shipping_method': shipping_method,
            'selected_payment_method': payment_method,
            'total_with_shipping': total_with_shipping
        }
        
        return render(request, 'cart/components/_order_details.html', context)


@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order,
        'items': order.items.all().select_related('product')
    }
    return render(request, 'cart/order_confirmation.html', context)


@login_required
def my_orders(request):
    # Récupérer toutes les commandes de l'utilisateur, triées par date de création (la plus récente en premier)
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'cart/my_orders.html', context)


@csrf_exempt
def stripe_webhook(request):
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=webhook_secret
        )
        data = event['data']
        event_type = event['type']
    except Exception as e:
        return HttpResponse(str(e), status=400)

    data_object = data['object']

    print('event ' + event_type)

    if event_type == 'checkout.session.completed':
        session = data_object
        
        try:
            # Créer la commande
            cart = Cart.objects.get(id=session.metadata.cart_id)
            shipping_method = ShippingMethod.objects.first()
            
            order = Order.objects.create(
                user_id=session.metadata.user_id,
                stripe_session_id=session.id,
                stripe_payment_status='paid',
                payment_method='online_payment',
                is_paid=True,
                shipping_method=shipping_method,
                subtotal=cart.get_total_price(),
                shipping_cost=shipping_method.price if shipping_method else 0,
                total=cart.get_total_price() + (shipping_method.price if shipping_method else 0)
            )

            # Envoyer l'email de confirmation
            send_order_confirmation_email(order)
            
            print('🔔 Payment succeeded!')
        except Exception as e:
            print(f'❌ Error: {str(e)}')

    return JsonResponse({'status': 'success'})


@login_required
def create_checkout_session(request):
    try:
        cart = Cart.get_or_create_cart(request)
        cart_items = cart.cart_items.all().select_related('product')
        
        # Récupérer la méthode de livraison sélectionnée
        shipping_method_id = request.POST.get('shipping_method')
        if not shipping_method_id:
            messages.error(request, "Veuillez sélectionner une méthode de livraison.")
            return redirect('cart:payment_online')
            
        shipping_method = ShippingMethod.objects.get(id=shipping_method_id)
        
        # Récupérer l'adresse de livraison
        address_choice = request.POST.get('address_choice')
        if address_choice == 'default':
            shipping_address = ShippingAddress.objects.get(user=request.user, is_default=True)
        else:
            # Créer une nouvelle adresse à partir du formulaire
            form = ShippingAddressForm(request.POST)
            if not form.is_valid():
                messages.error(request, "Veuillez corriger les erreurs dans le formulaire d'adresse.")
                return redirect('cart:payment_online')
            shipping_address = form.save(commit=False)
            shipping_address.user = request.user
            shipping_address.save()
            
            if request.POST.get('is_default'):
                ShippingAddress.objects.filter(user=request.user).exclude(id=shipping_address.id).update(is_default=False)
                shipping_address.is_default = True
                shipping_address.save()
        
        # Utilisez request.build_absolute_uri() pour obtenir l'URL de base
        domain_url = request.build_absolute_uri('/').rstrip('/')
        
        if 'ngrok' in domain_url:
            print(f"Utilisation de l'URL ngrok: {domain_url}")
        else:
            domain_url = "https://a7d6-2a02-842a-3cca-9501-5d98-6d31-91ad-1bbd.ngrok-free.app"
            print(f"Utilisation de l'URL locale: {domain_url}")

        line_items = []
        for item in cart_items:
            # Préparer le nom du produit avec ses attributs
            product_name = item.product.title
            if item.colors.exists():
                product_name += f" - {item.colors.first().name}"
            if item.sizes.exists():
                product_name += f" - Taille {item.sizes.first().name}"

            # Construire l'URL absolue de l'image
            image_url = None
            if item.product.image:
                image_url = f"{domain_url}/media/{item.product.image}"

            # Créer le produit Stripe
            stripe_product_data = {
                'name': product_name,
                'metadata': {
                    'product_id': item.product.id,
                    'colors': ', '.join([c.name for c in item.colors.all()]),
                    'sizes': ', '.join([s.name for s in item.sizes.all()]),
                }
            }
            
            if image_url:
                stripe_product_data['images'] = [image_url]

            stripe_product = stripe.Product.create(**stripe_product_data)

            # Créer le prix avec les bonnes métadonnées
            price = stripe.Price.create(
                product=stripe_product.id,
                unit_amount=int(item.product.price),
                currency='xof',
            )

            # Ajouter l'item avec sa quantité
            line_items.append({
                'price': price.id,
                'quantity': item.quantity,
                'adjustable_quantity': {
                    'enabled': True,
                    'minimum': 1,
                    'maximum': 10,
                },
            })

        # Créer la session avec plus d'options
        checkout_session = stripe.checkout.Session.create(
            customer_email=request.user.email,
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=domain_url + reverse('cart:payment_success') + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=domain_url + reverse('cart:payment_cancel'),
            metadata={
                'cart_id': cart.id,
                'user_id': request.user.id,
                'shipping_method_id': shipping_method_id,
                'shipping_address_id': shipping_address.id,
            },
            shipping_address_collection={
                'allowed_countries': ['ML']  # Mali uniquement
            },
            shipping_options=[{
                'shipping_rate_data': {
                    'type': 'fixed_amount',
                    'fixed_amount': {
                        'amount': int(shipping_method.price),
                        'currency': 'xof',
                    },
                    'display_name': shipping_method.name,
                    'delivery_estimate': {
                        'minimum': {'unit': 'business_day', 'value': shipping_method.min_delivery_days},
                        'maximum': {'unit': 'business_day', 'value': shipping_method.max_delivery_days},
                    }
                }
            }],
            locale='fr',  # Interface en français
        )

        return redirect(checkout_session.url, code=303)

    except Exception as e:
        print(f"Erreur lors de la création de la session Stripe: {str(e)}")
        messages.error(request, "Une erreur est survenue lors de la création de la session de paiement.")
        return redirect('cart:checkout')


@login_required
def payment_success(request):
    session_id = request.GET.get('session_id')
    if session_id:
        try:
            # Vérifier la session Stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            session = stripe.checkout.Session.retrieve(session_id)
            
            # Créer la commande
            cart = Cart.objects.get(id=session.metadata.cart_id)
            shipping_method = ShippingMethod.objects.get(id=session.metadata.shipping_method_id)
            
            # Récupérer l'adresse de livraison depuis la session Stripe
            shipping_details = session.shipping_details
            if not shipping_details:
                raise ValueError("Aucune adresse de livraison trouvée dans la session Stripe")
            
            # Créer une nouvelle adresse de livraison
            shipping_address = ShippingAddress.objects.create(
                user=request.user,
                full_name=shipping_details.name,
                street_address=shipping_details.address.line1,
                quarter=shipping_details.address.line2 or '',
                city=shipping_details.address.city,
                is_default=True
            )
            
            # Mettre à jour les autres adresses pour ne plus être par défaut
            ShippingAddress.objects.filter(user=request.user).exclude(id=shipping_address.id).update(is_default=False)
            
            # Créer la commande avec l'adresse de livraison
            order = Order.objects.create(
                user=request.user,
                shipping_address=shipping_address,
                stripe_session_id=session_id,
                stripe_payment_status='paid',
                payment_method='online_payment',
                is_paid=True,
                shipping_method=shipping_method,
                subtotal=cart.get_total_price(),
                shipping_cost=shipping_method.price,
                total=cart.get_total_price() + shipping_method.price
            )

            # Créer les éléments de la commande
            for item in cart.cart_items.all():
                order_item = OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
                if item.colors.exists():
                    order_item.colors.set(item.colors.all())
                if item.sizes.exists():
                    order_item.sizes.set(item.sizes.all())

            # Vider le panier
            cart.delete()

            # Envoyer l'email de confirmation
            send_order_confirmation_email(order)

            return redirect('cart:order_confirmation', order_id=order.id)

        except Exception as e:
            print(f"Erreur lors du traitement du paiement: {str(e)}")
            messages.error(request, "Une erreur est survenue lors du traitement de votre paiement.")
            return redirect('cart:payment_cancel')

    return redirect('cart:payment_online')


@login_required
def payment_cancel(request):
    messages.warning(request, "Le paiement a été annulé.")
    return redirect('cart:payment_online')