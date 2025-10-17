from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from product.models import Product

from cart.models import Cart, CartItem, Order, OrderItem
from cart.services import CartService
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
from product.models import Phone
from decimal import Decimal
from .payment_config import (
    get_available_payment_methods, 
    get_payment_method_display_name, 
    get_disabled_payment_method_message,
    get_shipping_summary_for_display
)
import logging
import os
import json
from datetime import datetime
from django.utils import timezone
from core.utils import track_purchase, track_add_to_cart, track_view_cart, track_initiate_checkout
from core.facebook_conversions import facebook_conversions
from .orange_money_service import orange_money_service



def add_to_cart(request, product_id):
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, id=product_id)
            
            # Validation de sécurité : quantité
            try:
                quantity = int(request.POST.get('quantity', 1))
            except (ValueError, TypeError):
                quantity = 1
            
            # Limites de sécurité
            max_quantity = 50
            if quantity > max_quantity:
                messages.error(request, f"❌ Quantité maximum autorisée : {max_quantity}")
                messages_html = f'<div id="messages-container" hx-swap-oob="true">' + render_to_string('includes/_messages.html', {}, request=request) + '</div>'
                return HttpResponse(messages_html, status=400)
            
            if quantity <= 0:
                messages.error(request, "❌ Quantité invalide")
                messages_html = f'<div id="messages-container" hx-swap-oob="true">' + render_to_string('includes/_messages.html', {}, request=request) + '</div>'
                return HttpResponse(messages_html, status=400)

            # Récupérer ou créer le panier
            cart = Cart.get_or_create_cart(request)

            # Utiliser le service pour ajouter au panier
            success, message = CartService.add_to_cart(
                cart=cart,
                product=product,
                quantity=quantity
            )

            if success:
                # Récupérer l'item ajouté ou mis à jour
                cart_item = cart.cart_items.filter(product=product).first()
                
                try:
                    # Ajouter le message Django
                    messages.success(request, f"✅ {message}")
                    
                    # Rendre les messages Django avec hx-swap-oob
                    messages_html = f'<div id="messages-container" hx-swap-oob="true">' + render_to_string('includes/_messages.html', {}, request=request) + '</div>'
                    
                    # Générer la réponse avec les mises à jour du panier
                    cart_updates = render_cart_updates(request, cart, cart_item)
                    
                    # Tracking de l'ajout au panier
                    track_add_to_cart(
                        request=request,
                        product_id=product.id,
                        product_name=product.title,
                        quantity=quantity,
                        price=str(product.price)
                    )
                    
                    # Envoyer l'événement AddToCart à Facebook
                    if request.user.is_authenticated:
                        user_data = {
                            "email": request.user.email,
                            "phone": getattr(request.user, 'phone', '')
                        }
                        
                        facebook_conversions.send_add_to_cart_event(
                            user_data=user_data,
                            content_name=product.title,
                            value=float(product.price),
                            currency="XOF"
                        )
                    
                    return HttpResponse(messages_html + cart_updates)
                except Exception as e:
                    # Si le rendu échoue, retourner une réponse simple
                    messages.success(request, f"✅ {message}")
                    return JsonResponse({'success': True, 'message': message})
            else:
                # Erreur de stock - Utiliser les messages Django
                messages.error(request, f"❌ {message}")
                messages_html = f'<div id="messages-container" hx-swap-oob="true">' + render_to_string('includes/_messages.html', {}, request=request) + '</div>'
                return HttpResponse(messages_html, status=400)

        except ValidationError as e:
            messages.error(request, str(e))
            messages_html = render_to_string('includes/_messages.html', {}, request=request)
            return HttpResponse(messages_html, status=400)
        except Exception as e:
            messages.error(request, _("Une erreur est survenue lors de l'ajout au panier."))
            messages_html = render_to_string('includes/_messages.html', {}, request=request)
            return HttpResponse(messages_html, status=500)

    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)


def cart(request):
    cart = Cart.get_or_create_cart(request)
    cart_items = cart.cart_items.all().select_related('product')

    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    
    # Tracking de la vue du panier
    track_view_cart(
        request=request,
        total_amount=str(cart.get_total_price()),
        currency='XOF',
        items_count=cart.cart_items.count(),
        cart_id=cart.id
    )
    
    # Si c'est une requête AJAX/HTMX, retourner juste le composant
    if request.headers.get('HX-Request'):
        html = render_to_string('cart/components/_cart_content.html', context, request=request)
        return HttpResponse(html)   
    
    # Sinon, retourner le template complet avec base.html
    return render(request, 'cart/cart.html', context)


def checkout(request):
    cart = Cart.get_or_create_cart(request)
    
    # Récupérer le type de produits et le type de paiement demandés
    product_type = request.GET.get('type', 'all')  # 'classic', 'salam', 'mixed', ou 'all'
    payment_type = request.GET.get('payment', 'flexible')  # 'flexible', 'immediate', ou 'all'
    
    # Détecter automatiquement si le panier est mixte
    classic_items = cart.cart_items.filter(product__is_salam=False)
    salam_items = cart.cart_items.filter(product__is_salam=True)
    is_mixed_cart = classic_items.exists() and salam_items.exists()
    
    # Si c'est un panier mixte et qu'aucun type n'est spécifié, ou si type=mixed est demandé
    if (is_mixed_cart and product_type == 'all' and payment_type == 'flexible') or product_type == 'mixed':
        # Calculer les totaux correctement en utilisant get_total_price()
        classic_total = sum(item.get_total_price() for item in classic_items)
        salam_total = sum(item.get_total_price() for item in salam_items)
        
        context = {
            'cart': cart,
            'is_mixed_cart': True,
            'classic_items': classic_items,
            'salam_items': salam_items,
            'classic_count': classic_items.count(),
            'salam_count': salam_items.count(),
            'classic_total': classic_total,
            'salam_total': salam_total,
        }
        
        # Tracking du début de commande mixte
        total_amount = classic_total + salam_total
        total_items = classic_items.count() + salam_items.count()
        track_initiate_checkout(
            request=request,
            total_amount=str(total_amount),
            currency='XOF',
            items_count=total_items,
            cart_id=cart.id
        )
        
        # Envoyer l'événement InitiateCheckout à Facebook
        if request.user.is_authenticated:
            user_data = {
                "email": request.user.email,
                "phone": getattr(request.user, 'phone', '')
            }
            
            facebook_conversions.send_initiate_checkout_event(
                user_data=user_data,
                content_name="Commande BoliBana",
                value=float(total_amount),
                currency="XOF"
            )
        
        return render(request, 'checkout_mixed.html', context)
    
    # Valider le panier avant d'afficher la page de commande
    is_valid, errors = CartService.validate_cart_for_checkout(cart, product_type)
    
    if not is_valid:
        # Afficher les erreurs et rediriger vers le panier
        for error in errors:
            messages.error(request, f"❌ {error}")
        return redirect('cart:cart')
    
    # Filtrer les items selon le type demandé
    if product_type == 'classic':
        cart_items = cart.cart_items.filter(product__is_salam=False)
        if not cart_items.exists():
            messages.warning(request, "🛒 Aucun produit classique dans votre panier")
            return redirect('cart:cart')
    elif product_type == 'salam':
        cart_items = cart.cart_items.filter(product__is_salam=True)
        if not cart_items.exists():
            messages.warning(request, "🛒 Aucun produit Salam dans votre panier")
            return redirect('cart:cart')
    else:
        cart_items = cart.cart_items.all()
    
    # Vérifier s'il y a des produits Salam dans le panier (pour tous les cas)
    salam_items_in_cart = cart.cart_items.filter(product__is_salam=True)
    has_salam_products = salam_items_in_cart.exists()
    
    # Déterminer les méthodes de paiement disponibles selon le type
    if payment_type == 'immediate':
        # Pour le paiement immédiat : toutes les méthodes sauf paiement à la livraison
        available_payment_methods = [method for method in get_available_payment_methods() if method != 'cash_on_delivery']
        payment_required = True
    elif product_type == 'salam':
        # Pour les produits Salam : toutes les méthodes sauf paiement à la livraison
        available_payment_methods = [method for method in get_available_payment_methods() if method != 'cash_on_delivery']
        payment_required = True
    elif product_type == 'classic' or payment_type == 'flexible':
        # Pour les produits classiques ou paiement flexible : vérifier s'il y a des produits Salam
        if has_salam_products:
            # S'il y a des produits Salam dans le panier, pas de paiement à la livraison
            available_payment_methods = [method for method in get_available_payment_methods() if method != 'cash_on_delivery']
            payment_required = True
            messages.warning(request, "⚠️ **Attention** : Votre panier contient des produits Salam qui nécessitent un paiement immédiat. Le paiement à la livraison n'est pas disponible.")
        else:
            # Sinon, toutes les méthodes incluant paiement à la livraison
            available_payment_methods = get_available_payment_methods()
            payment_required = False
    else:
        # Par défaut : vérifier s'il y a des produits Salam dans le panier
        if has_salam_products:
            # S'il y a des produits Salam, pas de paiement à la livraison
            available_payment_methods = [method for method in get_available_payment_methods() if method != 'cash_on_delivery']
            payment_required = True
            messages.warning(request, "⚠️ **Attention** : Votre panier contient des produits Salam qui nécessitent un paiement immédiat. Le paiement à la livraison n'est pas disponible.")
        else:
            # Sinon, toutes les méthodes
            available_payment_methods = get_available_payment_methods()
            payment_required = False
    
    product = Product.objects.all()
    shipping_method = ShippingMethod.objects.all()
    
    # Calculer les totaux selon le type de produits sélectionné
    if product_type == 'classic':
        # Pour les produits classiques seulement
        order_total = sum(item.get_total_price() for item in cart_items)
        total_items = cart_items.count()
    elif product_type == 'salam':
        # Pour les produits Salam seulement
        order_total = sum(item.get_total_price() for item in cart_items)
        total_items = cart_items.count()
    else:
        # Pour tous les produits
        order_total = sum(item.get_total_price() for item in cart_items)
        total_items = cart_items.count()

    context = {
        'cart': cart,
        'product': product,
        'shipping_method': shipping_method,
        'cart_items': cart_items,
        'order_total': order_total,  # Total calculé selon le type de produits
        'total_items': total_items,  # Nombre d'articles selon le type
        'is_checkout': True,  # Flag pour indiquer qu'on est sur la page de commande
        'product_type': product_type,  # Type de produits sélectionné
        'payment_type': payment_type,  # Type de paiement sélectionné
        'available_payment_methods': available_payment_methods,  # Méthodes de paiement disponibles
        'payment_required': payment_required,  # Si le paiement est obligatoire
        'is_mixed_cart': is_mixed_cart,  # Si le panier est mixte
        'has_salam_products': has_salam_products,  # Si le panier contient des produits Salam
    }
    
    # Tracking du début de commande
    track_initiate_checkout(
        request=request,
        total_amount=str(order_total),
        currency='XOF',
        items_count=total_items,
        cart_id=cart.id
    )
    
    # Envoyer l'événement InitiateCheckout à Facebook
    if request.user.is_authenticated:
        user_data = {
            "email": request.user.email,
            "phone": getattr(request.user, 'phone', '')
        }
        
        facebook_conversions.send_initiate_checkout_event(
            user_data=user_data,
            content_name="Commande BoliBana",
            value=float(order_total),
            currency="XOF"
        )
    
    return render(request, 'checkout.html', context)


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
        
        # Vérification de sécurité : s'assurer que l'item appartient au panier de l'utilisateur
        try:
            cart_item = CartItem.objects.get(id=cartitem_id, cart=cart)
        except CartItem.DoesNotExist:
            return JsonResponse({'error': 'Article non trouvé'}, status=404)
        
        # Limite de sécurité : quantité maximum par article
        max_quantity = 50
        if cart_item.quantity >= max_quantity:
            messages.error(request, f"❌ Quantité maximum atteinte ({max_quantity})")
            messages_html = f'<div id="messages-container" hx-swap-oob="true">' + render_to_string('includes/_messages.html', {}, request=request) + '</div>'
            return HttpResponse(messages_html, status=400)
        
        # Utiliser le service pour mettre à jour la quantité
        success, message = CartService.update_quantity(cart_item, cart_item.quantity + 1)
        
        if success:
            # Mettre à jour seulement l'élément spécifique et les totaux
            from .utils import render_cart_item, render_cart_count, render_cart_total
            
            # Récupérer l'élément mis à jour
            cart_item.refresh_from_db()
            
            # Générer les mises à jour
            item_html = render_cart_item(request, cart_item)
            count_html = render_cart_count(cart)
            total_html = render_cart_total(request, cart, cart.cart_items.all())
            
            return HttpResponse(item_html + count_html + total_html)
        else:
            # Erreur de stock - Utiliser les messages Django
            messages.error(request, f"❌ {message}")
            messages_html = f'<div id="messages-container" hx-swap-oob="true">' + render_to_string('includes/_messages.html', {}, request=request) + '</div>'
            return HttpResponse(messages_html, status=400)


def decrease_quantity(request, cartitem_id):
    if request.method == 'POST':
        cart = Cart.get_or_create_cart(request)
        
        # Vérification de sécurité : s'assurer que l'item appartient au panier de l'utilisateur
        try:
            cart_item = CartItem.objects.get(id=cartitem_id, cart=cart)
        except CartItem.DoesNotExist:
            return JsonResponse({'error': 'Article non trouvé'}, status=404)
        
        if cart_item.quantity > 1:
            # Utiliser le service pour mettre à jour la quantité
            success, message = CartService.update_quantity(cart_item, cart_item.quantity - 1)
            
            if success:
                # Mettre à jour seulement l'élément spécifique et les totaux
                from .utils import render_cart_item, render_cart_count, render_cart_total
                
                # Récupérer l'élément mis à jour
                cart_item.refresh_from_db()
                
                # Générer les mises à jour
                item_html = render_cart_item(request, cart_item)
                count_html = render_cart_count(cart)
                total_html = render_cart_total(request, cart, cart.cart_items.all())
                
                return HttpResponse(item_html + count_html + total_html)
            else:
                # Erreur de stock - Utiliser les messages Django
                messages.error(request, f"❌ {message}")
                messages_html = f'<div id="messages-container" hx-swap-oob="true">' + render_to_string('includes/_messages.html', {}, request=request) + '</div>'
                return HttpResponse(messages_html, status=400)
        else:
            cart_item.delete()
            # Si l'élément est supprimé, recharger tout le panier
            return HttpResponse(render_cart_updates(request, cart))


@login_required
def payment_online(request):
    print("\n" + "="*80)
    print("🚨 PAYMENT ONLINE VIEW CALLED")
    print("="*80)
    print(f"🚨 Method: {request.method}")
    print(f"🚨 User: {request.user.email}")
    # Suppression des logs sensibles
    print("="*80)
    
    try:
        cart = Cart.objects.get(user=request.user)
        print(f"🚨 Cart found: {cart.id} with {cart.cart_items.count()} items")
    except Cart.DoesNotExist:
        print("🚨 ERROR: Cart not found!")
        messages.warning(request, "🛒 Votre panier est vide. Veuillez ajouter des produits avant de procéder au paiement.")
        return redirect('cart:cart')
    
    # Récupérer le type de produits demandé
    product_type = request.GET.get('type', 'all')  # 'salam', 'classic', ou 'all'
    payment_type = request.GET.get('payment', 'flexible')  # 'flexible', 'immediate', ou 'all'
    
    # Détecter automatiquement si le panier est mixte
    classic_items = cart.cart_items.filter(product__is_salam=False)
    salam_items = cart.cart_items.filter(product__is_salam=True)
    is_mixed_cart = classic_items.exists() and salam_items.exists()
    
    # Filtrer les items selon le type demandé
    if product_type == 'salam':
        cart_items = cart.cart_items.filter(product__is_salam=True)
        if not cart_items.exists():
            messages.warning(request, "🛒 Aucun produit Salam dans votre panier")
            return redirect('cart:cart')
    elif product_type == 'classic':
        cart_items = cart.cart_items.filter(product__is_salam=False)
        if not cart_items.exists():
            messages.warning(request, "🛒 Aucun produit classique dans votre panier")
            return redirect('cart:cart')
    else:
        cart_items = cart.cart_items.all().select_related('product')
    
    print(f"Panier trouvé pour l'utilisateur {request.user.email} avec {cart_items.count()} articles")
    print(f"Type de produit: {product_type}, Panier mixte: {is_mixed_cart}")
    
    # Récupérer la méthode de paiement depuis l'URL
    payment_method = request.GET.get('payment_method', 'online_payment')
    print(f"Méthode de paiement sélectionnée: {payment_method}")
    
    # Vérifier si la méthode de paiement est disponible
    available_methods = get_available_payment_methods()
    if payment_method not in available_methods:
        messages.error(request, f"❌ **Méthode de paiement indisponible** : {payment_method} n'est pas disponible actuellement.")
        return redirect('cart:checkout')
    
    if request.method == 'POST':
        print("\n=== Traitement du formulaire (POST) ===")
        
        # Récupérer les données du formulaire
        payment_method = request.POST.get('payment_method', 'online_payment')
        product_type = request.POST.get('product_type', 'classic')
        address_choice = request.POST.get('address_choice', 'default')
        
        debug_log(f"📋 Payment method: {payment_method}")
        debug_log(f"📋 Product type: {product_type}")
        debug_log(f"📋 Address choice: {address_choice}")
        
        # Vérifier que les données essentielles sont présentes
        if not address_choice:
            debug_log("❌ ERROR: address_choice missing!")
            messages.error(request, "❌ **Erreur** : Choix d'adresse manquant")
            return redirect('cart:payment_online')
        
        # Gérer l'adresse de livraison
        address = None
        if address_choice == 'default':
            # Utiliser l'adresse par défaut
            address_id = request.POST.get('shipping_address_id')
            debug_log(f"📋 Address ID from form: {address_id}")
            
            if address_id:
                try:
                    address = ShippingAddress.objects.get(id=address_id, user=request.user)
                    debug_log(f"✅ Found default address: {address.id}")
                except ShippingAddress.DoesNotExist:
                    debug_log(f"❌ ERROR: Address {address_id} not found!")
                    messages.error(request, "❌ **Erreur** : Adresse par défaut introuvable")
                    return redirect('cart:payment_online')
            else:
                # Si pas d'ID fourni, essayer de récupérer l'adresse par défaut
                address = ShippingAddress.objects.filter(user=request.user, is_default=True).first()
                debug_log(f"📋 Found default address from DB: {address.id if address else None}")
                
                if not address:
                    debug_log("❌ ERROR: No default address found!")
                    messages.error(request, "❌ **Erreur** : Aucune adresse par défaut trouvée")
                    return redirect('cart:payment_online')
        else:
            # Pour "new", vérifier si des données d'adresse sont fournies
            debug_log("📋 New address option selected")
            
            # Vérifier si des données d'adresse sont présentes dans le formulaire
            full_name = request.POST.get('full_name')
            street_address = request.POST.get('street_address')
            quarter = request.POST.get('quarter')
            
            if full_name and street_address and quarter:
                # Créer une nouvelle adresse à partir des données du formulaire
                debug_log("📋 Creating new address from form data...")
                try:
                    form = ShippingAddressForm(request.POST)
                    if form.is_valid():
                        address = form.save(commit=False)
                        address.user = request.user
                        address.save()
                        debug_log(f"✅ Created new address: {address.id}")
                        
                        # Définir comme adresse par défaut si demandé
                        if request.POST.get('is_default'):
                            debug_log("📋 Setting as default address")
                            ShippingAddress.objects.filter(user=request.user).update(is_default=False)
                            address.is_default = True
                            address.save()
                            debug_log("✅ Set as default address")
                    else:
                        debug_log(f"❌ Form errors: {form.errors}")
                        for field, errors in form.errors.items():
                            for error in errors:
                                messages.error(request, f"❌ **Erreur** : {error}")
                        return redirect('cart:payment_online')
                except Exception as e:
                    debug_log(f"❌ ERROR creating address: {str(e)}")
                    messages.error(request, f"❌ **Erreur** : Impossible de créer l'adresse - {str(e)}")
                    return redirect('cart:payment_online')
            else:
                # Aucune donnée d'adresse fournie, rediriger vers la gestion des adresses
                debug_log("❌ No address data provided in form")
                messages.error(request, "❌ **Erreur** : Pour le paiement en ligne, vous devez d'abord créer une adresse de livraison")
                return redirect('accounts:addresses')
        
        if not address:
            debug_log("❌ ERROR: No address found!")
            messages.error(request, "❌ **Erreur** : Aucune adresse de livraison valide")
            return redirect('cart:payment_online')
        
        debug_log(f"✅ Final address: {address.id} - {address.full_name}")
        
        # Récupérer le panier de l'utilisateur
        debug_log("📋 Récupération du panier...")
        cart = Cart.get_or_create_cart(request)
        debug_log(f"📋 Cart ID: {cart.id}")
        debug_log(f"📋 Cart items count: {cart.cart_items.count()}")
        
        # Vérifier que le panier n'est pas vide
        if cart.cart_items.count() == 0:
            debug_log("❌ ERROR: Cart is empty!")
            messages.error(request, "❌ **Erreur** : Votre panier est vide")
            return redirect('cart:cart')
        
        # Calculer le résumé des frais de livraison
        debug_log("📋 Calcul du résumé des frais de livraison...")
        try:
            shipping_summary = get_shipping_summary_for_display(cart)
            debug_log(f"📋 Shipping summary: {shipping_summary['summary']}")
        except Exception as e:
            debug_log(f"❌ ERROR calculating shipping summary: {str(e)}")
            messages.error(request, f"❌ **Erreur** : Impossible de calculer les frais de livraison - {str(e)}")
            return redirect('cart:payment_online')

        debug_log("📋 Configuration de Stripe...")
        stripe.api_key = settings.STRIPE_SECRET_KEY
        debug_log(f"📋 Stripe API key configured: {bool(stripe.api_key)}")
        
        # Test de connexion Stripe
        try:
            debug_log("📋 Testing Stripe connection...")
            stripe.Account.retrieve()
            debug_log("✅ Stripe connection successful")
        except Exception as stripe_error:
            debug_log(f"❌ Stripe connection failed: {stripe_error}")
            messages.error(request, f"❌ **Erreur Stripe** : {str(stripe_error)}")
            return redirect('cart:payment_online')
        
        # Préparer les items pour Stripe
        debug_log("📋 Préparation des items pour Stripe...")
        line_items = []
        for item in cart.cart_items.all():
            # Utiliser le prix promotionnel si disponible, sinon le prix normal
            unit_price = item.product.discount_price if hasattr(item.product, 'discount_price') and item.product.discount_price else item.product.price
            line_item = {
                'price_data': {
                    'currency': 'xof',
                    'product_data': {
                        'name': item.product.title,
                    },
                    'unit_amount': int(unit_price),  # CFA n'a pas de centimes
                },
                'quantity': item.quantity,
            }
            line_items.append(line_item)
            debug_log(f"📋 Added line item: {item.product.title} x{item.quantity} = {unit_price} FCFA")
        
        debug_log(f"📋 Total line items: {len(line_items)}")
        
        # Construire l'URL de domaine
        debug_log("📋 Construction de l'URL de domaine...")
        domain_url = request.build_absolute_uri('/')[:-1]
        debug_log(f"📋 Domain URL: {domain_url}")
        
        # Configurer les méthodes de paiement
        debug_log("📋 Configuration des méthodes de paiement...")
        if payment_method == 'mobile_money':
            payment_method_types = ['card', 'mobile_money']
        else:
            payment_method_types = ['card']
        debug_log(f"📋 Payment method types: {payment_method_types}")
        
        try:
            # Valider le panier avant de créer la commande
            is_valid, errors = CartService.validate_cart_for_checkout(cart, product_type)
            if not is_valid:
                for error in errors:
                    messages.error(request, f"❌ {error}")
                return redirect('cart:cart')
            
            # Vérifier la disponibilité du stock (sans réserver)
            stock_available, stock_errors = CartService.check_stock_availability(cart, product_type)
            if not stock_available:
                for error in stock_errors:
                    messages.error(request, f"❌ {error}")
                return redirect('cart:cart')
            
            # Calcul dynamique du délai global de livraison (min/max)
            debug_log("📋 Calcul du délai de livraison...")
            min_days = None
            max_days = None
            for supplier in shipping_summary['suppliers']:
                if supplier['delivery_time'] and '-' in supplier['delivery_time']:
                    min_str, max_str = supplier['delivery_time'].replace(' jours', '').split('-')
                    min_val = int(min_str)
                    max_val = int(max_str)
                    if min_days is None or min_val < min_days:
                        min_days = min_val
                    if max_days is None or max_val > max_days:
                        max_days = max_val
            
            # Valeurs par défaut si aucun délai trouvé
            if min_days is None:
                min_days = 2
            if max_days is None:
                max_days = 6
            
            debug_log(f"📋 Delivery estimate: {min_days}-{max_days} days")
            
            # Détermination du display_name pour Stripe
            zones_count = len(shipping_summary['suppliers'])
            if zones_count > 1:
                display_name = "Livraison multi-zones"
            else:
                display_name = "Livraison"
            
            debug_log(f"📋 Display name: {display_name}")
            debug_log(f"📋 Shipping cost: {shipping_summary['summary']['shipping_cost']}")
            
            # Créer la session Stripe
            debug_log("📋 Creating Stripe checkout session...")
            checkout_session = stripe.checkout.Session.create(
                customer_email=request.user.email,
                payment_method_types=payment_method_types,
                line_items=line_items,
                mode='payment',
                success_url=domain_url + reverse('cart:payment_success') + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + reverse('cart:payment_cancel'),
                metadata={
                    'cart_id': cart.id,
                    'user_id': request.user.id,
                    'shipping_address_id': address.id,
                    'product_type': product_type,
                    'payment_method': payment_method,
                    'shipping_cost': str(shipping_summary['summary']['shipping_cost']),
                },
                shipping_options=[{
                    'shipping_rate_data': {
                        'type': 'fixed_amount',
                        'fixed_amount': {
                            'amount': int(shipping_summary['summary']['shipping_cost']),
                            'currency': 'xof',
                        },
                        'display_name': display_name,
                        'delivery_estimate': {
                            'minimum': {'unit': 'business_day', 'value': min_days},
                            'maximum': {'unit': 'business_day', 'value': max_days},
                        }
                    }
                }],
                locale='fr',
            )
            
            debug_log(f"✅ Stripe session created successfully: {checkout_session.id}")
            debug_log(f"✅ Redirect URL: {checkout_session.url}")
            
            return redirect(checkout_session.url, code=303)
            
        except Exception as e:
            debug_log(f"❌ ERROR lors de la création de la commande: {str(e)}")
            messages.error(request, f"❌ **Erreur lors de la création de la commande** : {str(e)}")
            raise
    
    # GET request
    print("\n=== Affichage du formulaire (GET) ===")
    default_address = ShippingAddress.objects.filter(user=request.user, is_default=True).first()
    # Toujours créer un formulaire vide pour "Nouvelle adresse"
    form = ShippingAddressForm()
    
    # Calculer le total de la commande avec les frais de livraison par fournisseur
    shipping_summary = get_shipping_summary_for_display(cart)
    order_total = shipping_summary['summary']['subtotal']
    shipping_cost = shipping_summary['summary']['shipping_cost']
    total_with_shipping = shipping_summary['summary']['total']
    
    print(f"Total panier: {order_total}")
    print(f"Frais de livraison: {shipping_cost}")
    print(f"Total avec livraison: {total_with_shipping}")
    print(f"Fournisseurs: {shipping_summary['summary']['suppliers_count']}")
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'order_total': order_total,
        'shipping_cost': shipping_cost,
        'total_with_shipping': total_with_shipping,
        'form': form,
        'default_address': default_address,
        'is_checkout': True,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'selected_payment_method': payment_method,
        'product_type': product_type,  # Type de produits sélectionné
        'payment_type': payment_type,  # Type de paiement sélectionné
        'shipping_summary': shipping_summary,  # Résumé des frais de livraison par fournisseur
        'is_mixed_cart': is_mixed_cart,  # Si le panier est mixte
    }
    
    print("=== Fin de payment_online ===\n")
    return render(request, 'payment_online.html', context)


def send_order_confirmation_email(order, request=None):
    """
    Envoie un email de confirmation de commande avec gestion d'erreurs détaillée
    """
    print(f"\n📧 === ENVOI EMAIL DE CONFIRMATION ===")
    print(f"Commande: {order.order_number}")
    print(f"Utilisateur: {order.user.email[:3]}***@{order.user.email.split('@')[1] if '@' in order.user.email else '***'}")
    print(f"Mode DEBUG: {settings.DEBUG}")
    print(f"EMAIL_BACKEND: {getattr(settings, 'EMAIL_BACKEND', 'Non configuré')}")
    print(f"DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Non configuré')}")
    
    # Récupérer le domain_url de manière dynamique
    if request:
        domain_url = request.build_absolute_uri('/')[:-1]
        print(f"Domain URL depuis request: {domain_url}")
    else:
        # Fallback pour les cas où request n'est pas disponible
        domain_url = "http://127.0.0.1:8000"
        print(f"Domain URL fallback: {domain_url}")
    
    subject = f'Confirmation de votre commande {order.order_number}'
    print(f"Sujet: {subject}")
    
    # Préparer le contexte pour le template
    # Précharger les relations pour optimiser les performances et s'assurer que les images sont disponibles
    from django.db.models import Prefetch
    
    order_with_items = Order.objects.select_related(
        'user', 'shipping_address', 'shipping_method'
    ).prefetch_related(
        Prefetch(
            'items',
            queryset=OrderItem.objects.select_related('product').prefetch_related(
                'colors', 'sizes'
            )
        )
    ).get(id=order.id)
    
    # Récupérer la configuration du site
    from core.models import SiteConfiguration
    try:
        site_config = SiteConfiguration.get_config()
        site_phone = site_config.phone_number
        site_email = site_config.email
        site_address = site_config.address
    except:
        site_phone = None
        site_email = None
        site_address = None
    
    context = {
        'order': order_with_items,
        'domain_url': domain_url,
        'site_phone': site_phone,
        'site_email': site_email,
        'site_address': site_address
    }
    
    try:
        html_message = render_to_string('cart/emails/order_confirmation.html', context)
        plain_message = strip_tags(html_message)
        print(f"✅ Template email rendu avec succès")
        print(f"Longueur HTML: {len(html_message)} caractères")
        print(f"Longueur texte: {len(plain_message)} caractères")
    except Exception as template_error:
        print(f"❌ Erreur lors du rendu du template: {str(template_error)}")
        return False
    
    try:
        print(f"📤 Tentative d'envoi d'email...")
        print(f"De: {settings.DEFAULT_FROM_EMAIL}")
        print(f"À: {order.user.email[:3]}***@{order.user.email.split('@')[1] if '@' in order.user.email else '***'}")
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email],
            html_message=html_message,
            fail_silently=False  # Pour voir les erreurs détaillées
        )
        print(f"✅ Email de confirmation envoyé avec succès à {order.user.email[:3]}***@{order.user.email.split('@')[1] if '@' in order.user.email else '***'}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de l'email de confirmation:")
        print(f"   Type d'erreur: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        
        # Logs spécifiques selon le type d'erreur
        if "SMTPAuthenticationError" in str(type(e)):
            print(f"   🔐 Erreur d'authentification SMTP - Vérifiez les paramètres d'authentification")
        elif "SMTPConnectError" in str(type(e)):
            print(f"   🌐 Erreur de connexion SMTP - Vérifiez EMAIL_HOST et EMAIL_PORT")
        elif "SMTPServerDisconnected" in str(type(e)):
            print(f"   🔌 Serveur SMTP déconnecté - Vérifiez la configuration")
        elif "SMTPRecipientsRefused" in str(type(e)):
            print(f"   📧 Destinataire refusé - Vérifiez l'adresse email: {order.user.email[:3]}***@{order.user.email.split('@')[1] if '@' in order.user.email else '***'}")
        
        # Ne pas lever l'exception pour éviter de bloquer le processus de commande
        # L'email peut être envoyé plus tard ou l'utilisateur peut voir la confirmation sur le site
        return False


@login_required
def payment_delivery(request):
    print("\n=== Début de payment_delivery ===")
    cart = Cart.objects.get(user=request.user)
    
    # Récupérer le type de produits et le type de paiement demandés
    product_type = request.GET.get('type', 'all')  # 'classic', 'salam', ou 'all'
    payment_type = request.GET.get('payment', 'flexible')  # 'flexible', 'immediate', ou 'all'
    
    # Détecter automatiquement si le panier est mixte
    classic_items = cart.cart_items.filter(product__is_salam=False)
    salam_items = cart.cart_items.filter(product__is_salam=True)
    is_mixed_cart = classic_items.exists() and salam_items.exists()
    
    # Vérifier que les produits Salam ne sont pas autorisés pour le paiement à la livraison
    if product_type == 'salam':
        messages.error(request, "❌ **Produits Salam non autorisés** : Les produits Salam nécessitent un paiement immédiat et ne peuvent pas être payés à la livraison. Veuillez utiliser le paiement en ligne ou Mobile Money.")
        return redirect('cart:checkout')
    
    # Filtrer les items selon le type demandé
    if product_type == 'classic':
        cart_items = cart.cart_items.filter(product__is_salam=False)
        if not cart_items.exists():
            messages.warning(request, "🛒 Aucun produit classique dans votre panier")
            return redirect('cart:cart')
    elif product_type == 'salam':
        # Ce cas ne devrait jamais arriver à cause de la vérification ci-dessus
        messages.error(request, "❌ **Erreur** : Les produits Salam nécessitent un paiement immédiat.")
        return redirect('cart:checkout')
    else:
        # Pour 'all', traiter tous les produits du panier
        cart_items = cart.cart_items.all().select_related('product')
    
    print(f"Panier trouvé pour l'utilisateur {request.user.email[:3]}***@{request.user.email.split('@')[1] if '@' in request.user.email else '***'} avec {cart_items.count()} articles")
    print(f"Type de produit: {product_type}, Panier mixte: {is_mixed_cart}")
    
    if request.method == 'POST':
        print("\n=== Traitement du formulaire (POST) ===")
        # Suppression des logs sensibles
        
        # Récupérer les données du formulaire
        address_choice = request.POST.get('address_choice')
        shipping_method_id = request.POST.get('shipping_method')
        action = request.POST.get('action')
        
        print(f"Action: {action}")
        print(f"Choix d'adresse: {address_choice}")
        print(f"Méthode de livraison: {shipping_method_id}")
        
        # Vérifier si c'est une action de création de commande
        if action != 'create_order':
            print(f"Action non reconnue: {action}")
            messages.error(request, "❌ **Erreur** : Action non reconnue")
            return redirect('cart:payment_delivery')
        
        # Valider le formulaire d'adresse
        print(f"Address choice: {address_choice}")
        if address_choice == 'new':
            print("Création du formulaire avec les données POST")
            form = ShippingAddressForm(request.POST)
            print(f"Form data: {form.data}")
        else:
            print("Création d'un formulaire vide (adresse par défaut)")
            form = ShippingAddressForm()
        
        print(f"Form is_valid: {form.is_valid()}")
        print(f"Shipping method ID: {shipping_method_id}")
        print(f"Form errors: {form.errors}")
        
        # Vérifier que les données essentielles sont présentes
        if not address_choice:
            messages.error(request, "❌ **Erreur** : Veuillez sélectionner une option d'adresse")
            return redirect('cart:payment_delivery')
        
        if not shipping_method_id:
            messages.error(request, "❌ **Erreur** : Méthode de livraison manquante")
            return redirect('cart:payment_delivery')
        
        # Valider le formulaire seulement si c'est une nouvelle adresse
        form_is_valid = True
        if address_choice == 'new':
            form_is_valid = form.is_valid()
            if not form_is_valid:
                print(f"Form errors: {form.errors}")
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"❌ **Erreur** : {error}")
                return redirect('cart:payment_delivery')
        
        if form_is_valid:
            try:
                shipping_method = ShippingMethod.objects.get(id=shipping_method_id)
            except ShippingMethod.DoesNotExist:
                messages.error(request, "❌ **Erreur** : Méthode de livraison non trouvée")
                return redirect('cart:payment_delivery')
            
            print(f"Méthode de livraison sélectionnée: {shipping_method.name} - {shipping_method.price} FCFA")
            
            # Valider le panier avant de créer la commande
            is_valid, errors = CartService.validate_cart_for_checkout(cart, product_type)
            if not is_valid:
                for error in errors:
                    messages.error(request, f"❌ {error}")
                return redirect('cart:cart')
            
            # Vérifier la disponibilité du stock (sans réserver)
            stock_available, stock_errors = CartService.check_stock_availability(cart, product_type)
            if not stock_available:
                for error in stock_errors:
                    messages.error(request, f"❌ {error}")
                return redirect('cart:cart')
            
            # Réserver le stock pour les produits classiques
            print("Réservation du stock pour les produits classiques...")
            stock_reserved, reserve_errors = CartService.reserve_stock_for_order(cart, product_type)
            if not stock_reserved:
                for error in reserve_errors:
                    messages.error(request, f"❌ {error}")
                return redirect('cart:cart')
            print("✅ Stock réservé avec succès")
            
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
            
            # Créer la commande avec gestion d'erreur et libération du stock
            try:
                print(f"\nCréation de la commande:")
                
                # Calculer le total des produits classiques seulement
                classic_total = sum(item.get_total_price() for item in cart_items)
                print(f"- Total produits classiques: {classic_total}")
                print(f"- Frais de livraison: {shipping_method.price}")
                print(f"- Total avec livraison: {classic_total + shipping_method.price}")
                
                # Message de confirmation pour le paiement à la livraison
                messages.success(request, "✅ **Commande créée** : Votre commande a été enregistrée avec succès. Vous paierez à la livraison.")
                
                # Créer la commande
                # Pour les commandes simples, ne pas ajouter de métadonnées de processus en 2 étapes
                if is_mixed_cart:
                    # Panier mixte : ajouter les métadonnées pour le processus en 2 étapes
                    metadata = {
                        'order_type': 'classic',
                        'is_classic_step': True,
                        'step_number': 1,
                        'total_steps': 2,
                        'next_step': 'salam_products'
                    }
                else:
                    # Commande simple : pas de métadonnées de processus
                    metadata = {}
                
                order = Order.objects.create(
                    user=request.user,
                    shipping_address=address,
                    shipping_method=shipping_method,
                    payment_method='cash_on_delivery',
                    subtotal=classic_total,
                    shipping_cost=shipping_method.price,
                    total=classic_total + shipping_method.price,
                    metadata=metadata
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
                        price=item.product.discount_price if hasattr(item.product, 'discount_price') and item.product.discount_price else item.product.price
                    )
                    if item.colors.exists():
                        print(f"  - Couleurs: {', '.join(c.name for c in item.colors.all())}")
                        order_item.colors.set(item.colors.all())
                    if item.sizes.exists():
                        print(f"  - Tailles: {', '.join(s.name for s in item.sizes.all())}")
                        order_item.sizes.set(item.sizes.all())
                
                print("✅ Commande et éléments créés avec succès")
                
            except Exception as e:
                # En cas d'erreur, libérer le stock réservé
                print(f"❌ Erreur lors de la création de la commande: {str(e)}")
                print("Libération du stock réservé...")
                CartService.release_stock_for_order(cart, product_type)
                print("✅ Stock libéré")
                
                messages.error(request, f"❌ **Erreur** : Impossible de créer la commande. Veuillez réessayer.")
                return redirect('cart:payment_delivery')
            
            # Supprimer seulement les produits classiques du panier
            print("\nSuppression des produits classiques du panier")
            if product_type == 'classic':
                # Supprimer seulement les produits classiques
                cart.cart_items.filter(product__is_salam=False).delete()
                print("✅ Produits classiques supprimés du panier")
                
                # Vérifier s'il reste des produits Salam
                salam_items_remaining = cart.cart_items.filter(product__is_salam=True)
                if salam_items_remaining.exists():
                    print(f"⚠️ {salam_items_remaining.count()} produits Salam restent dans le panier")
                    messages.info(request, f"📦 **Produits Salam en attente** : {salam_items_remaining.count()} produit(s) Salam restent dans votre panier. Vous pouvez les commander séparément.")
                else:
                    # Si plus aucun produit, supprimer le panier
                    cart.delete()
                    print("✅ Panier supprimé (plus aucun produit)")
            else:
                # Pour 'all', supprimer tout le panier
                cart.delete()
                print("✅ Panier supprimé (tous les produits traités)")
            
            # Envoyer l'email de confirmation
            print("Envoi de l'email de confirmation")
            try:
                send_order_confirmation_email(order, request)
                print("✅ Email de confirmation envoyé avec succès")
            except Exception as email_error:
                print(f"⚠️ Erreur lors de l'envoi de l'email: {str(email_error)}")
                # Ne pas bloquer le processus si l'email échoue
                # L'utilisateur peut voir la confirmation sur le site
            
            print("\n=== Redirection vers la confirmation ===")
            return redirect('cart:order_confirmation', order_id=order.id)
            
        else:
            print("\n=== Formulaire invalide ===")
            print(f"Erreurs du formulaire: {form.errors}")
            print(f"Méthode de livraison manquante: {not shipping_method_id}")
            print(f"Action: {action}")
            print(f"Address choice: {address_choice}")
            
            # Messages d'erreur spécifiques
            if not shipping_method_id:
                messages.error(request, "❌ **Erreur** : Veuillez sélectionner une méthode de livraison")
            if not address_choice:
                messages.error(request, "❌ **Erreur** : Veuillez sélectionner une option d'adresse")
            if form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"❌ **Erreur** : {error}")
            
            # Rediriger vers la même page pour afficher les erreurs
            return redirect('cart:payment_delivery')
    
    # GET request
    print("\n=== Affichage du formulaire (GET) ===")
    default_address = ShippingAddress.objects.filter(user=request.user, is_default=True).first()
    # Toujours créer un formulaire vide pour "Nouvelle adresse"
    form = ShippingAddressForm()
    
    # Calculer le total des produits classiques seulement
    order_total = sum(item.get_total_price() for item in cart_items)
    
    # Récupérer les méthodes de livraison compatibles avec les produits du panier
    from .payment_config import get_common_shipping_methods_for_cart
    common_methods = get_common_shipping_methods_for_cart(cart_items)
    default_shipping_method = common_methods[0] if common_methods else ShippingMethod.objects.first()
    if default_shipping_method:
        shipping_cost = default_shipping_method.price
    else:
        shipping_cost = 1000  # Valeur par défaut si aucune méthode n'existe
    
    total_with_shipping = order_total + shipping_cost
    
    print(f"Total produits classiques: {order_total}")
    print(f"Frais de livraison: {shipping_cost}")
    print(f"Total avec livraison: {total_with_shipping}")
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'order_total': order_total,
        'shipping_cost': shipping_cost,
        'total_with_shipping': total_with_shipping,
        'shipping_methods': get_common_shipping_methods_for_cart(cart_items),
        'default_shipping_method': default_shipping_method,
        'form': form,
        'default_address': default_address,
        'is_checkout': True,
        'product_type': product_type,  # Type de produits sélectionné
        'payment_type': payment_type,  # Type de paiement sélectionné
        'is_mixed_cart': is_mixed_cart,  # Si le panier est mixte
    }
    
    print("=== Fin de payment_delivery ===\n")
    return render(request, 'payment_delivery.html', context)



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
        
        # Vérification de sécurité : s'assurer que l'item appartient au panier de l'utilisateur
        try:
            cart_item = CartItem.objects.get(id=cartitem_id, cart=cart)
        except CartItem.DoesNotExist:
            return JsonResponse({'error': 'Article non trouvé'}, status=404)
        
        # Log de sécurité pour tracer les suppressions
        if hasattr(request, 'user') and request.user.is_authenticated:
            print(f"🔒 Suppression d'article {cartitem_id} par l'utilisateur {request.user.email[:3]}***")
        
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
    
    # Debug: afficher les métadonnées pour vérification
    print(f"Commande {order.id}: metadata = {order.metadata}")
    print(f"is_salam_step = {order.metadata.get('is_salam_step', False)}")
    
    # Tracking de l'achat
    track_purchase(
        request=request,
        order_id=str(order.id),
        total_amount=str(order.total),
        currency='XOF',
        items_count=order.items.count()
    )
    
    # Préparer le contexte pour le template
    # Précharger les relations pour optimiser les performances
    order_with_items = Order.objects.select_related(
        'user', 'shipping_address', 'shipping_method'
    ).prefetch_related(
        'items__product__images',  # Précharger les images des produits
        'items__colors',
        'items__sizes'
    ).get(id=order.id)
    
    # Récupérer le domain_url de manière dynamique
    domain_url = request.build_absolute_uri('/')[:-1]
    
    context = {
        'order': order_with_items,
        'domain_url': domain_url
    }
    return render(request, 'cart/order_confirmation.html', context)


@login_required
def my_orders(request):
    # Récupérer toutes les commandes de l'utilisateur, triées par date de création (la plus récente en premier)
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # Debug: afficher les métadonnées pour vérification
    for order in orders:
        print(f"Commande {order.id}: metadata = {order.metadata}")
    
    context = {
        'orders': orders,
    }
    return render(request, 'cart/my_orders.html', context)


@csrf_exempt
def stripe_webhook(request):
    debug_log("\n" + "="*80)
    debug_log("🔄 DÉBUT DU WEBHOOK STRIPE")
    debug_log("="*80)
    
    # Vérifier la méthode HTTP
    if request.method != 'POST':
        debug_log("❌ Méthode HTTP non autorisée")
        return HttpResponse('Method not allowed', status=405)
    
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    
    # Vérifier que le secret webhook est configuré
    if not webhook_secret:
        debug_log("❌ Webhook secret non configuré")
        return HttpResponse('Webhook secret not configured', status=500)
    
    debug_log(f"📋 Webhook secret configuré: {bool(webhook_secret)}")
    debug_log(f"📋 Payload length: {len(payload)}")
    debug_log(f"📋 Signature header: {bool(sig_header)}")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=webhook_secret
        )
        data = event['data']
        event_type = event['type']
        debug_log(f"✅ Event type: {event_type}")
    except ValueError as e:
        debug_log(f"❌ Erreur payload invalide: {str(e)}")
        return HttpResponse('Invalid payload', status=400)
    except stripe.error.SignatureVerificationError as e:
        debug_log(f"❌ Erreur signature invalide: {str(e)}")
        return HttpResponse('Invalid signature', status=400)
    except Exception as e:
        debug_log(f"❌ Erreur construction webhook: {str(e)}")
        return HttpResponse(str(e), status=400)

    data_object = data['object']
    debug_log(f"📋 Data object type: {type(data_object)}")

    if event_type == 'checkout.session.completed':
        debug_log("🔄 Traitement checkout.session.completed")
        session = data_object
        
        try:
            debug_log(f"📋 Session ID: {session.id}")
            debug_log(f"📋 Metadata: {session.metadata}")
            
            # Vérifier si cette session a déjà été traitée
            existing_order = Order.objects.filter(stripe_session_id=session.id).first()
            if existing_order:
                debug_log(f"⚠️ Session déjà traitée - Commande existante: {existing_order.id}")
                return JsonResponse({'status': 'success', 'message': 'Session already processed'})
            
            # Créer la commande
            cart_id = session.metadata.get('cart_id')
            debug_log(f"📋 Cart ID: {cart_id}")
            
            cart = Cart.objects.get(id=cart_id)
            debug_log(f"✅ Cart trouvé: {cart.id}")
            
            # Récupérer la méthode de livraison compatible avec les produits classiques
            from .payment_config import get_common_shipping_methods_for_cart
            classic_cart_items = cart.cart_items.filter(product__is_salam=False)
            common_methods = get_common_shipping_methods_for_cart(classic_cart_items)
            shipping_method = common_methods[0] if common_methods else ShippingMethod.objects.first()
            debug_log(f"📋 Shipping method: {shipping_method.id if shipping_method else None}")
            
            # Récupérer le type de produits depuis les métadonnées
            product_type = session.metadata.get('product_type', 'all')
            debug_log(f"📋 Product type: {product_type}")
            
            # Récupérer l'adresse de livraison
            shipping_address_id = session.metadata.get('shipping_address_id')
            debug_log(f"📋 Shipping address ID: {shipping_address_id}")
            
            shipping_address = ShippingAddress.objects.get(id=shipping_address_id)
            debug_log(f"✅ Shipping address trouvée: {shipping_address.id}")
            
            # Récupérer les frais de livraison
            shipping_cost = Decimal(str(session.metadata.get('shipping_cost', 0)))
            debug_log(f"📋 Shipping cost: {shipping_cost}")
            
            # Calculer le total selon le type de produits
            if product_type == 'salam':
                debug_log("🔄 Création commande Salam")
                subtotal = sum(item.get_total_price() for item in cart.cart_items.filter(product__is_salam=True))
                debug_log(f"📋 Subtotal Salam: {subtotal}")
                
                # Créer la commande Salam avec toutes les métadonnées pour le processus en 2 étapes
                order = Order.objects.create(
                    user=cart.user,
                    shipping_address=shipping_address,
                    stripe_session_id=session.id,
                    stripe_payment_status='paid',
                    payment_method='online_payment',
                    is_paid=True,
                    shipping_method=shipping_method,
                    subtotal=subtotal,
                    shipping_cost=shipping_cost,
                    total=subtotal + shipping_cost,
                    metadata={
                        'order_type': 'salam',
                        'is_salam_step': True,
                        'step_number': 2,
                        'total_steps': 2,
                        'next_step': 'completed'
                    }
                )
                debug_log(f"✅ Commande Salam créée: {order.id}")
            elif product_type == 'classic':
                subtotal = sum(item.get_total_price() for item in cart.cart_items.filter(product__is_salam=False))
                # Créer la commande classique avec métadonnées pour le processus en 2 étapes
                order = Order.objects.create(
                    user=cart.user,
                    shipping_address=shipping_address,
                    stripe_session_id=session.id,
                    stripe_payment_status='paid',
                    payment_method='online_payment',
                    is_paid=True,
                    shipping_method=shipping_method,
                    subtotal=subtotal,
                    shipping_cost=shipping_cost,
                    total=subtotal + shipping_cost,
                    metadata={
                        'order_type': 'classic',
                        'is_classic_step': True,
                        'step_number': 1,
                        'total_steps': 2,
                        'next_step': 'salam_products'
                    }
                )
                debug_log(f"✅ Commande classique créée: {order.id}")
            else:
                # Créer la commande normale
                order = Order.objects.create(
                    user=cart.user,
                    shipping_address=shipping_address,
                    stripe_session_id=session.id,
                    stripe_payment_status='paid',
                    payment_method='online_payment',
                    is_paid=True,
                    shipping_method=shipping_method,
                    subtotal=cart.get_total_price(),
                    shipping_cost=shipping_cost,
                    total=cart.get_total_price() + shipping_cost
                )
                debug_log(f"✅ Commande normale créée: {order.id}")

            # Créer les éléments de la commande
            if product_type == 'salam':
                # Ne traiter que les produits Salam
                for item in cart.cart_items.filter(product__is_salam=True):
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.discount_price if hasattr(item.product, 'discount_price') and item.product.discount_price else item.product.price
                    )
                    if item.colors.exists():
                        order_item.colors.set(item.colors.all())
                    if item.sizes.exists():
                        order_item.sizes.set(item.sizes.all())
                
                # Supprimer seulement les produits Salam du panier
                cart.cart_items.filter(product__is_salam=True).delete()
                
                # Message de succès pour Salam
                messages.success(request, "✅ **Paiement Salam réussi** : Vos produits Salam ont été payés et votre commande est en cours de traitement.")
            elif product_type == 'classic':
                # Ne traiter que les produits classiques
                for item in cart.cart_items.filter(product__is_salam=False):
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.discount_price if hasattr(item.product, 'discount_price') and item.product.discount_price else item.product.price
                    )
                    if item.colors.exists():
                        order_item.colors.set(item.colors.all())
                    if item.sizes.exists():
                        order_item.sizes.set(item.sizes.all())
                
                # Supprimer seulement les produits classiques du panier
                cart.cart_items.filter(product__is_salam=False).delete()
                
                # Message de succès pour classique
                messages.success(request, "✅ **Commande classique réussie** : Vos produits classiques ont été commandés. Vous pouvez maintenant commander vos produits Salam.")
            else:
                # Traiter tous les produits
                for item in cart.cart_items.all():
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.discount_price if hasattr(item.product, 'discount_price') and item.product.discount_price else item.product.price
                    )
                    if item.colors.exists():
                        order_item.colors.set(item.colors.all())
                    if item.sizes.exists():
                        order_item.sizes.set(item.sizes.all())

            # Vider le panier seulement si tous les produits ont été traités
            if product_type == 'all':
                cart.delete()

            # Envoyer l'email de confirmation
            try:
                send_order_confirmation_email(order, None)  # Pas de request dans le webhook
                debug_log("✅ Email de confirmation envoyé")
            except Exception as email_error:
                debug_log(f"⚠️ Erreur envoi email: {str(email_error)}")

            debug_log("✅ Webhook traité avec succès")
            return JsonResponse({'status': 'success'})

        except Cart.DoesNotExist:
            debug_log("❌ Panier non trouvé - probablement déjà traité")
            return JsonResponse({'status': 'success', 'message': 'Cart already processed'})
        except Exception as e:
            debug_log(f"❌ Erreur lors du traitement du paiement: {str(e)}")
            debug_log(f"❌ Error type: {type(e)}")
            import traceback
            debug_log(f"❌ Traceback: {traceback.format_exc()}")
            return JsonResponse({'error': str(e)}, status=500)

    debug_log(f"📋 Event type non géré: {event_type}")
    return JsonResponse({'status': 'success'})


@login_required
def payment_success(request):
    """Vue de succès de paiement avec tracking Facebook"""
    session_id = request.GET.get('session_id')
    if session_id:
        try:
            # Vérifier la session Stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            session = stripe.checkout.Session.retrieve(session_id)
            
            # Vérifier si une commande existe déjà pour cette session
            existing_order = Order.objects.filter(stripe_session_id=session.id).first()
            if existing_order:
                # La commande a déjà été traitée par le webhook
                messages.success(request, "✅ **Paiement confirmé** : Votre commande a été traitée avec succès.")
                return redirect('cart:order_confirmation', order_id=existing_order.id)
            
            # Si pas de commande existante, essayer de traiter (fallback)
            try:
                cart = Cart.objects.get(id=session.metadata.cart_id)
            except Cart.DoesNotExist:
                messages.warning(request, "⚠️ **Commande déjà traitée** : Votre commande a été traitée automatiquement.")
                return redirect('cart:my_orders')
            
            # Récupérer les frais de livraison depuis les métadonnées
            shipping_cost = Decimal(str(session.metadata.get('shipping_cost', 0)))
            
            # Récupérer l'adresse de livraison depuis les métadonnées
            shipping_address_id = session.metadata.get('shipping_address_id')
            if not shipping_address_id:
                raise ValueError("Aucune adresse de livraison trouvée dans les métadonnées")
            
            try:
                shipping_address = ShippingAddress.objects.get(id=shipping_address_id, user=request.user)
                debug_log(f"✅ Adresse de livraison trouvée: {shipping_address.id}")
            except ShippingAddress.DoesNotExist:
                raise ValueError(f"Adresse de livraison {shipping_address_id} introuvable")
            
            # Récupérer le type de produits depuis les métadonnées
            product_type = session.metadata.get('product_type', 'all')
            
            # Récupérer la méthode de livraison compatible avec les produits Salam
            from .payment_config import get_common_shipping_methods_for_cart
            salam_cart_items = cart.cart_items.filter(product__is_salam=True)
            common_methods = get_common_shipping_methods_for_cart(salam_cart_items)
            shipping_method = common_methods[0] if common_methods else ShippingMethod.objects.first()
            
            # Calculer le total selon le type de produits
            if product_type == 'salam':
                subtotal = sum(item.get_total_price() for item in cart.cart_items.filter(product__is_salam=True))
                # Créer la commande Salam avec toutes les métadonnées pour le processus en 2 étapes
                order = Order.objects.create(
                    user=request.user,
                    shipping_address=shipping_address,
                    stripe_session_id=session_id,
                    stripe_payment_status='paid',
                    payment_method='online_payment',
                    is_paid=True,
                    shipping_method=shipping_method,
                    subtotal=subtotal,
                    shipping_cost=shipping_cost,
                    total=subtotal + shipping_cost,
                    metadata={
                        'order_type': 'salam',
                        'is_salam_step': True,
                        'step_number': 2,
                        'total_steps': 2,
                        'next_step': 'completed'
                    }
                )
                debug_log(f"✅ Commande Salam créée: {order.id}")
            elif product_type == 'classic':
                subtotal = sum(item.get_total_price() for item in cart.cart_items.filter(product__is_salam=False))
                # Créer la commande classique avec métadonnées pour le processus en 2 étapes
                order = Order.objects.create(
                    user=request.user,
                    shipping_address=shipping_address,
                    stripe_session_id=session_id,
                    stripe_payment_status='paid',
                    payment_method='online_payment',
                    is_paid=True,
                    shipping_method=shipping_method,
                    subtotal=subtotal,
                    shipping_cost=shipping_cost,
                    total=subtotal + shipping_cost,
                    metadata={
                        'order_type': 'classic',
                        'is_classic_step': True,
                        'step_number': 1,
                        'total_steps': 2,
                        'next_step': 'salam_products'
                    }
                )
                debug_log(f"✅ Commande classique créée: {order.id}")
            else:
                # Créer la commande normale
                order = Order.objects.create(
                    user=request.user,
                    shipping_address=shipping_address,
                    stripe_session_id=session_id,
                    stripe_payment_status='paid',
                    payment_method='online_payment',
                    is_paid=True,
                    shipping_method=shipping_method,
                    subtotal=cart.get_total_price(),
                    shipping_cost=shipping_cost,
                    total=cart.get_total_price() + shipping_cost
                )
                debug_log(f"✅ Commande normale créée: {order.id}")

            # Créer les éléments de la commande
            if product_type == 'salam':
                # Ne traiter que les produits Salam
                for item in cart.cart_items.filter(product__is_salam=True):
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.discount_price if hasattr(item.product, 'discount_price') and item.product.discount_price else item.product.price
                    )
                    if item.colors.exists():
                        order_item.colors.set(item.colors.all())
                    if item.sizes.exists():
                        order_item.sizes.set(item.sizes.all())
                
                # Supprimer seulement les produits Salam du panier
                cart.cart_items.filter(product__is_salam=True).delete()
                
                # Message de succès pour Salam
                messages.success(request, "✅ **Paiement Salam réussi** : Vos produits Salam ont été payés et votre commande est en cours de traitement.")
            elif product_type == 'classic':
                # Ne traiter que les produits classiques
                for item in cart.cart_items.filter(product__is_salam=False):
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.discount_price if hasattr(item.product, 'discount_price') and item.product.discount_price else item.product.price
                    )
                    if item.colors.exists():
                        order_item.colors.set(item.colors.all())
                    if item.sizes.exists():
                        order_item.sizes.set(item.sizes.all())
                
                # Supprimer seulement les produits classiques du panier
                cart.cart_items.filter(product__is_salam=False).delete()
                
                # Message de succès pour classique
                messages.success(request, "✅ **Commande classique réussie** : Vos produits classiques ont été commandés. Vous pouvez maintenant commander vos produits Salam.")
            else:
                # Traiter tous les produits
                for item in cart.cart_items.all():
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.discount_price if hasattr(item.product, 'discount_price') and item.product.discount_price else item.product.price
                    )
                    if item.colors.exists():
                        order_item.colors.set(item.colors.all())
                    if item.sizes.exists():
                        order_item.sizes.set(item.sizes.all())

            # Vider le panier seulement si tous les produits ont été traités
            if product_type == 'all':
                cart.delete()

            # Envoyer l'email de confirmation
            send_order_confirmation_email(order, request)

            # Envoyer l'événement de conversion à Facebook
            if request.user.is_authenticated:
                user_data = {
                    "email": request.user.email,
                    "phone": getattr(request.user, 'phone', '')
                }
                
                # Calculer le montant total de la commande
                cart_total = request.session.get('cart_total', 0)
                
                facebook_conversions.send_purchase_event(
                    user_data=user_data,
                    amount=cart_total,
                    currency="XOF",
                    content_name="Service Salam BoliBana"
                )

            return redirect('cart:order_confirmation', order_id=order.id)

        except Exception as e:
            print(f"Erreur lors du traitement du paiement: {str(e)}")
            messages.error(request, "Une erreur est survenue lors du traitement de votre paiement.")
            return redirect('cart:my_orders')

    return redirect('cart:my_orders')


@login_required
def payment_cancel(request):
    messages.warning(request, "❌ **Paiement annulé** : Votre paiement a été annulé. Vous pouvez réessayer quand vous le souhaitez.")
    return render(request, 'payment_cancel.html')


@login_required
def create_checkout_session(request):
    """
    Crée une session Stripe pour tous les types de paniers (classique, salam, mixte)
    """
    import stripe
    from django.urls import reverse
    
    debug_log("\n" + "="*80)
    debug_log("🚀 DÉBUT DE CREATE_CHECKOUT_SESSION UNIFIÉE")
    debug_log("="*80)
    
    debug_log(f"📋 Method: {request.method}")
    # Suppression des logs sensibles
    
    # Vérifier la configuration Stripe
    debug_log(f"🔑 STRIPE_SECRET_KEY configurée: {bool(settings.STRIPE_SECRET_KEY)}")
    debug_log(f"🔑 STRIPE_PUBLIC_KEY configurée: {bool(settings.STRIPE_PUBLIC_KEY)}")
    
    if not settings.STRIPE_SECRET_KEY:
        debug_log("❌ ERROR: STRIPE_SECRET_KEY non configurée!")
        messages.error(request, "❌ **Erreur de configuration** : Clé Stripe manquante")
        return redirect('cart:checkout')
    
    try:
        # Récupérer le panier de l'utilisateur
        cart = Cart.get_or_create_cart(request)
        debug_log(f"📋 Cart ID: {cart.id}")
        debug_log(f"📋 Cart items count: {cart.cart_items.count()}")
        
        # Vérifier que le panier n'est pas vide
        if cart.cart_items.count() == 0:
            debug_log("❌ ERROR: Cart is empty!")
            messages.error(request, "❌ **Erreur** : Votre panier est vide")
            return redirect('cart:cart')
        
        # Détecter le type de panier
        salam_items = cart.cart_items.filter(product__is_salam=True)
        classic_items = cart.cart_items.filter(product__is_salam=False)
        
        is_mixed = salam_items.exists() and classic_items.exists()
        
        debug_log(f"📋 Panier Salam: {salam_items.count()} items")
        debug_log(f"📋 Panier Classique: {classic_items.count()} items")
        debug_log(f"📋 Panier Mixte: {is_mixed}")
        
        # Récupérer les données du formulaire
        payment_method = request.POST.get('payment_method', 'online_payment')
        product_type = request.POST.get('product_type', 'all')
        address_choice = request.POST.get('address_choice', 'default')
        
        debug_log(f"📋 Payment method: {payment_method}")
        debug_log(f"📋 Product type: {product_type}")
        debug_log(f"📋 Address choice: {address_choice}")
        
        # Gérer l'adresse de livraison
        address = None
        if address_choice == 'default':
            address_id = request.POST.get('shipping_address_id')
            debug_log(f"📋 Address ID from form: {address_id}")
            
            if address_id:
                try:
                    address = ShippingAddress.objects.get(id=address_id, user=request.user)
                    debug_log(f"✅ Found default address: {address.id}")
                except ShippingAddress.DoesNotExist:
                    debug_log(f"❌ ERROR: Address {address_id} not found!")
                    messages.error(request, "❌ **Erreur** : Adresse par défaut introuvable")
                    return redirect('cart:payment_online')
            else:
                # Si pas d'ID fourni, essayer de récupérer l'adresse par défaut
                address = ShippingAddress.objects.filter(user=request.user, is_default=True).first()
                debug_log(f"📋 Found default address from DB: {address.id if address else None}")
                
                if not address:
                    debug_log("❌ ERROR: No default address found!")
                    messages.error(request, "❌ **Erreur** : Aucune adresse par défaut trouvée")
                    return redirect('cart:payment_online')
        else:
            # Pour "new", vérifier si des données d'adresse sont fournies
            debug_log("📋 New address option selected")
            
            # Vérifier si des données d'adresse sont présentes dans le formulaire
            full_name = request.POST.get('full_name')
            street_address = request.POST.get('street_address')
            quarter = request.POST.get('quarter')
            
            if full_name and street_address and quarter:
                # Créer une nouvelle adresse à partir des données du formulaire
                debug_log("📋 Creating new address from form data...")
                try:
                    form = ShippingAddressForm(request.POST)
                    if form.is_valid():
                        address = form.save(commit=False)
                        address.user = request.user
                        address.save()
                        debug_log(f"✅ Created new address: {address.id}")
                        
                        # Définir comme adresse par défaut si demandé
                        if request.POST.get('is_default'):
                            debug_log("📋 Setting as default address")
                            ShippingAddress.objects.filter(user=request.user).update(is_default=False)
                            address.is_default = True
                            address.save()
                            debug_log("✅ Set as default address")
                    else:
                        debug_log(f"❌ Form errors: {form.errors}")
                        for field, errors in form.errors.items():
                            for error in errors:
                                messages.error(request, f"❌ **Erreur** : {error}")
                        return redirect('cart:payment_online')
                except Exception as e:
                    debug_log(f"❌ ERROR creating address: {str(e)}")
                    messages.error(request, f"❌ **Erreur** : Impossible de créer l'adresse - {str(e)}")
                    return redirect('cart:payment_online')
            else:
                # Aucune donnée d'adresse fournie, rediriger vers la gestion des adresses
                debug_log("❌ No address data provided in form")
                messages.error(request, "❌ **Erreur** : Pour le paiement en ligne, vous devez d'abord créer une adresse de livraison")
                return redirect('accounts:addresses')
        
        if not address:
            debug_log("❌ ERROR: No address found!")
            messages.error(request, "❌ **Erreur** : Aucune adresse de livraison valide")
            return redirect('cart:payment_online')
        
        debug_log(f"✅ Final address: {address.id} - {address.full_name}")
        
        # Configuration Stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Préparer les items selon le type de panier
        line_items = []
        
        # Validation des montants pour sécurité
        total_amount = 0
        max_amount = 1000000  # 1 million FCFA maximum par commande
        
        if is_mixed:
            # Panier mixte - utiliser la logique existante de create_mixed_checkout_session
            debug_log("🔄 Traitement panier mixte")
            
            # Récupérer les données des commandes mixtes depuis le formulaire
            salam_order_id = request.POST.get('salam_order_id')
            classic_order_id = request.POST.get('classic_order_id')
            shipping_method_id = request.POST.get('shipping_method_id')
            
            if salam_order_id and classic_order_id and shipping_method_id:
                salam_order = Order.objects.get(id=salam_order_id, user=request.user)
                classic_order = Order.objects.get(id=classic_order_id, user=request.user)
                shipping_method = ShippingMethod.objects.get(id=shipping_method_id)
                
                # Ajouter les produits Salam
                for item in salam_order.items.all():
                    # Utiliser le prix promotionnel si disponible, sinon le prix normal
                    unit_price = item.product.discount_price if hasattr(item.product, 'discount_price') and item.product.discount_price else item.product.price
                    item_amount = int(unit_price * 100)
                    total_amount += item_amount
                    
                    if total_amount > max_amount:
                        messages.error(request, "❌ **Erreur** : Montant de commande trop élevé")
                        return redirect('cart:checkout')
                    
                    line_items.append({
                        'price_data': {
                            'currency': 'xof',
                            'product_data': {
                                'name': f"{item.product.title} (Salam)",
                            },
                            'unit_amount': item_amount,
                        },
                        'quantity': item.quantity,
                    })
                
                # Ajouter les produits classiques
                for item in classic_order.items.all():
                    # Utiliser le prix promotionnel si disponible, sinon le prix normal
                    unit_price = item.product.discount_price if hasattr(item.product, 'discount_price') and item.product.discount_price else item.product.price
                    item_amount = int(unit_price * 100)
                    total_amount += item_amount
                    
                    if total_amount > max_amount:
                        messages.error(request, "❌ **Erreur** : Montant de commande trop élevé")
                        return redirect('cart:checkout')
                    
                    line_items.append({
                        'price_data': {
                            'currency': 'xof',
                            'product_data': {
                                'name': f"{item.product.title} (Classique)",
                            },
                            'unit_amount': item_amount,
                        },
                        'quantity': item.quantity,
                    })
                
                shipping_cost = shipping_method.price
                display_name = "Livraison multi-zones" if shipping_method.suppliers.count() > 1 else "Livraison"
                
            else:
                debug_log("❌ ERROR: Missing mixed order data")
                messages.error(request, "❌ **Erreur** : Données de commande mixte manquantes")
                return redirect('cart:checkout')
                
        else:
            # Panier simple - utiliser la logique existante
            debug_log(f"🔄 Traitement panier simple: {product_type}")
            
            # Filtrer les produits selon le type demandé pour le calcul des frais de livraison
            if product_type == 'salam':
                # Pour les produits Salam, créer un panier temporaire avec seulement les produits Salam
                temp_cart_items = cart.cart_items.filter(product__is_salam=True)
                debug_log(f"📋 Calcul frais de livraison sur {temp_cart_items.count()} produits Salam")
                
                # Créer un panier temporaire pour le calcul des frais
                temp_cart = type('TempCart', (), {
                    'cart_items': type('TempCartItems', (), {
                        'all': lambda: temp_cart_items
                    })()
                })()
                
                # Calculer le résumé des frais de livraison sur les produits Salam seulement
                try:
                    shipping_summary = get_shipping_summary_for_display(temp_cart)
                    debug_log(f"📋 Shipping summary (Salam only): {shipping_summary['summary']}")
                except Exception as e:
                    debug_log(f"❌ ERROR calculating shipping summary: {str(e)}")
                    messages.error(request, f"❌ **Erreur** : Impossible de calculer les frais de livraison - {str(e)}")
                    return redirect('cart:payment_online')
            else:
                # Pour tous les autres cas, calculer sur tous les produits
                try:
                    shipping_summary = get_shipping_summary_for_display(cart)
                    debug_log(f"📋 Shipping summary (all products): {shipping_summary['summary']}")
                except Exception as e:
                    debug_log(f"❌ ERROR calculating shipping summary: {str(e)}")
                    messages.error(request, f"❌ **Erreur** : Impossible de calculer les frais de livraison - {str(e)}")
                    return redirect('cart:payment_online')
            
            # Toujours envoyer tous les produits à Stripe pour l'affichage
            for item in cart.cart_items.all():
                # Utiliser le prix promotionnel si disponible, sinon le prix normal
                unit_price = item.product.discount_price if hasattr(item.product, 'discount_price') and item.product.discount_price else item.product.price
                line_item = {
                    'price_data': {
                        'currency': 'xof',
                        'product_data': {
                            'name': item.product.title,
                        },
                        'unit_amount': int(unit_price),  # CFA n'a pas de centimes
                    },
                    'quantity': item.quantity,
                }
                line_items.append(line_item)
                debug_log(f"📋 Added line item: {item.product.title} x{item.quantity} = {unit_price} FCFA")
            
            shipping_cost = shipping_summary['summary']['shipping_cost']
            display_name = "Livraison multi-zones" if len(shipping_summary['suppliers']) > 1 else "Livraison"
        
        debug_log(f"📋 Total line items: {len(line_items)}")
        
        # Construire l'URL de domaine
        domain_url = request.build_absolute_uri('/')[:-1]
        
        # Configurer les méthodes de paiement
        if payment_method == 'mobile_money':
            payment_method_types = ['card', 'mobile_money']
        else:
            payment_method_types = ['card']
        
        # Calculer les délais de livraison
        min_days = 1
        max_days = 6
        
        # Créer la session Stripe
        debug_log("📋 Creating Stripe checkout session...")
        checkout_session = stripe.checkout.Session.create(
            customer_email=request.user.email,
            payment_method_types=payment_method_types,
            line_items=line_items,
            mode='payment',
            success_url=domain_url + reverse('cart:payment_success') + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=domain_url + reverse('cart:payment_cancel'),
            metadata={
                'cart_id': cart.id,
                'user_id': request.user.id,
                'shipping_address_id': address.id,
                'product_type': product_type,
                'payment_method': payment_method,
                'shipping_cost': str(shipping_cost),
                'default_country': 'ML',
                'default_country_name': 'Mali',
            },
            shipping_options=[{
                'shipping_rate_data': {
                    'type': 'fixed_amount',
                    'fixed_amount': {
                        'amount': int(shipping_cost),  # CFA n'a pas de centimes
                        'currency': 'xof',
                    },
                    'display_name': display_name,
                    'delivery_estimate': {
                        'minimum': {'unit': 'business_day', 'value': min_days},
                        'maximum': {'unit': 'business_day', 'value': max_days},
                    }
                }
            }],
            locale='fr',
            # Configuration du pays par défaut pour Stripe
            payment_intent_data={
                'metadata': {
                    'default_country': 'ML',
                    'default_country_name': 'Mali'
                }
            },
            # Collecte de l'adresse de facturation avec pays par défaut
            billing_address_collection='required',
        )
        
        debug_log(f"✅ Stripe session created successfully: {checkout_session.id}")
        debug_log(f"✅ Redirect URL: {checkout_session.url}")
        
        return redirect(checkout_session.url, code=303)
        
    except Exception as e:
        debug_log(f"❌ ERROR in create_checkout_session: {str(e)}")
        messages.error(request, f"❌ **Erreur lors de la création de la session de paiement** : {str(e)}")
        return redirect('cart:payment_online')


def debug_log(message):
    """
    Fonction pour écrire les logs de debug dans un fichier
    """
    log_file = os.path.join(os.path.dirname(__file__), 'debug_payment.log')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {message}\n")
    
    # Aussi afficher dans la console
    print(message)


@login_required
def test_email_configuration(request):
    """
    Vue de test pour vérifier la configuration email
    Accessible uniquement aux administrateurs
    """
    if not request.user.is_staff:
        messages.error(request, "❌ Accès refusé. Cette fonction est réservée aux administrateurs.")
        return redirect('suppliers:supplier_index')
    
    if request.method == 'POST':
        test_email = request.POST.get('test_email', '').strip()
        
        if not test_email:
            messages.error(request, "❌ Veuillez fournir une adresse email de test")
            return redirect('cart:test_email')
        
        try:
            # Préparer le contexte pour le template
            from django.utils import timezone
            context = {
                'backend': getattr(settings, 'EMAIL_BACKEND', 'Non configuré'),
                'host': getattr(settings, 'EMAIL_HOST', 'Non configuré'),
                'port': getattr(settings, 'EMAIL_PORT', 'Non configuré'),
                'tls': getattr(settings, 'EMAIL_USE_TLS', 'Non configuré'),
                'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'Non configuré'),
                'test_date': timezone.now().strftime("%d/%m/%Y à %H:%M")
            }
            
            # Rendre le template HTML
            html_message = render_to_string('cart/emails/test_email.html', context)
            plain_message = strip_tags(html_message)
            
            # Envoyer l'email de test
            subject = "🧪 Test de configuration email - SagaKore"
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [test_email],
                html_message=html_message,
                fail_silently=False
            )
            
            messages.success(request, f"✅ Email de test envoyé avec succès à {test_email}")
            messages.info(request, "📧 Vérifiez votre boîte de réception (et les spams)")
            
        except Exception as e:
            error_msg = f"❌ Erreur lors de l'envoi de l'email de test: {str(e)}"
            messages.error(request, error_msg)
            print(f"Erreur email test: {str(e)}")
    
    # Afficher la configuration actuelle
    email_config = {
        'debug': settings.DEBUG,
        'backend': getattr(settings, 'EMAIL_BACKEND', 'Non configuré'),
        'host': getattr(settings, 'EMAIL_HOST', 'Non configuré'),
        'port': getattr(settings, 'EMAIL_PORT', 'Non configuré'),
        'tls': getattr(settings, 'EMAIL_USE_TLS', 'Non configuré'),
        'host_user': getattr(settings, 'EMAIL_HOST_USER', 'Non configuré'),
        'host_password': 'Configuré' if getattr(settings, 'EMAIL_HOST_PASSWORD', None) else 'Non configuré',
        'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'Non configuré'),
    }
    
    return render(request, 'cart/test_email_config.html', {
        'email_config': email_config
    })


# =============================================================================
# VUES ORANGE MONEY
# =============================================================================

@login_required
def orange_money_payment(request):
    """
    Vue pour initier un paiement Orange Money
    """
    # Debug: Log détaillé de la configuration Orange Money
    logger = logging.getLogger(__name__)
    logger.info("DEBUG Orange Money Payment - Debut de la verification")
    
    # Vérifier la configuration directement
    from django.conf import settings
    config = settings.ORANGE_MONEY_CONFIG
    logger.info(f"Configuration Django: enabled={config.get('enabled')}, merchant_key={'OK' if config.get('merchant_key') else 'MANQUANT'}, client_id={'OK' if config.get('client_id') else 'MANQUANT'}, client_secret={'OK' if config.get('client_secret') else 'MANQUANT'}")
    
    # Forcer le rechargement de la configuration avant le test
    orange_money_service.refresh_config()
    
    # Test de is_enabled avec logs détaillés
    is_enabled_result = orange_money_service.is_enabled()
    logger.info(f"orange_money_service.is_enabled(): {is_enabled_result}")
    
    if not is_enabled_result:
        logger.error("Orange Money desactive - Details de la configuration:")
        logger.error(f"  - config['enabled']: {config.get('enabled')}")
        logger.error(f"  - config['merchant_key']: {bool(config.get('merchant_key'))}")
        logger.error(f"  - config['client_id']: {bool(config.get('client_id'))}")
        logger.error(f"  - config['client_secret']: {bool(config.get('client_secret'))}")
        
        messages.error(request, "❌ Le paiement Orange Money n'est pas disponible actuellement.")
        return redirect('cart:cart')
    
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        messages.warning(request, "🛒 Votre panier est vide.")
        return redirect('cart:cart')
    
    # Récupérer les paramètres de la requête
    product_type = request.GET.get('type', 'all')
    payment_type = request.GET.get('payment', 'flexible')
    
    # Filtrer les items selon le type demandé
    if product_type == 'salam':
        cart_items = cart.cart_items.filter(product__is_salam=True)
    elif product_type == 'classic':
        cart_items = cart.cart_items.filter(product__is_salam=False)
    else:
        cart_items = cart.cart_items.all().select_related('product')
    
    if not cart_items.exists():
        messages.warning(request, "🛒 Aucun article dans votre panier pour ce type de paiement.")
        return redirect('cart:cart')
    
    # Valider le panier
    is_valid, errors = CartService.validate_cart_for_checkout(cart, product_type)
    if not is_valid:
        for error in errors:
            messages.error(request, f"❌ {error}")
        return redirect('cart:cart')
    
    # Vérifier la disponibilité du stock
    stock_available, stock_errors = CartService.check_stock_availability(cart, product_type)
    if not stock_available:
        for error in stock_errors:
            messages.error(request, f"❌ {error}")
        return redirect('cart:cart')
    
    try:
        logger.info("DEBUG Orange Money Payment - Debut de l'initialisation")
        
        # Calculer le total
        logger.info("DEBUG Orange Money Payment - Calcul du total")
        total_amount = sum(item.get_total_price() for item in cart_items)
        logger.info(f"DEBUG Orange Money Payment - Total calcule: {total_amount}")
        
        # Créer une commande temporaire
        logger.info("DEBUG Orange Money Payment - Creation de la commande")
        order = Order.objects.create(
            user=request.user,
            subtotal=total_amount,
            shipping_cost=0,  # Pas de frais de livraison pour Orange Money
            total=total_amount,
            payment_method=Order.MOBILE_MONEY,
            status=Order.PENDING
        )
        logger.info(f"DEBUG Orange Money Payment - Commande creee: {order.order_number}")
        
        # Ajouter les items à la commande
        logger.info("DEBUG Orange Money Payment - Ajout des items a la commande")
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.get_unit_price()
            )
        logger.info(f"DEBUG Orange Money Payment - {cart_items.count()} items ajoutes")
        
        # Préparer les données pour Orange Money
        logger.info("DEBUG Orange Money Payment - Preparation des donnees Orange Money")
        
        # Utiliser les URLs configurées dans les variables d'environnement
        from django.conf import settings
        webhooks_config = settings.ORANGE_MONEY_WEBHOOKS
        
        # Utiliser les URLs configurées si disponibles, sinon construire les URLs complètes
        return_url = webhooks_config.get('return_url') or request.build_absolute_uri(reverse('cart:orange_money_return'))
        cancel_url = webhooks_config.get('cancel_url') or request.build_absolute_uri(reverse('cart:orange_money_cancel'))
        notif_url = webhooks_config.get('notification_url') or request.build_absolute_uri(reverse('cart:orange_money_webhook'))
        
        order_data = {
            'order_id': order.order_number,
            'amount': orange_money_service.format_amount(float(total_amount)),
            'return_url': return_url,
            'cancel_url': cancel_url,
            'notif_url': notif_url,
            'reference': f'SagaKore-{order.order_number}'
        }
        logger.info(f"DEBUG Orange Money Payment - Donnees preparees: {order_data}")
        
        # Créer la session de paiement
        logger.info("DEBUG Orange Money Payment - Creation de la session de paiement")
        success, response_data = orange_money_service.create_payment_session(order_data)
        logger.info(f"DEBUG Orange Money Payment - Session creee: success={success}, response={response_data}")
        
        if success:
            # Sauvegarder le token de paiement
            logger.info("DEBUG Orange Money Payment - Sauvegarde des tokens")
            pay_token = response_data.get('pay_token')
            notif_token = response_data.get('notif_token')
            
            # Stocker les tokens dans la session
            request.session['orange_money_pay_token'] = pay_token
            request.session['orange_money_notif_token'] = notif_token
            request.session['orange_money_order_id'] = order.id
            logger.info(f"DEBUG Orange Money Payment - Tokens sauvegardes: pay_token={pay_token}")
            
            # Construire l'URL de paiement
            payment_url = orange_money_service.get_payment_url(pay_token)
            logger.info(f"DEBUG Orange Money Payment - URL de paiement: {payment_url}")
            
            # Rediriger vers Orange Money
            return redirect(payment_url)
        else:
            # Erreur lors de la création de la session
            logger.error(f"DEBUG Orange Money Payment - Erreur creation session: {response_data}")
            order.delete()  # Supprimer la commande temporaire
            error_msg = response_data.get('error', 'Erreur inconnue')
            messages.error(request, f"❌ Erreur lors de l'initialisation du paiement Orange Money: {error_msg}")
            return redirect('cart:checkout')
            
    except Exception as e:
        logger.error(f"DEBUG Orange Money Payment - Exception: {str(e)}")
        import traceback
        logger.error(f"DEBUG Orange Money Payment - Traceback: {traceback.format_exc()}")
        messages.error(request, f"❌ Une erreur est survenue lors de l'initialisation du paiement: {str(e)}")
        return redirect('cart:checkout')


def orange_money_return(request):
    """
    Vue de retour après paiement Orange Money (succès ou échec)
    """
    order_id = request.session.get('orange_money_order_id')
    pay_token = request.session.get('orange_money_pay_token')
    
    if not order_id or not pay_token:
        messages.error(request, "❌ Session de paiement invalide.")
        return redirect('cart:cart')
    
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        
        # Vérifier le statut de la transaction
        success, status_data = orange_money_service.check_transaction_status(
            order.order_number,
            orange_money_service.format_amount(float(order.total)),
            pay_token
        )
        
        if success:
            status = status_data.get('status')
            if status == 'SUCCESS':
                # Paiement réussi
                order.is_paid = True
                order.paid_at = timezone.now()
                order.status = Order.CONFIRMED
                order.save()
                
                # Vider le panier
                Cart.objects.filter(user=request.user).delete()
                
                # Nettoyer la session
                request.session.pop('orange_money_pay_token', None)
                request.session.pop('orange_money_notif_token', None)
                request.session.pop('orange_money_order_id', None)
                
                messages.success(request, "✅ Paiement Orange Money effectué avec succès !")
                return redirect('cart:order_success', order_id=order.id)
            else:
                # Paiement échoué ou en attente
                messages.warning(request, f"⚠️ Statut du paiement: {status}")
                return redirect('cart:order_detail', order_id=order.id)
        else:
            # Erreur lors de la vérification
            error_msg = status_data.get('error', 'Erreur inconnue')
            messages.error(request, f"❌ Erreur lors de la vérification du paiement: {error_msg}")
            return redirect('cart:order_detail', order_id=order.id)
            
    except Order.DoesNotExist:
        messages.error(request, "❌ Commande introuvable.")
        return redirect('cart:cart')
    except Exception as e:
        logger.error(f"Erreur lors du retour Orange Money: {str(e)}")
        messages.error(request, "❌ Une erreur est survenue.")
        return redirect('cart:cart')


def orange_money_cancel(request):
    """
    Vue d'annulation du paiement Orange Money
    """
    order_id = request.session.get('orange_money_order_id')
    
    if order_id:
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            order.status = Order.CANCELLED
            order.save()
        except Order.DoesNotExist:
            pass
    
    # Nettoyer la session
    request.session.pop('orange_money_pay_token', None)
    request.session.pop('orange_money_notif_token', None)
    request.session.pop('orange_money_order_id', None)
    
    messages.info(request, "ℹ️ Paiement Orange Money annulé.")
    return redirect('cart:cart')


@csrf_exempt
def orange_money_webhook(request):
    """
    Webhook pour recevoir les notifications Orange Money
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if request.method != 'POST':
        return HttpResponse('Method not allowed', status=405)
    
    try:
        # Parser les données JSON
        notification_data = json.loads(request.body)
        
        # Récupérer les tokens de la session (si disponibles)
        notif_token = request.session.get('orange_money_notif_token')
        
        # Valider la notification
        if not orange_money_service.validate_webhook_notification(notification_data, notif_token):
            logger.warning("Notification Orange Money invalide reçue")
            return HttpResponse('Invalid notification', status=400)
        
        # Traiter la notification
        status = notification_data.get('status')
        order_id = notification_data.get('txnid')
        
        if status == 'SUCCESS':
            # Paiement réussi - mettre à jour la commande
            try:
                # Trouver la commande par order_number (pas par txnid)
                # Le txnid est l'ID de transaction Orange Money, pas notre order_number
                # On doit utiliser une autre méthode pour identifier la commande
                logger.info(f"Paiement Orange Money réussi pour la transaction {order_id}")
                
                # Ici, vous devriez implémenter une logique pour retrouver la commande
                # basée sur les données de la notification
                
            except Exception as e:
                logger.error(f"Erreur lors du traitement de la notification de succès: {str(e)}")
        
        elif status == 'FAILED':
            logger.info(f"Paiement Orange Money échoué pour la transaction {order_id}")
        
        return HttpResponse('OK', status=200)
        
    except json.JSONDecodeError:
        logger.error("Données JSON invalides reçues dans le webhook Orange Money")
        return HttpResponse('Invalid JSON', status=400)
    except Exception as e:
        logger.error(f"Erreur dans le webhook Orange Money: {str(e)}")
        return HttpResponse('Internal error', status=500)
