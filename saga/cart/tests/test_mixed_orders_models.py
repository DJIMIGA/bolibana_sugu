from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal

from cart.models import Cart, CartItem, Order, OrderItem
from product.models import Product, Category
from accounts.models import ShippingAddress

User = get_user_model()


class MixedOrderModelsTestCase(TestCase):
    """Tests pour les modèles de commandes mixtes"""
    
    def setUp(self):
        """Configuration initiale"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.category_salam = Category.objects.create(name='Salam', slug='salam')
        self.category_classic = Category.objects.create(name='Classic', slug='classic')
        
        self.product_salam = Product.objects.create(
            title='Produit Salam',
            slug='produit-salam',
            price=Decimal('100000'),
            category=self.category_salam,
            is_salam=True,
            stock=10
        )
        
        self.product_classic = Product.objects.create(
            title='Produit Classique',
            slug='produit-classique',
            price=Decimal('5000'),
            category=self.category_classic,
            is_salam=False,
            stock=20
        )
        
        self.shipping_address = ShippingAddress.objects.create(
            user=self.user,
            full_name='Test User',
            quarter='Test Quarter',
            street_address='123 Test',
            city='BKO',
            is_default=True
        )
    
    def test_cart_mixed_items(self):
        """Test de création d'un panier avec items mixtes"""
        cart = Cart.objects.create(user=self.user)
        
        # Ajouter des items mixtes
        CartItem.objects.create(
            cart=cart,
            product=self.product_salam,
            quantity=1
        )
        CartItem.objects.create(
            cart=cart,
            product=self.product_classic,
            quantity=2
        )
        
        # Vérifier les items
        self.assertEqual(cart.cart_items.count(), 2)
        
        # Vérifier les totaux
        salam_items = cart.cart_items.filter(product__is_salam=True)
        classic_items = cart.cart_items.filter(product__is_salam=False)
        
        self.assertEqual(salam_items.count(), 1)
        self.assertEqual(classic_items.count(), 1)
        
        # Vérifier les prix
        salam_total = sum(item.get_total_price() for item in salam_items)
        classic_total = sum(item.get_total_price() for item in classic_items)
        
        self.assertEqual(salam_total, Decimal('100000'))
        self.assertEqual(classic_total, Decimal('10000'))  # 2 * 5000
    
    def test_order_mixed_items(self):
        """Test de création d'une commande avec items mixtes"""
        # Créer une commande Salam
        salam_order = Order.objects.create(
            user=self.user,
            shipping_address=self.shipping_address,
            payment_method='online_payment',
            subtotal=Decimal('100000'),
            shipping_cost=Decimal('1000'),
            total=Decimal('101000')
        )
        
        # Créer une commande Classique
        classic_order = Order.objects.create(
            user=self.user,
            shipping_address=self.shipping_address,
            payment_method='cash_on_delivery',
            subtotal=Decimal('10000'),
            shipping_cost=Decimal('1000'),
            total=Decimal('11000')
        )
        
        # Ajouter les items
        OrderItem.objects.create(
            order=salam_order,
            product=self.product_salam,
            quantity=1,
            price=Decimal('100000')
        )
        
        OrderItem.objects.create(
            order=classic_order,
            product=self.product_classic,
            quantity=2,
            price=Decimal('5000')
        )
        
        # Vérifier les commandes
        self.assertEqual(salam_order.items.count(), 1)
        self.assertEqual(classic_order.items.count(), 1)
        
        # Vérifier les totaux
        self.assertEqual(salam_order.subtotal, Decimal('100000'))
        self.assertEqual(classic_order.subtotal, Decimal('10000'))
        
        # Vérifier les méthodes de paiement
        self.assertEqual(salam_order.payment_method, 'online_payment')
        self.assertEqual(classic_order.payment_method, 'cash_on_delivery')
    
    def test_order_status_management(self):
        """Test de gestion des statuts de commande"""
        # Créer une commande Salam
        salam_order = Order.objects.create(
            user=self.user,
            shipping_address=self.shipping_address,
            payment_method='online_payment',
            subtotal=Decimal('100000'),
            shipping_cost=Decimal('1000'),
            total=Decimal('101000')
        )
        
        # Créer une commande Classique
        classic_order = Order.objects.create(
            user=self.user,
            shipping_address=self.shipping_address,
            payment_method='cash_on_delivery',
            subtotal=Decimal('10000'),
            shipping_cost=Decimal('1000'),
            total=Decimal('11000')
        )
        
        # Vérifier les statuts initiaux
        self.assertEqual(salam_order.status, Order.DRAFT)
        self.assertEqual(classic_order.status, Order.DRAFT)
        
        # Marquer la commande Salam comme payée
        salam_order.is_paid = True
        salam_order.save()
        
        # Vérifier que le statut a changé
        salam_order.refresh_from_db()
        self.assertTrue(salam_order.is_paid)
    
    def test_order_item_calculations(self):
        """Test des calculs des items de commande"""
        # Créer une commande
        order = Order.objects.create(
            user=self.user,
            shipping_address=self.shipping_address,
            payment_method='online_payment',
            subtotal=Decimal('0'),
            shipping_cost=Decimal('1000'),
            total=Decimal('1000')
        )
        
        # Ajouter des items
        item1 = OrderItem.objects.create(
            order=order,
            product=self.product_salam,
            quantity=1,
            price=Decimal('100000')
        )
        
        item2 = OrderItem.objects.create(
            order=order,
            product=self.product_classic,
            quantity=3,
            price=Decimal('5000')
        )
        
        # Vérifier les calculs
        self.assertEqual(item1.get_total_price(), Decimal('100000'))
        self.assertEqual(item2.get_total_price(), Decimal('15000'))
        
        # Vérifier le total de la commande
        total_items = sum(item.get_total_price() for item in order.items.all())
        self.assertEqual(total_items, Decimal('115000'))
    
    def test_cart_item_validation(self):
        """Test de validation des items du panier"""
        cart = Cart.objects.create(user=self.user)
        
        # Test avec quantité valide
        item = CartItem.objects.create(
            cart=cart,
            product=self.product_classic,
            quantity=5
        )
        self.assertEqual(item.quantity, 5)
        
        # Test avec quantité de 1 (minimum valide)
        item2 = CartItem.objects.create(
            cart=cart,
            product=self.product_salam,
            quantity=1
        )
        self.assertEqual(item2.quantity, 1)
        
        # Vérifier que les items ont été créés
        self.assertEqual(cart.cart_items.count(), 2)
    
    def test_order_relationships(self):
        """Test des relations entre les modèles"""
        # Créer une commande
        order = Order.objects.create(
            user=self.user,
            shipping_address=self.shipping_address,
            payment_method='online_payment',
            subtotal=Decimal('100000'),
            shipping_cost=Decimal('1000'),
            total=Decimal('101000')
        )
        
        # Ajouter un item
        item = OrderItem.objects.create(
            order=order,
            product=self.product_salam,
            quantity=1,
            price=Decimal('100000')
        )
        
        # Vérifier les relations
        self.assertEqual(item.order, order)
        self.assertEqual(item.product, self.product_salam)
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.shipping_address, self.shipping_address)
        
        # Vérifier les relations inverses
        self.assertIn(item, order.items.all())
        self.assertIn(order, self.user.orders.all()) 