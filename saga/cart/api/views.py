from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import transaction
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from django.urls import reverse
from decimal import Decimal
from .serializers import CartSerializer, CartItemSerializer
from cart.models import Cart, CartItem, Order, OrderItem
from product.models import Product, Phone, ShippingMethod
from accounts.models import ShippingAddress
from cart.services import CartService
from cart.orange_money_service import orange_money_service
from inventory.services import OrderSyncService
import stripe
import logging
import json

logger = logging.getLogger("cart.checkout")


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [AllowAny]  # Permettre aux utilisateurs anonymes d'accéder au panier
    
    def _is_weighted_product(self, product):
        specs = product.specifications or {}
        sold_by_weight = specs.get('sold_by_weight')
        is_sold_by_weight = sold_by_weight is True or (
            isinstance(sold_by_weight, str) and sold_by_weight.lower() in ['true', '1', 'yes']
        )
        unit_raw = specs.get('weight_unit') or specs.get('unit_display') or specs.get('unit_type')
        unit = str(unit_raw).lower() if unit_raw is not None else ''
        normalized_unit = unit.replace(' ', '')
        has_gram_fields = specs.get('available_weight_g') is not None or specs.get('price_per_g') is not None or specs.get('discount_price_per_g') is not None
        has_kg_fields = specs.get('available_weight_kg') is not None or specs.get('price_per_kg') is not None or specs.get('discount_price_per_kg') is not None
        return (
            is_sold_by_weight
            or unit in ['weight', 'kg', 'kilogram', 'g', 'gram', 'gramme']
            or ('kg' in normalized_unit)
            or (normalized_unit.endswith('g') and normalized_unit != 'kg')
            or has_gram_fields
            or has_kg_fields
        )

    def _get_weight_unit(self, product):
        specs = product.specifications or {}
        unit_raw = specs.get('weight_unit') or specs.get('unit_display') or specs.get('unit_type')
        if not unit_raw:
            # Heuristique: si des champs grammes existent, utiliser g
            if specs.get('available_weight_g') is not None or specs.get('price_per_g') is not None or specs.get('discount_price_per_g') is not None:
                return 'g'
            return 'kg'
        unit = str(unit_raw).lower()
        normalized_unit = unit.replace(' ', '')
        if unit in ['weight', 'kg', 'kilogram']:
            return 'kg'
        if unit in ['g', 'gram', 'gramme']:
            return 'g'
        if 'kg' in normalized_unit:
            return 'kg'
        if normalized_unit.endswith('g'):
            return 'g'
        return unit

    def _get_client_ip(self, request):
        if not request:
            return None
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

    def _track_payment_failure(self, request, payment_method, order_ids, error):
        window_seconds = getattr(settings, 'PAYMENT_FAILURE_WINDOW_SECONDS', 900)
        threshold = getattr(settings, 'PAYMENT_FAILURE_ALERT_THRESHOLD', 3)
        client_ip = self._get_client_ip(request) or 'unknown'
        method = payment_method or 'unknown'
        cache_key = f"payment_failed:{method}:{client_ip}"
        data = cache.get(cache_key) or {
            'count': 0,
            'first_seen': timezone.now().isoformat(),
        }
        data['count'] += 1
        cache.set(cache_key, data, timeout=window_seconds)

        if data['count'] == threshold or data['count'] % threshold == 0:
            logger.warning(
                "Alerte paiement anormal: method=%s ip=%s count=%s first_seen=%s window=%ss orders=%s error=%s",
                method,
                client_ip,
                data['count'],
                data['first_seen'],
                window_seconds,
                order_ids,
                str(error),
            )

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

    def _to_decimal(self, value, default=None):
        if value is None:
            return default
        try:
            return Decimal(str(value))
        except Exception:
            return default

    def _normalize_method_id(self, value):
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return str(value)

    def _get_delivery_methods_for_product(self, product):
        methods = []
        specs = product.specifications or {}
        raw_methods = specs.get('delivery_methods')
        if isinstance(raw_methods, list):
            for raw in raw_methods:
                if not isinstance(raw, dict):
                    continue
                method_id = raw.get('id')
                name = raw.get('name')
                if method_id is None or not name:
                    continue
                methods.append({
                    'id': self._normalize_method_id(method_id),
                    'name': str(name),
                    'slug': raw.get('slug'),
                    'description': raw.get('description'),
                    'base_price': self._to_decimal(raw.get('base_price')),
                    'effective_price': self._to_decimal(raw.get('effective_price')),
                    'override_price': self._to_decimal(raw.get('override_price')),
                    'order': raw.get('order'),
                    'site_configuration': raw.get('site_configuration'),
                    'source': 'specs',
                    'shipping_method_obj': None,
                })

        if not methods:
            for method in product.shipping_methods.all():
                methods.append({
                    'id': self._normalize_method_id(method.id),
                    'name': method.name,
                    'slug': None,
                    'description': None,
                    'base_price': method.price,
                    'effective_price': method.price,
                    'override_price': None,
                    'order': None,
                    'site_configuration': None,
                    'source': 'model',
                    'shipping_method_obj': method,
                })

        return methods

    def _get_delivery_method_price(self, method):
        if not method:
            return Decimal('0')
        for key in ['effective_price', 'override_price', 'base_price']:
            value = method.get(key)
            if value is not None:
                return self._to_decimal(value, Decimal('0')) or Decimal('0')
        shipping_method_obj = method.get('shipping_method_obj')
        if shipping_method_obj:
            return self._to_decimal(shipping_method_obj.price, Decimal('0')) or Decimal('0')
        return Decimal('0')

    def _sync_order_to_b2b(self, order):
        """
        Synchronise une commande vers B2B de manière asynchrone (non bloquante)
        """
        try:
            sync_service = OrderSyncService()
            result = sync_service.sync_order_to_b2b(order)
            logger.info(
                f"Commande {order.order_number} synchronisée vers B2B "
                f"(external_sale_id: {result.get('external_sale_id')})"
            )
        except Exception as e:
            # Ne pas bloquer le flux de paiement en cas d'erreur de sync
            logger.error(
                f"Erreur synchronisation commande {order.order_number} vers B2B: {str(e)}",
                exc_info=True
            )
    
    def _clear_user_cart(self, user):
        if not user:
            return
        cart = Cart.objects.filter(user=user).first()
        if cart:
            cart.cart_items.all().delete()

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
                else:
                    # Produits classiques: vérifier le stock total (variante ou produit)
                    if variant:
                        if variant.stock < float(new_quantity):
                            return Response(
                                {'error': f'Stock insuffisant pour cette variante. Disponible: {variant.stock}'},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                    else:
                        if product.stock < float(new_quantity):
                            return Response(
                                {'error': f'Stock insuffisant. Disponible: {product.stock}'},
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
        shipping_method_id = request.data.get('shipping_method_id')
        product_type = request.data.get('product_type', 'all')  # 'classic', 'salam', 'all'
        
        if not payment_method:
            return Response({'error': 'La méthode de paiement est requise'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not address_id:
            return Response({'error': 'L\'adresse de livraison est requise'}, status=status.HTTP_400_BAD_REQUEST)
            
        address = get_object_or_404(ShippingAddress, id=address_id, user=user)
        
        # Valider le panier
        logger.warning(
            "Checkout start - user=%s cart=%s items=%s product_type=%s payment=%s",
            user.id,
            cart.id,
            cart.cart_items.count(),
            product_type,
            payment_method,
        )
        is_valid, errors = CartService.validate_cart_for_checkout(cart, product_type)
        if not is_valid:
            logger.warning(
                "Checkout validation failed - cart=%s errors=%s",
                cart.id,
                errors,
            )
            return Response({'error': errors[0] if errors else 'Panier invalide'}, status=status.HTTP_400_BAD_REQUEST)
            
        cart_items = cart.cart_items.select_related(
            'product',
            'variant'
        ).prefetch_related(
            'colors',
            'sizes',
            'product__shipping_methods'
        )

        default_shipping_method = ShippingMethod.objects.first()
        default_method_option = None
        if default_shipping_method:
            default_method_option = {
                'id': self._normalize_method_id(default_shipping_method.id),
                'name': default_shipping_method.name,
                'slug': None,
                'description': None,
                'base_price': default_shipping_method.price,
                'effective_price': default_shipping_method.price,
                'override_price': None,
                'order': None,
                'site_configuration': None,
                'source': 'model',
                'shipping_method_obj': default_shipping_method,
            }

        warnings = []
        shipping_method_id_normalized = (
            self._normalize_method_id(shipping_method_id) if shipping_method_id else None
        )
        item_methods = {}
        method_keys_by_item = []
        method_by_key = {}

        for item in cart_items:
            methods = self._get_delivery_methods_for_product(item.product)
            if not methods and default_method_option:
                methods = [default_method_option]
            item_methods[item.id] = methods
            keys = set()
            for method in methods:
                method_id = self._normalize_method_id(method.get('id'))
                site_id = method.get('site_configuration')
                key = (site_id, method_id)
                keys.add(key)
                if key not in method_by_key:
                    method_by_key[key] = method
            method_keys_by_item.append(keys)

        common_keys = set.intersection(*method_keys_by_item) if method_keys_by_item else set()
        selected_common_key = None
        if shipping_method_id_normalized is not None and common_keys:
            for key in common_keys:
                if key[1] == shipping_method_id_normalized:
                    selected_common_key = key
                    break
        if selected_common_key is None and common_keys:
            selected_common_key = next(iter(common_keys))

        groups = {}
        missing_selected = []
        for item in cart_items:
            methods = item_methods.get(item.id, [])
            selected_method = None
            if selected_common_key:
                selected_method = method_by_key.get(selected_common_key)
            else:
                if shipping_method_id_normalized is not None:
                    for method in methods:
                        if self._normalize_method_id(method.get('id')) == shipping_method_id_normalized:
                            selected_method = method
                            break
                    if not selected_method:
                        missing_selected.append(item.id)
                if not selected_method:
                    selected_method = methods[0] if methods else None

            if not selected_method:
                selected_method = default_method_option or {
                    'id': None,
                    'name': 'Livraison',
                    'slug': None,
                    'description': None,
                    'base_price': Decimal('0'),
                    'effective_price': Decimal('0'),
                    'override_price': None,
                    'order': None,
                    'site_configuration': None,
                    'source': 'fallback',
                    'shipping_method_obj': None,
                }

            method_id = self._normalize_method_id(selected_method.get('id'))
            site_id = selected_method.get('site_configuration')
            group_key = (site_id, method_id)
            group = groups.setdefault(group_key, {'method': selected_method, 'items': []})
            group['items'].append(item)

        if missing_selected:
            warnings.append('La méthode de livraison choisie n’est pas disponible pour tous les produits.')

        def serialize_method(method):
            return {
                'id': method.get('id'),
                'name': method.get('name'),
                'slug': method.get('slug'),
                'description': method.get('description'),
                'base_price': str(method.get('base_price')) if method.get('base_price') is not None else None,
                'effective_price': str(method.get('effective_price')) if method.get('effective_price') is not None else None,
                'override_price': str(method.get('override_price')) if method.get('override_price') is not None else None,
                'order': method.get('order'),
                'site_configuration': method.get('site_configuration'),
            }

        try:
            with transaction.atomic():
                group_orders = []
                logger.info(
                    "Checkout - Groupement par site/méthode: %s groupes créés",
                    len(groups)
                )

                for group_key, group in groups.items():
                    method = group['method']
                    shipping_cost = self._get_delivery_method_price(method)
                    subtotal = sum(item.get_total_price() for item in group['items'])
                    method_payload = serialize_method(method)
                    site_id = method.get('site_configuration')
                    method_id = method.get('id')

                    logger.info(
                        "Checkout - Création commande groupe: site=%s method=%s items=%s subtotal=%s shipping=%s",
                        site_id,
                        method_id,
                        len(group['items']),
                        subtotal,
                        shipping_cost
                    )

                    metadata = {
                        'delivery_method': method_payload,
                        'delivery_site_configuration': site_id,
                        'delivery_group_key': f"{group_key[0]}:{group_key[1]}",
                        'split_order': len(groups) > 1,
                        'group_items_count': len(group['items']),
                    }
                    order = Order.objects.create(
                        user=user,
                        shipping_address=address,
                        shipping_method=method.get('shipping_method_obj'),
                        payment_method=payment_method,
                        subtotal=subtotal,
                        shipping_cost=shipping_cost,
                        total=subtotal + shipping_cost,
                        status=Order.DRAFT,
                        metadata=metadata
                    )

                    for item in group['items']:
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

                    group_orders.append({
                        'order': order,
                        'method': method_payload,
                        'site_configuration': site_id,
                    })

                    logger.info(
                        "Checkout - Commande créée: order=%s site=%s method=%s total=%s",
                        order.id,
                        site_id,
                        method_id,
                        order.total
                    )

            domain_url = request.build_absolute_uri('/')[:-1]
            payment_results = []

            # Détecter si la requête vient d'un mobile
            user_agent = (request.META.get('HTTP_USER_AGENT', '') or '').lower()
            is_mobile_request = any(marker in user_agent for marker in ['mobile', 'android', 'iphone', 'ipad', 'okhttp'])
            mobile_param = '&mobile=1' if is_mobile_request else ''

            logger.info(
                "Checkout - Début paiement: user=%s cart=%s method=%s split=%s",
                user.id if user else None,
                cart.id if cart else None,
                payment_method,
                len(group_orders) > 1,
            )

                if payment_method == 'stripe' or payment_method == 'online_payment':
                    stripe.api_key = settings.STRIPE_SECRET_KEY
                    for entry in group_orders:
                        order = entry['order']
                        logger.warning(
                            "Checkout Stripe - order=%s cart=%s items=%s total=%s shipping=%s",
                            order.id,
                            cart.id,
                            order.items.count(),
                            order.total,
                            order.shipping_cost,
                        )
                        line_items = []
                        for item in order.items.all():
                            total_price = Decimal(str(item.price)) * Decimal(str(item.quantity))
                            quantity_decimal = Decimal(str(item.quantity))
                            is_weighted = self._is_weighted_product(item.product)
                            weight_unit = self._get_weight_unit(item.product) if is_weighted else 'unité'
                            specs = item.product.specifications or {}

                            if is_weighted:
                                stripe_quantity = 1
                                stripe_unit_amount = max(1, int(float(total_price)))
                            else:
                                stripe_quantity = max(1, int(float(quantity_decimal)))
                                stripe_unit_amount = max(1, int(float(item.price)))

                            logger.warning(
                                "Checkout Stripe item - product=%s title=%s qty=%s is_weighted=%s unit=%s "
                                "price=%s total=%s stripe_qty=%s stripe_amount=%s specs_keys=%s",
                                item.product.id,
                                item.product.title,
                                item.quantity,
                                is_weighted,
                                weight_unit,
                                item.price,
                                total_price,
                                stripe_quantity,
                                stripe_unit_amount,
                                list(specs.keys()),
                            )

                            line_items.append({
                                'price_data': {
                                    'currency': 'xof',
                                    'product_data': {'name': item.product.title},
                                    'unit_amount': stripe_unit_amount,
                                },
                                'quantity': stripe_quantity,
                            })

                        shipping_cost_int = int(order.shipping_cost)
                        if shipping_cost_int > 0:
                            line_items.append({
                                'price_data': {
                                    'currency': 'xof',
                                    'product_data': {'name': 'Frais de livraison'},
                                    'unit_amount': shipping_cost_int,
                                },
                                'quantity': 1,
                            })

                        checkout_session = stripe.checkout.Session.create(
                            customer_email=user.email,
                            payment_method_types=['card'],
                            line_items=line_items,
                            mode='payment',
                            success_url=f"{domain_url}/api/cart/payment-success/?session_id={{CHECKOUT_SESSION_ID}}&order_id={order.id}{mobile_param}",
                            cancel_url=f"{domain_url}/api/cart/payment-cancel/?order_id={order.id}&mobile=1",
                            metadata={
                                'order_id': str(order.id),
                                'cart_id': str(cart.id),
                                'user_id': str(user.id),
                                'payment_method': payment_method,
                                'mobile': 'true'
                            }
                        )

                        order.stripe_session_id = checkout_session.id
                        order.save(update_fields=['stripe_session_id'])
                        logger.info(
                            "Stripe session créée - order=%s session=%s status=%s amount_total=%s",
                            order.id,
                            checkout_session.id,
                            checkout_session.payment_status,
                            checkout_session.amount_total,
                        )

                        payment_results.append({
                            'order_id': order.id,
                            'checkout_url': checkout_session.url,
                            'payment_method': 'stripe',
                            'shipping_method': entry['method'],
                            'site_configuration': entry['site_configuration'],
                            'subtotal': str(order.subtotal),
                            'shipping_cost': str(order.shipping_cost),
                            'total': str(order.total),
                        })

                elif payment_method == 'orange_money' or payment_method == 'mobile_money':
                    for entry in group_orders:
                        order = entry['order']
                        logger.info(
                            "Checkout Orange Money - order=%s site=%s method=%s items=%s total=%s",
                            order.id,
                            entry['site_configuration'],
                            entry['method'].get('id'),
                            order.items.count(),
                            order.total,
                        )
                        order_data = {
                            'order_id': order.order_number,
                            'amount': int(order.total * 100),
                            'amount': orange_money_service.format_amount(float(order.total)),
                            'return_url': f"{domain_url}/api/cart/orange-money-return/?order_id={order.id}",
                            'cancel_url': f"{domain_url}/api/cart/orange-money-cancel/?order_id={order.id}&mobile=1",
                            'notif_url': f"{domain_url}/api/cart/orange-money-webhook/",
                            'reference': f"CMD-{order.id}"
                        }

                        success, response_data = orange_money_service.create_payment_session(order_data)
                        if not success:
                            raise ValueError(response_data.get('error', 'Erreur Orange Money'))

                        payment_url = orange_money_service.get_payment_url(
                            response_data.get('pay_token'),
                            response_data.get('payment_url')
                        )
                        metadata = order.metadata or {}
                        metadata.update({
                            'orange_money_pay_token': response_data.get('pay_token'),
                            'orange_money_notif_token': response_data.get('notif_token'),
                            'orange_money_order_number': order.order_number
                        })
                        order.metadata = metadata
                        order.save(update_fields=['metadata'])

                        payment_results.append({
                            'order_id': order.id,
                            'checkout_url': payment_url,
                            'payment_method': 'orange_money',
                            'shipping_method': entry['method'],
                            'site_configuration': entry['site_configuration'],
                            'subtotal': str(order.subtotal),
                            'shipping_cost': str(order.shipping_cost),
                            'total': str(order.total),
                        })

                elif payment_method == 'cash_on_delivery':
                    # Vider le panier après création de toutes les commandes
                    transaction.on_commit(lambda: cart.cart_items.all().delete())
                    
                    for entry in group_orders:
                        order = entry['order']
                        if order.status != Order.CONFIRMED:
                            order.status = Order.CONFIRMED
                            order.save(update_fields=['status'])
                        
                        # Synchroniser chaque commande vers B2B
                        transaction.on_commit(lambda o=order: self._sync_order_to_b2b(o))
                        
                        logger.info(
                            "Checkout cash_on_delivery - Commande confirmée: order=%s site=%s total=%s",
                            order.id,
                            entry['site_configuration'],
                            order.total
                        )
                        
                        payment_results.append({
                            'order_id': order.id,
                            'status': 'confirmed',
                            'payment_method': 'cash_on_delivery',
                            'shipping_method': entry['method'],
                            'site_configuration': entry['site_configuration'],
                            'subtotal': str(order.subtotal),
                            'shipping_cost': str(order.shipping_cost),
                            'total': str(order.total),
                        })
                else:
                    return Response({'error': 'Méthode de paiement non supportée'}, status=status.HTTP_400_BAD_REQUEST)

                response_payload = {
                    'orders': payment_results,
                    'payment_method': payment_method,
                    'split': len(payment_results) > 1,
                }
                if warnings:
                    response_payload['warnings'] = warnings
                if len(payment_results) == 1:
                    single = payment_results[0]
                    response_payload.update({
                        'order_id': single.get('order_id'),
                        'checkout_url': single.get('checkout_url'),
                        'status': single.get('status'),
                    })

                return Response(response_payload)

        except Exception as e:
            order_ids = []
            try:
                order_ids = [entry['order'].id for entry in group_orders]
            except Exception:
                order_ids = []
            self._track_payment_failure(request, payment_method, order_ids, e)
            logger.error(f"Checkout Error: {str(e)}")
            return Response({'error': f"Erreur lors de la commande: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='payment-success', permission_classes=[AllowAny])
    def payment_success(self, request):
        session_id = request.GET.get('session_id')
        order_id = request.GET.get('order_id')
        if not session_id:
            return Response({'error': 'session_id manquant'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            session = stripe.checkout.Session.retrieve(session_id)
            logger.info(
                "Stripe payment_success - session=%s status=%s metadata=%s",
                session.id,
                session.payment_status,
                session.metadata,
            )
            
            if session.payment_status != 'paid':
                logger.warning("Stripe Payment Success - Le paiement n'est pas encore 'paid' (status: %s)", session.payment_status)
                return Response({'status': 'pending', 'message': 'Paiement non confirmé'}, status=status.HTTP_200_OK)

            order = None
            metadata_order_id = session.metadata.get('order_id') if session.metadata else None
            if metadata_order_id:
                order = Order.objects.filter(id=metadata_order_id).first()
            
            if not order and order_id:
                order = Order.objects.filter(id=order_id).first()
            
            if not order:
                order = Order.objects.filter(stripe_session_id=session_id).first()
            
            if not order:
                logger.error("ERREUR: Commande introuvable pour la session %s", session_id)
                return Response({'error': 'Commande introuvable'}, status=status.HTTP_404_NOT_FOUND)

            logger.info(
                "Stripe payment_success - Commande trouvée: order=%s status=%s is_paid=%s",
                order.id,
                order.status,
                order.is_paid,
            )

            order.stripe_session_id = session.id
            order.stripe_payment_status = session.payment_status
            
            # Mettre à jour le statut et is_paid si nécessaire
            if not order.is_paid:
                old_status = order.status
                order.mark_as_paid()
                logger.info(
                    "Stripe payment_success - Statut mis à jour: order=%s %s→%s is_paid=%s",
                    order.id,
                    old_status,
                    order.status,
                    order.is_paid,
                )
            else:
                # Si déjà payé, s'assurer que le statut est CONFIRMED
                if order.status == Order.DRAFT:
                    order.status = Order.CONFIRMED
                    order.save(update_fields=['status', 'stripe_session_id', 'stripe_payment_status'])
                    logger.info(
                        "Stripe payment_success - Statut forcé CONFIRMED: order=%s",
                        order.id,
                    )
                else:
                    order.save(update_fields=['stripe_session_id', 'stripe_payment_status'])

            # Synchroniser vers B2B après paiement réussi
            self._sync_order_to_b2b(order)
            logger.info(
                "Stripe payment_success - Sync B2B déclenchée: order=%s",
                order.id,
            )
            
            # Vider le panier de l'utilisateur après un paiement réussi.
            self._clear_user_cart(order.user)
            logger.info(
                "Stripe payment_success - Panier vidé: user=%s",
                order.user.id if order.user else None,
            )
            
            # Détection mobile : priorité au paramètre mobile=1 dans l'URL
            is_mobile_param = request.GET.get('mobile') == '1' or request.GET.get('mobile') == 'true'
            
            # Vérifications supplémentaires si pas de paramètre
            if not is_mobile_param:
                user_agent = (request.META.get('HTTP_USER_AGENT', '') or '').lower()
                referer = (request.META.get('HTTP_REFERER', '') or '').lower()
                accept = (request.META.get('HTTP_ACCEPT') or '').lower()
                
                is_mobile_ua = any(marker in user_agent for marker in ['mobile', 'android', 'iphone', 'ipad', 'okhttp'])
                is_mobile_referer = 'bolibana' in referer or 'mobile' in referer
                wants_html = 'text/html' in accept or request.GET.get('format') == 'html'
                
                is_mobile_param = is_mobile_ua or is_mobile_referer or wants_html
            
            # Si c'est mobile, retourner une page HTML qui redirige vers l'app
            if is_mobile_param:
                from django.shortcuts import render
                context = {
                    'order_id': str(order.id) if order.id else '',
                    'order_number': str(order.order_number) if order.order_number else '',
                    'status': order.status,
                    'is_paid': order.is_paid,
                }
                logger.info(
                    "Stripe payment_success - Réponse HTML mobile: order=%s",
                    order.id,
                )
                return render(request, 'cart/payment_success_mobile.html', context, status=200)

            
            # Sinon, retourner JSON pour les appels API
            return Response({
                'status': 'success',
                'message': 'Paiement confirmé, panier vidé',
                'order_id': order.id,
                'order_status': order.status,
                'is_paid': order.is_paid
            })
        except Exception as e:
            logger.error(f"Payment success error: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='payment-callback', permission_classes=[AllowAny])
    def payment_callback(self, request):
        """
        Route de callback pour l'app mobile.
        Cette page est interceptée par l'app via Linking lorsque l'URL HTTPS est chargée.
        L'app ferme alors le WebBrowser et navigue vers l'écran approprié.
        On ne tente plus de rediriger vers bolibana:// depuis JavaScript (bloqué par WebBrowser Expo).
        """
        from django.http import HttpResponse
        
        order_id = request.GET.get('order_id')
        order_number = request.GET.get('order_number')
        
        if not order_id:
            return HttpResponse(
                '<html><body><h1>Erreur 400</h1><p>order_id manquant</p></body></html>',
                status=400
            )
        
        # Construire l'URL HTTPS complète (sera interceptée par l'app via Linking)
        domain_url = request.build_absolute_uri('/')[:-1]
        callback_url = f"{domain_url}/api/cart/payment-callback/?order_id={order_id}"
        if order_number:
            callback_url += f"&order_number={order_number}"
        
        # Page HTML simple : l'app intercepte cette URL HTTPS via Linking
        # Plus besoin de JavaScript complexe pour rediriger vers bolibana://
        html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Paiement réussi - BoliBana</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #10B981 0%, #059669 100%);
            padding: 20px;
        }}
        .container {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 400px;
            width: 100%;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }}
        .success-icon {{
            width: 80px;
            height: 80px;
            background: #10B981;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
        }}
        .success-icon svg {{
            width: 50px;
            height: 50px;
            color: white;
        }}
        h1 {{
            color: #1F2937;
            font-size: 24px;
            margin-bottom: 10px;
        }}
        .message {{
            color: #6B7280;
            font-size: 16px;
            margin-bottom: 30px;
            line-height: 1.5;
        }}
        .order-info {{
            background: #F3F4F6;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 30px;
        }}
        .order-number {{
            font-size: 18px;
            font-weight: 600;
            color: #1F2937;
            margin-bottom: 5px;
        }}
        .order-status {{
            font-size: 14px;
            color: #10B981;
            font-weight: 500;
        }}
        .button {{
            background: #10B981;
            color: white;
            border: none;
            border-radius: 12px;
            padding: 16px 32px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: background 0.2s;
            text-decoration: none;
            display: inline-block;
        }}
        .button:hover {{
            background: #059669;
        }}
        .button:active {{
            transform: scale(0.98);
        }}
        .info-text {{
            font-size: 12px;
            color: #9CA3AF;
            margin-top: 20px;
        }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
        </div>
        <h1>Paiement réussi !</h1>
        <p class="message">Votre commande a été confirmée avec succès.</p>
        
        <div class="order-info">
            <div class="order-number">Commande #{order_number if order_number else order_id}</div>
            <div class="order-status">Statut: Confirmée</div>
        </div>
        
        <button class="button" id="openAppButton" onclick="openApp()" style="margin-top: 20px;">Fermer et retourner à l'application</button>
        <p class="info-text">Si la page ne se ferme pas automatiquement, appuyez sur le bouton ci-dessus.</p>
    </div>
    <script>
        // Utiliser location.replace pour sortir de l'historique
        
        const orderId = '{order_id}';
        const orderNumber = '{order_number}';
        const deepLink = 'bolibana://payment-success?order_id=' + encodeURIComponent(orderId) + '&order_number=' + encodeURIComponent(orderNumber);
        
        function openApp() {{
            try {{
                window.location.replace(deepLink);
            }} catch (e) {{
                window.location.href = deepLink;
            }}
        }}
        
        // Tentative automatique
        setTimeout(openApp, 500);
        
        document.addEventListener('DOMContentLoaded', function() {{
            const button = document.getElementById('openAppButton');
            if (button) button.addEventListener('click', openApp);
        }});
    </script>
</body>
</html>
        """
        
        return HttpResponse(html_content, content_type='text/html', status=200)
    
    @action(detail=False, methods=['get'], url_path='payment-cancel', permission_classes=[AllowAny])
    def payment_cancel(self, request):
        order_id = request.GET.get('order_id')
        logger.info("Stripe payment_cancel - order=%s", order_id)
        accept = (request.META.get('HTTP_ACCEPT') or '').lower()
        if request.GET.get('mobile') == '1' or 'text/html' in accept:
            return render(request, 'payment_cancel.html', status=200)
        return Response({'status': 'cancelled', 'message': 'Paiement annulé'})

    @action(detail=False, methods=['get'], url_path='orange-money-return', permission_classes=[AllowAny])
    def orange_money_return(self, request):
        order_id = request.GET.get('order_id')
        if not order_id:
            return Response({'error': 'order_id manquant'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.filter(id=order_id).first()
            if not order:
                return Response({'error': 'Commande introuvable'}, status=status.HTTP_404_NOT_FOUND)

            metadata = order.metadata or {}
            pay_token = metadata.get('orange_money_pay_token')
            if not pay_token:
                return Response({'error': 'pay_token manquant'}, status=status.HTTP_400_BAD_REQUEST)

            amount_cents = orange_money_service.format_amount(float(order.total))
            success, status_data = orange_money_service.check_transaction_status(
                order.order_number,
                amount_cents,
                pay_token
            )

            if not success:
                return Response({'status': 'pending', 'message': status_data.get('error', 'Paiement non confirmé')}, status=status.HTTP_200_OK)

            if status_data.get('status') == 'SUCCESS' or status_data.get('handled_status') is True:
                if not order.is_paid:
                    order.mark_as_paid()
                    # Synchroniser vers B2B après paiement réussi
                    self._sync_order_to_b2b(order)
                
                # Vérifier si toutes les commandes du panier sont payées avant de vider
                user_orders_pending = Order.objects.filter(
                    user=order.user,
                    status=Order.PENDING,
                    is_paid=False
                ).exclude(id=order.id)
                
                # Si c'est la dernière commande en attente, vider le panier
                if not user_orders_pending.exists():
                    self._clear_user_cart(order.user)
                
                return Response({
                    'status': 'success',
                    'message': 'Paiement Orange Money confirmé, panier vidé',
                    'order_id': order.id
                })

            return Response({'status': 'pending', 'message': status_data.get('status_message', 'Paiement en attente')}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Orange Money return error: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='orange-money-cancel', permission_classes=[AllowAny])
    def orange_money_cancel(self, request):
        accept = (request.META.get('HTTP_ACCEPT') or '').lower()
        if request.GET.get('mobile') == '1' or 'text/html' in accept:
            return render(request, 'payment_cancel.html', status=200)
        return Response({'status': 'cancelled', 'message': 'Paiement Orange Money annulé'})

    @action(detail=False, methods=['post'], url_path='orange-money-webhook', permission_classes=[AllowAny])
    def orange_money_webhook(self, request):
        try:
            notification_data = request.data or {}
            status_value = notification_data.get('status')
            notif_token = notification_data.get('notif_token')

            if not status_value or not notif_token:
                return Response({'error': 'Notification invalide'}, status=status.HTTP_400_BAD_REQUEST)

            if status_value not in ['SUCCESS', 'FAILED', 'PENDING', 'EXPIRED', 'INITIATED']:
                return Response({'error': 'Statut invalide'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'status': 'ok'})
        except Exception as e:
            logger.error(f"Orange Money webhook error: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)