from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Cart, CartItem, Order, OrderItem
from product.models import Product, Color, Size, ShippingMethod
from accounts.models import ShippingAddress
from decimal import Decimal
from django.utils import timezone


class CartService:
    """Service pour gérer la logique métier du panier"""

    @staticmethod
    def _is_weighted_product(product):
        specs = product.specifications or {}
        sold_by_weight = specs.get('sold_by_weight')
        is_sold_by_weight = sold_by_weight is True or (
            isinstance(sold_by_weight, str) and sold_by_weight.lower() in ['true', '1', 'yes']
        )
        unit_raw = specs.get('weight_unit') or specs.get('unit_display') or specs.get('unit_type')
        unit = str(unit_raw).lower() if unit_raw is not None else ''
        normalized_unit = unit.replace(' ', '')
        has_weight_fields = (
            specs.get('available_weight_g') is not None
            or specs.get('available_weight_kg') is not None
            or specs.get('price_per_g') is not None
            or specs.get('price_per_kg') is not None
            or specs.get('discount_price_per_g') is not None
            or specs.get('discount_price_per_kg') is not None
        )
        return (
            is_sold_by_weight
            or unit in ['weight', 'kg', 'kilogram', 'g', 'gram', 'gramme', 'grams', 'grammes', 'gr', 'gms', 'gm']
            or ('kg' in normalized_unit)
            or (normalized_unit.endswith('g') and normalized_unit != 'kg')
            or has_weight_fields
        )

    @staticmethod
    def _get_weight_unit(product):
        specs = product.specifications or {}
        unit_raw = specs.get('weight_unit') or specs.get('unit_display') or specs.get('unit_type')
        if not unit_raw:
            if specs.get('available_weight_g') is not None or specs.get('price_per_g') is not None or specs.get('discount_price_per_g') is not None:
                return 'g'
            return 'kg'
        unit = str(unit_raw).lower()
        normalized_unit = unit.replace(' ', '')
        if unit in ['weight', 'kg', 'kilogram']:
            return 'kg'
        if unit in ['g', 'gram', 'gramme', 'grams', 'grammes', 'gr', 'gms', 'gm']:
            return 'g'
        if 'kg' in normalized_unit:
            return 'kg'
        if normalized_unit.endswith('g'):
            return 'g'
        return unit

    @staticmethod
    def _get_available_weight(product):
        specs = product.specifications or {}
        unit = CartService._get_weight_unit(product)
        if unit == 'g':
            available_g = specs.get('available_weight_g')
            if available_g is not None:
                return Decimal(str(available_g))
            available_kg = specs.get('available_weight_kg')
            if available_kg is not None:
                return Decimal(str(available_kg)) * Decimal('1000')
            return Decimal('0')
        available_kg = specs.get('available_weight_kg')
        if available_kg is not None:
            return Decimal(str(available_kg))
        available_g = specs.get('available_weight_g')
        if available_g is not None:
            return Decimal(str(available_g)) / Decimal('1000')
        return Decimal('0')
    
    @staticmethod
    def add_to_cart(cart, product, quantity=1):
        """
        Ajoute un produit au panier
        
        Args:
            cart: Instance du panier
            product: Produit à ajouter
            quantity: Quantité à ajouter
        
        Returns:
            tuple: (success, message)
        """
        try:
            with transaction.atomic():
                # Vérifier la disponibilité du produit
                if not product.is_available:
                    return False, "Ce produit n'est plus disponible"
                
                # Pour les produits classiques, vérifier le stock
                if not product.is_salam:
                    if CartService._is_weighted_product(product):
                        unit = CartService._get_weight_unit(product)
                        available_weight = CartService._get_available_weight(product)
                        if Decimal(str(quantity)) > available_weight:
                            return False, f"Stock insuffisant. Disponible: {available_weight} {unit}"
                    elif not product.can_order(quantity):
                        return False, f"Stock insuffisant. Il ne reste que {product.stock} unité(s) disponible(s)"
                
                # Chercher un item existant avec le même produit
                existing_item = cart.cart_items.filter(product=product).first()
                
                if existing_item:
                    # Mettre à jour la quantité
                    new_quantity = existing_item.quantity + quantity
                    
                    # Vérifier le stock pour les produits classiques
                    if not product.is_salam:
                        if CartService._is_weighted_product(product):
                            unit = CartService._get_weight_unit(product)
                            available_weight = CartService._get_available_weight(product)
                            if Decimal(str(new_quantity)) > available_weight:
                                return False, f"Stock insuffisant. Disponible: {available_weight} {unit}"
                        elif not product.can_order(new_quantity):
                            return False, f"Quantité totale ({new_quantity}) dépasse le stock disponible ({product.stock})"
                    
                    existing_item.quantity = new_quantity
                    existing_item.save()
                    
                    message = f"Quantité mise à jour pour {product.title}"
                else:
                    # Créer un nouvel item
                    cart_item = CartItem.objects.create(
                        cart=cart,
                        product=product,
                        quantity=quantity
                    )
                    
                    # Si c'est un vêtement, copier les couleurs et tailles du produit
                    if hasattr(product, 'clothing_product') and product.clothing_product:
                        clothing = product.clothing_product
                        if clothing.color.exists():
                            cart_item.colors.set(clothing.color.all())
                        if clothing.size.exists():
                            cart_item.sizes.set(clothing.size.all())
                    
                    message = f"{product.title} ajouté au panier"
                
                return True, message
                
        except Exception as e:
            return False, f"Erreur lors de l'ajout au panier: {str(e)}"
    
    @staticmethod
    def update_quantity(cart_item, new_quantity):
        """
        Met à jour la quantité d'un item du panier
        
        Args:
            cart_item: Item du panier à mettre à jour
            new_quantity: Nouvelle quantité
        
        Returns:
            tuple: (success, message)
        """
        try:
            with transaction.atomic():
                product = cart_item.product
                
                # Vérifier que la quantité est positive
                if new_quantity <= 0:
                    cart_item.delete()
                    return True, "Article supprimé du panier"
                
                # Pour les produits classiques, vérifier le stock
                if not product.is_salam:
                    if CartService._is_weighted_product(product):
                        unit = CartService._get_weight_unit(product)
                        available_weight = CartService._get_available_weight(product)
                        if Decimal(str(new_quantity)) > available_weight:
                            return False, f"Stock insuffisant. Disponible: {available_weight} {unit}"
                    elif not product.can_order(new_quantity):
                        return False, f"Stock insuffisant. Il ne reste que {product.stock} unité(s) disponible(s)"
                
                cart_item.quantity = new_quantity
                cart_item.save()
                
                return True, "Quantité mise à jour"
                
        except Exception as e:
            return False, f"Erreur lors de la mise à jour: {str(e)}"
    
    @staticmethod
    def validate_cart_for_checkout(cart, product_type='all'):
        """
        Valide le panier avant le passage de commande
        
        Args:
            cart: Instance du panier
            product_type: Type de produits à valider ('classic', 'salam', 'all', 'mixed')
        
        Returns:
            tuple: (success, errors)
        """
        errors = []
        
        if not cart.cart_items.exists():
            errors.append("Le panier est vide")
            return False, errors
        
        # Filtrer les items selon le type
        if product_type == 'classic':
            items_to_validate = cart.cart_items.filter(product__is_salam=False)
        elif product_type == 'salam':
            items_to_validate = cart.cart_items.filter(product__is_salam=True)
        elif product_type == 'mixed':
            # Pour les commandes mixtes, valider tous les items
            items_to_validate = cart.cart_items.all()
        else:
            items_to_validate = cart.cart_items.all()
        
        if not items_to_validate.exists():
            if product_type == 'classic':
                errors.append("Aucun produit classique dans le panier")
            elif product_type == 'salam':
                errors.append("Aucun produit Salam dans le panier")
            elif product_type == 'mixed':
                errors.append("Aucun produit dans le panier")
            return False, errors
        
        for item in items_to_validate:
            product = item.product
            
            # Vérifier que le produit est toujours disponible
            if not product.is_available:
                errors.append(f"Le produit '{product.title}' n'est plus disponible")
                continue
            
            # Pour les produits classiques, vérifier le stock
            if not product.is_salam:
                if CartService._is_weighted_product(product):
                    unit = CartService._get_weight_unit(product)
                    available_weight = CartService._get_available_weight(product)
                    if Decimal(str(item.quantity)) > available_weight:
                        errors.append(
                            f"Stock insuffisant pour '{product.title}'. "
                            f"Disponible: {available_weight} {unit}"
                        )
                else:
                    # Vérifier d'abord si c'est peut-être un produit au poids mal détecté
                    # (double vérification pour éviter les faux négatifs)
                    specs = product.specifications or {}
                    has_weight_fields = (
                        specs.get('available_weight_g') is not None
                        or specs.get('available_weight_kg') is not None
                        or specs.get('price_per_g') is not None
                        or specs.get('price_per_kg') is not None
                    )
                    if has_weight_fields:
                        # C'est probablement un produit au poids, vérifier le poids disponible
                        unit = CartService._get_weight_unit(product)
                        available_weight = CartService._get_available_weight(product)
                        if Decimal(str(item.quantity)) > available_weight:
                            errors.append(
                                f"Stock insuffisant pour '{product.title}'. "
                                f"Disponible: {available_weight} {unit}"
                            )
                    else:
                        # Produit normal, vérifier le stock en unités
                        if not product.can_order(item.quantity):
                            errors.append(f"Stock insuffisant pour '{product.title}'. Il ne reste que {product.stock} unité(s) disponible(s)")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def is_mixed_cart(cart):
        """
        Vérifie si le panier contient des produits mixtes (Salam + Classiques)
        
        Args:
            cart: Instance du panier
        
        Returns:
            bool: True si le panier est mixte
        """
        salam_items = cart.cart_items.filter(product__is_salam=True)
        classic_items = cart.cart_items.filter(product__is_salam=False)
        
        return salam_items.exists() and classic_items.exists()
    
    @staticmethod
    def get_mixed_cart_summary(cart):
        """
        Retourne un résumé du panier mixte
        
        Args:
            cart: Instance du panier
        
        Returns:
            dict: Résumé du panier mixte
        """
        salam_items = cart.cart_items.filter(product__is_salam=True)
        classic_items = cart.cart_items.filter(product__is_salam=False)
        
        total_salam = sum(item.get_total_price() for item in salam_items)
        total_classic = sum(item.get_total_price() for item in classic_items)
        
        return {
            'salam_items': salam_items,
            'classic_items': classic_items,
            'total_salam': total_salam,
            'total_classic': total_classic,
            'total_combined': total_salam + total_classic,
            'salam_count': salam_items.count(),
            'classic_count': classic_items.count()
        }
    
    @staticmethod
    def check_stock_availability(cart, product_type='all'):
        """
        Vérifie la disponibilité du stock sans le réserver (uniquement pour les produits classiques)
        
        Args:
            cart: Instance du panier
            product_type: Type de produits à vérifier ('classic', 'salam', 'all', 'mixed')
        
        Returns:
            tuple: (success, errors)
        """
        errors = []
        
        try:
            # Filtrer les items selon le type
            if product_type == 'classic':
                items_to_check = cart.cart_items.filter(product__is_salam=False)
            elif product_type == 'salam':
                # Pour les produits Salam, pas de vérification de stock
                return True, []
            elif product_type == 'mixed':
                # Pour les commandes mixtes, vérifier seulement les classiques
                items_to_check = cart.cart_items.filter(product__is_salam=False)
            else:
                items_to_check = cart.cart_items.filter(product__is_salam=False)
            
            for item in items_to_check:
                product = item.product
                
                # Vérifier le stock uniquement pour les produits classiques
                if not product.is_salam:
                    if CartService._is_weighted_product(product):
                        unit = CartService._get_weight_unit(product)
                        available_weight = CartService._get_available_weight(product)
                        if Decimal(str(item.quantity)) > available_weight:
                            errors.append(
                                f"Stock insuffisant pour '{product.title}' "
                                f"(demandé: {item.quantity} {unit}, disponible: {available_weight} {unit})"
                            )
                    else:
                        if not product.can_order(item.quantity):
                            errors.append(f"Stock insuffisant pour '{product.title}' (demandé: {item.quantity}, disponible: {product.stock})")
            
            return len(errors) == 0, errors
                
        except Exception as e:
            return False, [f"Erreur lors de la vérification du stock: {str(e)}"]

    @staticmethod
    def reserve_stock_for_order(cart, product_type='all'):
        """
        Réserve le stock pour une commande (uniquement pour les produits classiques)
        
        Args:
            cart: Instance du panier
            product_type: Type de produits à réserver ('classic', 'salam', 'all', 'mixed')
        
        Returns:
            tuple: (success, errors)
        """
        errors = []
        
        try:
            with transaction.atomic():
                # Filtrer les items selon le type
                if product_type == 'classic':
                    items_to_reserve = cart.cart_items.filter(product__is_salam=False)
                elif product_type == 'salam':
                    # Pour les produits Salam, pas de réservation de stock
                    return True, []
                elif product_type == 'mixed':
                    # Pour les commandes mixtes, réserver seulement les classiques
                    items_to_reserve = cart.cart_items.filter(product__is_salam=False)
                else:
                    items_to_reserve = cart.cart_items.filter(product__is_salam=False)
                
                for item in items_to_reserve:
                    product = item.product
                    
                    # Réserver le stock uniquement pour les produits classiques
                    if not product.is_salam:
                        if not product.reserve_stock(item.quantity):
                            errors.append(f"Impossible de réserver le stock pour '{product.title}'")
                
                if errors:
                    # Annuler la transaction si il y a des erreurs
                    raise ValidationError("Erreur de réservation de stock")
                
                return True, []
                
        except Exception as e:
            return False, [f"Erreur lors de la réservation: {str(e)}"]
    
    @staticmethod
    def release_stock_for_order(cart, product_type='all'):
        """
        Libère le stock réservé pour une commande (uniquement pour les produits classiques)
        
        Args:
            cart: Instance du panier
            product_type: Type de produits à libérer ('classic', 'salam', 'all', 'mixed')
        """
        try:
            with transaction.atomic():
                # Filtrer les items selon le type
                if product_type == 'classic':
                    items_to_release = cart.cart_items.filter(product__is_salam=False)
                elif product_type == 'salam':
                    # Pour les produits Salam, pas de libération de stock
                    return
                elif product_type == 'mixed':
                    # Pour les commandes mixtes, libérer seulement les classiques
                    items_to_release = cart.cart_items.filter(product__is_salam=False)
                else:
                    items_to_release = cart.cart_items.filter(product__is_salam=False)
                
                for item in items_to_release:
                    product = item.product
                    
                    # Libérer le stock uniquement pour les produits classiques
                    if not product.is_salam:
                        product.release_stock(item.quantity)
                        
        except Exception as e:
            print(f"Erreur lors de la libération du stock: {str(e)}")
    
    @staticmethod
    def create_mixed_orders(cart, user, shipping_address, shipping_method, classic_payment_choice='delivery'):
        """
        Crée les commandes pour un panier mixte
        
        Args:
            cart: Instance du panier
            user: Utilisateur
            shipping_address: Adresse de livraison
            shipping_method: Méthode de livraison
            classic_payment_choice: Choix de paiement pour les classiques ('immediate' ou 'delivery')
        
        Returns:
            dict: Commandes créées
        """
        try:
            with transaction.atomic():
                summary = CartService.get_mixed_cart_summary(cart)
                
                # Vérifier qu'il y a des produits Salam et classiques
                if not summary['salam_items'].exists():
                    raise ValidationError("Aucun produit Salam dans le panier")
                if not summary['classic_items'].exists():
                    raise ValidationError("Aucun produit classique dans le panier")
                
                # Créer la commande Salam (paiement immédiat obligatoire)
                salam_order = Order.objects.create(
                    user=user,
                    shipping_address=shipping_address,
                    shipping_method=shipping_method,
                    payment_method='online_payment',  # Paiement immédiat
                    subtotal=summary['total_salam'],
                    shipping_cost=shipping_method.price,
                    total=summary['total_salam'] + shipping_method.price,
                    is_paid=False,  # Sera payé via Stripe
                    status=Order.PENDING
                )
                
                # Créer les éléments de la commande Salam
                for item in summary['salam_items']:
                    OrderItem.objects.create(
                        order=salam_order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.discount_price if hasattr(item.product, 'discount_price') and item.product.discount_price else item.product.price
                    )
                
                # Créer la commande Classique
                classic_payment_method = 'online_payment' if classic_payment_choice == 'immediate' else 'cash_on_delivery'
                classic_is_paid = classic_payment_choice == 'immediate'
                
                classic_order = Order.objects.create(
                    user=user,
                    shipping_address=shipping_address,
                    shipping_method=shipping_method,
                    payment_method=classic_payment_method,
                    subtotal=summary['total_classic'],
                    shipping_cost=shipping_method.price,
                    total=summary['total_classic'] + shipping_method.price,
                    is_paid=classic_is_paid,
                    status=Order.PENDING
                )
                
                # Créer les éléments de la commande Classique
                for item in summary['classic_items']:
                    order_item = OrderItem.objects.create(
                        order=classic_order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.discount_price if hasattr(item.product, 'discount_price') and item.product.discount_price else item.product.price
                    )
                    
                    # Ajouter les couleurs et tailles si présentes
                    if item.colors.exists():
                        order_item.colors.set(item.colors.all())
                    if item.sizes.exists():
                        order_item.sizes.set(item.sizes.all())
                
                # Vérifier que les commandes ont été créées
                if not salam_order or not classic_order:
                    raise ValidationError("Erreur lors de la création des commandes")
                
                return {
                    'salam_order': salam_order,
                    'classic_order': classic_order,
                    'summary': summary
                }
                
        except Exception as e:
            # Libérer le stock réservé en cas d'erreur
            CartService.release_stock_for_order(cart, 'mixed')
            raise ValidationError(f"Erreur lors de la création des commandes mixtes: {str(e)}")
    
    @staticmethod
    def get_cart_summary(cart):
        """
        Retourne un résumé du panier
        
        Args:
            cart: Instance du panier
        
        Returns:
            dict: Résumé du panier
        """
        items = cart.cart_items.all()
        total = sum(item.get_total_price() for item in items)
        
        return {
            'items': items,
            'total': total,
            'item_count': items.count(),
            'is_mixed': CartService.is_mixed_cart(cart)
        } 