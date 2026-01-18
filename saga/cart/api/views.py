from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.urls import reverse
from decimal import Decimal
from .serializers import CartSerializer, CartItemSerializer
from cart.models import Cart, CartItem, Order, OrderItem
from product.models import Product, Phone, ShippingMethod
from accounts.models import ShippingAddress
from cart.services import CartService
from cart.orange_money_service import orange_money_service
import stripe
import logging

logger = logging.getLogger(__name__)


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [AllowAny]  # Permettre aux utilisateurs anonymes d'accéder au panier
    
    def _is_weighted_product(self, product):
        specs = product.specifications or {}
        sold_by_weight = specs.get('sold_by_weight')
        is_sold_by_weight = sold_by_weight is True or (
            isinstance(sold_by_weight, str) and sold_by_weight.lower() in ['true', '1', 'yes']
        )
        unit_type_raw = specs.get('unit_type')
        unit_type = str(unit_type_raw).lower() if unit_type_raw is not None else ''
        return is_sold_by_weight or unit_type in ['weight', 'kg', 'kilogram']

    def _get_weight_unit(self, product):
        specs = product.specifications or {}
        unit_raw = specs.get('weight_unit') or specs.get('unit_display') or specs.get('unit_type')
        if not unit_raw:
            return 'kg'
        unit = str(unit_raw).lower()
        if unit in ['weight', 'kg', 'kilogram']:
            return 'kg'
        if unit in ['g', 'gram', 'gramme']:
            return 'g'
        return unit

    def _get_available_weight(self, product):
        specs = product.specifications or {}
        unit = self._get_weight_unit(product)
        if unit == 'g':
            available_g = specs.get('available_weight_g')
            if available_g is not None:
                return Decimal(str(available_g))
            # Fallback: convertir le stock kg -> g si dispo
            available_kg = specs.get('available_weight_kg')
            if available_kg is not None:
                return Decimal(str(available_kg)) * Decimal('1000')
            return Decimal('0')
        available_kg = specs.get('available_weight_kg')
        if available_kg is not None:
            return Decimal(str(available_kg))
        # Fallback: convertir le stock g -> kg si dispo
        available_g = specs.get('available_weight_g')
        if available_g is not None:
            return Decimal(str(available_g)) / Decimal('1000')
        return Decimal('0')

    def get_queryset(self):
        """Retourne le panier de l'utilisateur connecté ou anonyme"""
        if self.request.user.is_authenticated:
            return Cart.objects.filter(user=self.request.user).prefetch_related(
                'cart_items__product',
                'cart_items__variant',
                'cart_items__colors',
                'cart_items__sizes'
            )
        else:
            # Pour les utilisateurs anonymes, utiliser la session
            if not self.request.session.session_key:
                self.request.session.create()
                self.request.session.save()
            session_key = self.request.session.session_key
            return Cart.objects.filter(session_key=session_key).prefetch_related(
                'cart_items__product',
                'cart_items__variant',
                'cart_items__colors',
                'cart_items__sizes'
            )

    def get_object(self):
        """Récupère ou crée le panier de l'utilisateur"""
        queryset = self.get_queryset()
        cart = queryset.first()
        
        if not cart:
            # Créer un nouveau panier
            if self.request.user.is_authenticated:
                cart = Cart.objects.create(user=self.request.user)
            else:
                if not self.request.session.session_key:
                    self.request.session.create()
                    self.request.session.save()
                cart = Cart.objects.create(session_key=self.request.session.session_key)
        
        return cart

    def list(self, request, *args, **kwargs):
        """Récupère le panier de l'utilisateur"""
        cart = self.get_object()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Récupère le panier (même comportement que list)"""
        return self.list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Ajoute un article au panier"""
        cart = self.get_object()
        
        product_id = request.data.get('product')
        variant_id = request.data.get('variant')
        # Préserver les décimales pour les produits au poids
        quantity_raw = request.data.get('quantity', 1)
        quantity = Decimal(str(quantity_raw)) if quantity_raw else Decimal('1')
        colors = request.data.get('colors', [])
        sizes = request.data.get('sizes', [])

        if not product_id:
            return Response(
                {'error': 'Le produit est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Produit introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Vérifier le stock si ce n'est pas un produit Salam
        if not product.is_salam:
            is_weighted = self._is_weighted_product(product)
            if is_weighted:
                unit = self._get_weight_unit(product)
                available_weight = self._get_available_weight(product)
                if available_weight < quantity:
                    return Response(
                        {'error': f'Stock insuffisant. Disponible: {available_weight} {unit}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                if quantity < Decimal('0.5'):
                    return Response(
                        {'error': f'La quantité minimale est de 0.5 {unit}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            elif product.stock < float(quantity):
                return Response(
                    {'error': f'Stock insuffisant. Disponible: {product.stock}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Vérifier si une variante est spécifiée
        variant = None
        if variant_id:
            try:
                variant = Phone.objects.get(id=variant_id, product=product)
                if variant.stock < float(quantity):
                    return Response(
                        {'error': f'Stock insuffisant pour cette variante. Disponible: {variant.stock}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except Phone.DoesNotExist:
                return Response(
                    {'error': 'Variante introuvable'},
                    status=status.HTTP_404_NOT_FOUND
                )

        # Chercher un item existant avec les mêmes caractéristiques
        cart_item = CartItem.objects.filter(
            cart=cart,
            product=product,
            variant=variant
        ).first()

        if cart_item:
            # Mettre à jour la quantité
            new_quantity = cart_item.quantity + quantity
            # Revalider le stock pour les produits au poids
            if not product.is_salam:
                is_weighted = self._is_weighted_product(product)
                if is_weighted:
                    unit = self._get_weight_unit(product)
                    available_weight = self._get_available_weight(product)
                    if available_weight < new_quantity:
                        return Response(
                            {'error': f'Stock insuffisant. Disponible: {available_weight} {unit}'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    if new_quantity < Decimal('0.5'):
                        return Response(
                            {'error': f'La quantité minimale est de 0.5 {unit}'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
            cart_item.quantity = new_quantity
            cart_item.save()
        else:
            # Créer un nouvel item
            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,
                variant=variant,
                quantity=quantity
            )
            if colors:
                cart_item.colors.set(colors)
            if sizes:
                cart_item.sizes.set(sizes)

        # Retourner le panier mis à jour
        # Re-chercher le panier pour s'assurer que les items sont à jour
        cart = self.get_queryset().filter(id=cart.id).first()
        serializer = self.get_serializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """Supprime le panier ou un item selon le contexte"""
        try:
            # Si un pk est fourni, c'est pour supprimer un item
            if 'pk' in kwargs and kwargs['pk']:
                item_id = kwargs['pk']
                cart = self.get_object()
                try:
                    cart_item = CartItem.objects.get(id=item_id, cart=cart)
                    cart_item.delete()
                    
                    # Re-chercher le panier pour s'assurer que les items sont à jour
                    cart = self.get_queryset().filter(id=cart.id).first()
                    serializer = self.get_serializer(cart)
                    return Response(serializer.data)
                except CartItem.DoesNotExist:
                    return Response(
                        {'error': 'Article introuvable'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                # Sinon, vider le panier
                return self.clear(request)
        except Exception as e:
            print(f"ERROR in CartViewSet.destroy: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        """Met à jour un article du panier"""
        try:
            # Si un pk est fourni, c'est pour mettre à jour un item
            if 'pk' in kwargs and kwargs['pk']:
                item_id = kwargs['pk']
                cart = self.get_object()
                try:
                    cart_item = CartItem.objects.get(id=item_id, cart=cart)
                except CartItem.DoesNotExist:
                    return Response(
                        {'error': 'Article introuvable'},
                        status=status.HTTP_404_NOT_FOUND
                    )

                quantity_raw = request.data.get('quantity')
                if quantity_raw is not None:
                    try:
                        quantity = Decimal(str(quantity_raw))
                    except Exception:
                        return Response(
                            {'error': 'Quantité invalide'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    if quantity <= 0:
                        cart_item.delete()
                    else:
                        # Vérifier le stock
                        product = cart_item.product
                        variant = cart_item.variant
                        is_weighted = self._is_weighted_product(product)

                        if variant:
                            if variant.stock < float(quantity):
                                return Response(
                                    {'error': f'Stock insuffisant. Disponible: {variant.stock}'},
                                    status=status.HTTP_400_BAD_REQUEST
                                )
                            # Pour les variantes, on garde une quantité entière
                            quantity = Decimal(int(quantity))
                        elif not product.is_salam:
                            if is_weighted:
                                unit = self._get_weight_unit(product)
                                available_weight = self._get_available_weight(product)
                                if available_weight < quantity:
                                    return Response(
                                        {'error': f'Stock insuffisant. Disponible: {available_weight} {unit}'},
                                        status=status.HTTP_400_BAD_REQUEST
                                    )
                                if quantity < Decimal('0.5'):
                                    return Response(
                                        {'error': f'La quantité minimale est de 0.5 {unit}'},
                                        status=status.HTTP_400_BAD_REQUEST
                                    )
                            elif product.stock < float(quantity):
                                return Response(
                                    {'error': f'Stock insuffisant. Disponible: {product.stock}'},
                                    status=status.HTTP_400_BAD_REQUEST
                                )
                            else:
                                # Produits à l'unité -> forcer à l'entier
                                quantity = Decimal(int(quantity))
                        
                        cart_item.quantity = quantity
                        cart_item.save()

                # Re-chercher le panier pour s'assurer que les items sont à jour
                cart = self.get_queryset().filter(id=cart.id).first()
                serializer = self.get_serializer(cart)
                return Response(serializer.data)
            else:
                # Sinon, mettre à jour le panier lui-même (non implémenté pour l'instant)
                return Response(
                    {'error': 'Mise à jour du panier non supportée'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            print(f"ERROR in CartViewSet.update: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, *args, **kwargs):
        """Met à jour partiellement un article du panier"""
        return self.update(request, *args, **kwargs)

    @action(detail=False, methods=['delete'], url_path='clear')
    def clear(self, request):
        """Vide le panier (supprime tous les items)"""
        print(f"DEBUG: Clear cart called for user {request.user}")
        try:
            cart = self.get_object()
            if not cart:
                return Response({'items': [], 'total_price': 0})
                
            cart.cart_items.all().delete()
            
            # Retourner un objet panier vide propre
            return Response({
                'id': cart.id,
                'items': [],
                'total_price': 0,
                'items_count': 0
            })
        except Exception as e:
            print(f"ERROR in CartViewSet.clear: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def checkout(self, request):
        """
        Initié le processus de commande pour le mobile.
        Retourne une URL de paiement (Stripe ou Orange Money).
        """
        user = request.user
        cart = self.get_object()
        
        payment_method = request.data.get('payment_method')  # 'stripe', 'orange_money', 'cash_on_delivery'
        address_id = request.data.get('shipping_address_id')
        product_type = request.data.get('product_type', 'all')  # 'classic', 'salam', 'all'
        
        if not payment_method:
            return Response({'error': 'La méthode de paiement est requise'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not address_id:
            return Response({'error': 'L\'adresse de livraison est requise'}, status=status.HTTP_400_BAD_REQUEST)
            
        address = get_object_or_404(ShippingAddress, id=address_id, user=user)
        
        # Valider le panier
        is_valid, errors = CartService.validate_cart_for_checkout(cart, product_type)
        if not is_valid:
            return Response({'error': errors[0] if errors else 'Panier invalide'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Déterminer la méthode de livraison par défaut (la première disponible)
        shipping_method = ShippingMethod.objects.first()
        if not shipping_method:
            return Response({'error': 'Aucune méthode de livraison configurée'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # 1. Créer la commande
                total_price = cart.get_total_price()
                order = Order.objects.create(
                    user=user,
                    shipping_address=address,
                    shipping_method=shipping_method,
                    payment_method=payment_method,
                    subtotal=total_price,
                    shipping_cost=shipping_method.price,
                    total=total_price + shipping_method.price,
                    status=Order.PENDING
                )
                
                # 2. Créer les items de commande
                for item in cart.cart_items.all():
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.get_unit_price()
                    )
                    if item.colors.exists():
                        order_item.colors.set(item.colors.all())
                    if item.sizes.exists():
                        order_item.sizes.set(item.sizes.all())

                # 3. Gérer le paiement
                domain_url = request.build_absolute_uri('/')[:-1]
                
                if payment_method == 'stripe' or payment_method == 'online_payment':
                    stripe.api_key = settings.STRIPE_SECRET_KEY
                    
                    line_items = []
                    for item in order.items.all():
                        line_items.append({
                            'price_data': {
                                'currency': 'xof',
                                'product_data': {'name': item.product.title},
                                'unit_amount': int(item.price),
                            },
                            'quantity': int(float(item.quantity)),  # Stripe nécessite un entier pour quantity
                        })
                    
                    # Ajouter les frais de livraison
                    line_items.append({
                        'price_data': {
                            'currency': 'xof',
                            'product_data': {'name': 'Frais de livraison'},
                            'unit_amount': int(order.shipping_cost),
                        },
                        'quantity': 1,
                    })

                    checkout_session = stripe.checkout.Session.create(
                        customer_email=user.email,
                        payment_method_types=['card'],
                        line_items=line_items,
                        mode='payment',
                        success_url=f"{domain_url}/cart/success/?session_id={{CHECKOUT_SESSION_ID}}&order_id={order.id}",
                        cancel_url=f"{domain_url}/cart/cancel/?order_id={order.id}",
                        metadata={'order_id': order.id, 'mobile': 'true'}
                    )
                    
                    order.stripe_session_id = checkout_session.id
                    order.save()
                    
                    return Response({
                        'order_id': order.id,
                        'checkout_url': checkout_session.url,
                        'payment_method': 'stripe'
                    })

                elif payment_method == 'orange_money' or payment_method == 'mobile_money':
                    order_data = {
                        'order_id': order.order_number,
                        'amount': int(order.total * 100),  # Orange Money veut des centimes? Non, FCFA? 
                        # Selon orange_money_service.py: format_amount multiplie par 100
                        'amount': orange_money_service.format_amount(float(order.total)),
                        'return_url': f"{domain_url}/cart/success/?order_id={order.id}",
                        'cancel_url': f"{domain_url}/cart/cancel/?order_id={order.id}",
                        'notif_url': f"{domain_url}/api/cart/orange-money-webhook/",
                        'reference': f"CMD-{order.id}"
                    }
                    
                    success, response_data = orange_money_service.create_payment_session(order_data)
                    if success:
                        payment_url = orange_money_service.get_payment_url(
                            response_data.get('pay_token'), 
                            response_data.get('payment_url')
                        )
                        return Response({
                            'order_id': order.id,
                            'checkout_url': payment_url,
                            'payment_method': 'orange_money'
                        })
                    else:
                        return Response({'error': response_data.get('error', 'Erreur Orange Money')}, status=status.HTTP_400_BAD_REQUEST)

                elif payment_method == 'cash_on_delivery':
                    # Pour le paiement à la livraison, pas d'URL de redirection
                    # On vide le panier car la commande est validée
                    cart.cart_items.all().delete()
                    return Response({
                        'order_id': order.id,
                        'status': 'confirmed',
                        'message': 'Commande enregistrée avec succès (Paiement à la livraison)',
                        'payment_method': 'cash_on_delivery'
                    })

                return Response({'error': 'Méthode de paiement non supportée'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Checkout Error: {str(e)}")
            return Response({'error': f"Erreur lors de la commande: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 