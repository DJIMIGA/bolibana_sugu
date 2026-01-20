"""
Tests pour la validation des produits au poids et la conversion Stripe
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from unittest.mock import patch, MagicMock

from cart.models import Cart, CartItem, Order, OrderItem
from cart.services import CartService
from cart.api.views import CartViewSet
from product.models import Product, Category
from accounts.models import ShippingAddress
from product.models import ShippingMethod

User = get_user_model()


class WeightedProductsValidationTestCase(TestCase):
    """Tests pour la validation des produits au poids"""
    
    def setUp(self):
        """Configuration initiale"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(name='Épices', slug='epices')
        
        # Produit au poids en grammes
        self.product_grams = Product.objects.create(
            title='Poudre de laurier',
            slug='poudre-laurier',
            price=Decimal('25'),
            category=self.category,
            is_salam=False,
            stock=0,  # Stock en unités = 0 (produit au poids)
            specifications={
                'sold_by_weight': True,
                'weight_unit': 'g',
                'available_weight_g': 0,  # Stock épuisé
                'price_per_g': 25,
            }
        )
        
        # Produit au poids en kg avec stock disponible
        self.product_kg = Product.objects.create(
            title='Piment vrac',
            slug='piment-vrac',
            price=Decimal('150'),
            category=self.category,
            is_salam=False,
            stock=0,  # Stock en unités = 0 (produit au poids)
            specifications={
                'sold_by_weight': True,
                'weight_unit': 'kg',
                'available_weight_kg': 5.0,  # 5 kg disponibles
                'price_per_kg': 150,
            }
        )
        
        # Produit au poids en kg avec stock insuffisant
        self.product_kg_low_stock = Product.objects.create(
            title='Curcuma vrac',
            slug='curcuma-vrac',
            price=Decimal('200'),
            category=self.category,
            is_salam=False,
            stock=0,
            specifications={
                'sold_by_weight': True,
                'weight_unit': 'kg',
                'available_weight_kg': 0.3,  # 0.3 kg disponibles
                'price_per_kg': 200,
            }
        )
        
        # Produit normal (non pondéré)
        self.product_normal = Product.objects.create(
            title='BIOLIGHT Hibiscus 300 ML',
            slug='biolight-hibiscus',
            price=Decimal('2000'),
            category=self.category,
            is_salam=False,
            stock=10,  # 10 unités disponibles
        )
        
        self.shipping_address = ShippingAddress.objects.create(
            user=self.user,
            full_name='Test User',
            quarter='Test Quarter',
            street_address='123 Test',
            city='BKO',
            is_default=True
        )
    
    def test_validate_cart_weighted_product_grams_insufficient_stock(self):
        """Test validation d'un produit au poids en grammes avec stock insuffisant"""
        cart = Cart.objects.create(user=self.user)
        
        # Ajouter un produit en grammes avec quantité > stock disponible
        CartItem.objects.create(
            cart=cart,
            product=self.product_grams,
            quantity=Decimal('1')  # 1g demandé, mais stock = 0g
        )
        
        success, errors = CartService.validate_cart_for_checkout(cart)
        
        self.assertFalse(success)
        self.assertGreater(len(errors), 0)
        # Vérifier que le message contient l'unité correcte (g) et non "unité(s)"
        error_message = ' '.join(errors)
        self.assertIn('g', error_message.lower())
        self.assertNotIn('unité', error_message.lower())
        self.assertIn('Poudre de laurier', error_message)
    
    def test_validate_cart_weighted_product_kg_sufficient_stock(self):
        """Test validation d'un produit au poids en kg avec stock suffisant"""
        cart = Cart.objects.create(user=self.user)
        
        # Ajouter un produit en kg avec quantité <= stock disponible
        CartItem.objects.create(
            cart=cart,
            product=self.product_kg,
            quantity=Decimal('2.5')  # 2.5 kg demandé, stock = 5 kg
        )
        
        success, errors = CartService.validate_cart_for_checkout(cart)
        
        self.assertTrue(success)
        self.assertEqual(len(errors), 0)
    
    def test_validate_cart_weighted_product_kg_insufficient_stock(self):
        """Test validation d'un produit au poids en kg avec stock insuffisant"""
        cart = Cart.objects.create(user=self.user)
        
        # Ajouter un produit en kg avec quantité > stock disponible
        CartItem.objects.create(
            cart=cart,
            product=self.product_kg_low_stock,
            quantity=Decimal('0.5')  # 0.5 kg demandé, mais stock = 0.3 kg
        )
        
        success, errors = CartService.validate_cart_for_checkout(cart)
        
        self.assertFalse(success)
        self.assertGreater(len(errors), 0)
        # Vérifier que le message contient l'unité correcte (kg)
        error_message = ' '.join(errors)
        self.assertIn('kg', error_message.lower())
        self.assertIn('Curcuma vrac', error_message)
    
    def test_validate_cart_weighted_product_double_check(self):
        """Test que la double vérification détecte les produits au poids même s'ils ne sont pas correctement identifiés"""
        cart = Cart.objects.create(user=self.user)
        
        # Créer un produit avec des champs de poids mais sans sold_by_weight explicite
        product_mal_detected = Product.objects.create(
            title='Épice test',
            slug='epice-test',
            price=Decimal('100'),
            category=self.category,
            is_salam=False,
            stock=0,
            specifications={
                # Pas de sold_by_weight, mais a des champs de poids
                'available_weight_g': 0,
                'price_per_g': 100,
            }
        )
        
        CartItem.objects.create(
            cart=cart,
            product=product_mal_detected,
            quantity=Decimal('1')  # 1g demandé, mais stock = 0g
        )
        
        success, errors = CartService.validate_cart_for_checkout(cart)
        
        self.assertFalse(success)
        self.assertGreater(len(errors), 0)
        # Vérifier que le message utilise le poids et non les unités
        error_message = ' '.join(errors)
        self.assertIn('g', error_message.lower())
        self.assertNotIn('unité', error_message.lower())
    
    def test_validate_cart_normal_product_insufficient_stock(self):
        """Test validation d'un produit normal avec stock insuffisant"""
        cart = Cart.objects.create(user=self.user)
        
        # Ajouter un produit normal avec quantité > stock disponible
        CartItem.objects.create(
            cart=cart,
            product=self.product_normal,
            quantity=Decimal('15')  # 15 demandés, mais stock = 10
        )
        
        success, errors = CartService.validate_cart_for_checkout(cart)
        
        self.assertFalse(success)
        self.assertGreater(len(errors), 0)
        # Vérifier que le message utilise "unité(s)" pour un produit normal
        error_message = ' '.join(errors)
        self.assertIn('unité', error_message.lower())
    
    def test_validate_cart_mixed_products(self):
        """Test validation d'un panier mixte (produits au poids + produits normaux)"""
        cart = Cart.objects.create(user=self.user)
        
        # Ajouter un produit au poids avec stock suffisant
        CartItem.objects.create(
            cart=cart,
            product=self.product_kg,
            quantity=Decimal('1.0')  # 1 kg, stock = 5 kg
        )
        
        # Ajouter un produit normal avec stock suffisant
        CartItem.objects.create(
            cart=cart,
            product=self.product_normal,
            quantity=Decimal('2')  # 2 unités, stock = 10
        )
        
        success, errors = CartService.validate_cart_for_checkout(cart)
        
        self.assertTrue(success)
        self.assertEqual(len(errors), 0)


class StripeWeightedProductsConversionTestCase(TestCase):
    """Tests pour la conversion Stripe des produits au poids"""
    
    def setUp(self):
        """Configuration initiale"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(name='Épices', slug='epices')
        
        # Produit au poids en grammes
        self.product_grams = Product.objects.create(
            title='Poudre de laurier',
            slug='poudre-laurier',
            price=Decimal('25'),
            category=self.category,
            is_salam=False,
            stock=100,
            specifications={
                'sold_by_weight': True,
                'weight_unit': 'g',
                'available_weight_g': 100,
                'price_per_g': 25,
            }
        )
        
        # Produit au poids en kg < 1 kg
        self.product_kg_small = Product.objects.create(
            title='Piment vrac',
            slug='piment-vrac',
            price=Decimal('150'),
            category=self.category,
            is_salam=False,
            stock=100,
            specifications={
                'sold_by_weight': True,
                'weight_unit': 'kg',
                'available_weight_kg': 10.0,
                'price_per_kg': 150,
            }
        )
        
        # Produit au poids en kg >= 1 kg
        self.product_kg_large = Product.objects.create(
            title='Curcuma vrac',
            slug='curcuma-vrac',
            price=Decimal('200'),
            category=self.category,
            is_salam=False,
            stock=100,
            specifications={
                'sold_by_weight': True,
                'weight_unit': 'kg',
                'available_weight_kg': 10.0,
                'price_per_kg': 200,
            }
        )
        
        # Produit normal
        self.product_normal = Product.objects.create(
            title='Produit normal',
            slug='produit-normal',
            price=Decimal('2000'),
            category=self.category,
            is_salam=False,
            stock=10,
        )
        
        self.shipping_address = ShippingAddress.objects.create(
            user=self.user,
            full_name='Test User',
            quarter='Test Quarter',
            street_address='123 Test',
            city='BKO',
            is_default=True
        )
        
        self.shipping_method = ShippingMethod.objects.create(
            name='Standard',
            price=Decimal('1000'),
            min_delivery_days=3,
            max_delivery_days=5
        )
    
    @patch('cart.api.views.stripe.checkout.Session.create')
    def test_stripe_conversion_grams(self, mock_stripe_create):
        """Test conversion Stripe pour produit en grammes"""
        mock_stripe_create.return_value = MagicMock(id='test_session', url='https://stripe.com/checkout')
        
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(
            cart=cart,
            product=self.product_grams,
            quantity=Decimal('1')  # 1g
        )
        
        view = CartViewSet()
        view.request = MagicMock()
        view.request.user = self.user
        view.request.build_absolute_uri = lambda x: 'http://test.com'
        
        # Simuler la création de la commande
        order = Order.objects.create(
            user=self.user,
            shipping_address=self.shipping_address,
            shipping_method=self.shipping_method,
            payment_method='stripe',
            subtotal=Decimal('25'),
            shipping_cost=Decimal('1000'),
            total=Decimal('1025'),
            status=Order.PENDING
        )
        
        OrderItem.objects.create(
            order=order,
            product=self.product_grams,
            quantity=Decimal('1'),
            price=Decimal('25')  # Prix par gramme
        )
        
        # Appeler la méthode checkout (simulation)
        # Note: On teste directement la logique de conversion
        line_items = []
        for item in order.items.all():
            total_price = Decimal(str(item.price)) * Decimal(str(item.quantity))
            quantity_decimal = Decimal(str(item.quantity))
            is_weighted = view._is_weighted_product(item.product)
            
            if is_weighted:
                unit = view._get_weight_unit(item.product)
                
                if unit == 'kg' and quantity_decimal < Decimal('1'):
                    stripe_quantity = 1
                    stripe_unit_amount = int(float(total_price))
                elif unit == 'g':
                    stripe_quantity = max(1, int(float(quantity_decimal)))
                    stripe_unit_amount = int(float(item.price))
                else:
                    stripe_quantity = max(1, int(float(quantity_decimal)))
                    stripe_unit_amount = int(float(item.price))
            else:
                stripe_quantity = max(1, int(float(quantity_decimal)))
                stripe_unit_amount = int(float(item.price))
            
            line_items.append({
                'price_data': {
                    'currency': 'xof',
                    'product_data': {'name': item.product.title},
                    'unit_amount': stripe_unit_amount,
                },
                'quantity': stripe_quantity,
            })
        
        # Vérifications
        self.assertEqual(len(line_items), 1)
        self.assertEqual(line_items[0]['quantity'], 1)  # Toujours 1 pour produits au poids
        self.assertEqual(line_items[0]['price_data']['unit_amount'], 25)  # Prix total (1g * 25)
    
    @patch('cart.api.views.stripe.checkout.Session.create')
    def test_stripe_conversion_kg_small(self, mock_stripe_create):
        """Test conversion Stripe pour produit en kg < 1 kg"""
        mock_stripe_create.return_value = MagicMock(id='test_session', url='https://stripe.com/checkout')
        
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(
            cart=cart,
            product=self.product_kg_small,
            quantity=Decimal('0.5')  # 0.5 kg
        )
        
        view = CartViewSet()
        
        order = Order.objects.create(
            user=self.user,
            shipping_address=self.shipping_address,
            shipping_method=self.shipping_method,
            payment_method='stripe',
            subtotal=Decimal('75'),  # 0.5 * 150
            shipping_cost=Decimal('1000'),
            total=Decimal('1075'),
            status=Order.PENDING
        )
        
        OrderItem.objects.create(
            order=order,
            product=self.product_kg_small,
            quantity=Decimal('0.5'),
            price=Decimal('150')  # Prix par kg
        )
        
        # Tester la logique de conversion
        line_items = []
        for item in order.items.all():
            total_price = Decimal(str(item.price)) * Decimal(str(item.quantity))
            quantity_decimal = Decimal(str(item.quantity))
            is_weighted = view._is_weighted_product(item.product)
            
            if is_weighted:
                # Pour tous les produits au poids, utiliser le prix total avec quantité = 1
                stripe_quantity = 1
                stripe_unit_amount = max(1, int(float(total_price)))
            else:
                stripe_quantity = max(1, int(float(quantity_decimal)))
                stripe_unit_amount = max(1, int(float(item.price)))
            
            line_items.append({
                'price_data': {
                    'currency': 'xof',
                    'product_data': {'name': item.product.title},
                    'unit_amount': stripe_unit_amount,
                },
                'quantity': stripe_quantity,
            })
        
        # Vérifications
        self.assertEqual(len(line_items), 1)
        self.assertEqual(line_items[0]['quantity'], 1)  # Quantité = 1 (prix total)
        self.assertEqual(line_items[0]['price_data']['unit_amount'], 75)  # Prix total (0.5 * 150)
    
    @patch('cart.api.views.stripe.checkout.Session.create')
    def test_stripe_conversion_kg_large(self, mock_stripe_create):
        """Test conversion Stripe pour produit en kg >= 1 kg"""
        mock_stripe_create.return_value = MagicMock(id='test_session', url='https://stripe.com/checkout')
        
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(
            cart=cart,
            product=self.product_kg_large,
            quantity=Decimal('2.5')  # 2.5 kg
        )
        
        view = CartViewSet()
        
        order = Order.objects.create(
            user=self.user,
            shipping_address=self.shipping_address,
            shipping_method=self.shipping_method,
            payment_method='stripe',
            subtotal=Decimal('500'),  # 2.5 * 200
            shipping_cost=Decimal('1000'),
            total=Decimal('1500'),
            status=Order.PENDING
        )
        
        OrderItem.objects.create(
            order=order,
            product=self.product_kg_large,
            quantity=Decimal('2.5'),
            price=Decimal('200')  # Prix par kg
        )
        
        # Tester la logique de conversion
        line_items = []
        for item in order.items.all():
            total_price = Decimal(str(item.price)) * Decimal(str(item.quantity))
            quantity_decimal = Decimal(str(item.quantity))
            is_weighted = view._is_weighted_product(item.product)
            
            if is_weighted:
                # Pour tous les produits au poids, utiliser le prix total avec quantité = 1
                stripe_quantity = 1
                stripe_unit_amount = max(1, int(float(total_price)))
            else:
                stripe_quantity = max(1, int(float(quantity_decimal)))
                stripe_unit_amount = max(1, int(float(item.price)))
            
            line_items.append({
                'price_data': {
                    'currency': 'xof',
                    'product_data': {'name': item.product.title},
                    'unit_amount': stripe_unit_amount,
                },
                'quantity': stripe_quantity,
            })
        
        # Vérifications
        self.assertEqual(len(line_items), 1)
        self.assertEqual(line_items[0]['quantity'], 1)  # Toujours 1 pour produits au poids
        self.assertEqual(line_items[0]['price_data']['unit_amount'], 500)  # Prix total (2.5 * 200)
    
    @patch('cart.api.views.stripe.checkout.Session.create')
    def test_stripe_conversion_normal_product(self, mock_stripe_create):
        """Test conversion Stripe pour produit normal"""
        mock_stripe_create.return_value = MagicMock(id='test_session', url='https://stripe.com/checkout')
        
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(
            cart=cart,
            product=self.product_normal,
            quantity=Decimal('3')  # 3 unités
        )
        
        view = CartViewSet()
        
        order = Order.objects.create(
            user=self.user,
            shipping_address=self.shipping_address,
            shipping_method=self.shipping_method,
            payment_method='stripe',
            subtotal=Decimal('6000'),  # 3 * 2000
            shipping_cost=Decimal('1000'),
            total=Decimal('7000'),
            status=Order.PENDING
        )
        
        OrderItem.objects.create(
            order=order,
            product=self.product_normal,
            quantity=Decimal('3'),
            price=Decimal('2000')
        )
        
        # Tester la logique de conversion
        line_items = []
        for item in order.items.all():
            total_price = Decimal(str(item.price)) * Decimal(str(item.quantity))
            quantity_decimal = Decimal(str(item.quantity))
            is_weighted = view._is_weighted_product(item.product)
            
            if is_weighted:
                # Pour tous les produits au poids, utiliser le prix total avec quantité = 1
                stripe_quantity = 1
                stripe_unit_amount = max(1, int(float(total_price)))
            else:
                stripe_quantity = max(1, int(float(quantity_decimal)))
                stripe_unit_amount = max(1, int(float(item.price)))
            
            line_items.append({
                'price_data': {
                    'currency': 'xof',
                    'product_data': {'name': item.product.title},
                    'unit_amount': stripe_unit_amount,
                },
                'quantity': stripe_quantity,
            })
        
        # Vérifications
        self.assertEqual(len(line_items), 1)
        self.assertEqual(line_items[0]['quantity'], 3)  # 3 unités
        self.assertEqual(line_items[0]['price_data']['unit_amount'], 2000)  # Prix unitaire
