"""
Tests pour l'intégration Orange Money
"""

import json
from unittest.mock import patch, Mock
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings
from django.core.cache import cache
from cart.models import Cart, CartItem, Order, OrderItem
from accounts.models import ShippingAddress
from product.models import Product
from cart.orange_money_service import OrangeMoneyService

User = get_user_model()


class OrangeMoneyServiceTest(TestCase):
    """Tests pour le service Orange Money"""
    
    def setUp(self):
        """Configuration des tests"""
        self.service = OrangeMoneyService()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        # Configuration de test
        self.test_config = {
            'enabled': True,
            'merchant_key': 'test_merchant_key',
            'client_id': 'test_client_id',
            'client_secret': 'test_client_secret',
            'currency': 'OUV',
            'language': 'fr',
            'timeout': 30,
            'max_retries': 3,
            'token_url': 'https://api.orange.com/oauth/v3/token',
            'webpayment_url': 'https://api.orange.com/orange-money-webpay/dev/v1/webpayment',
            'status_url': 'https://api.orange.com/orange-money-webpay/dev/v1/transactionstatus',
            'payment_url': 'https://webpayment-qualif.orange-money.com'
        }
    
    def tearDown(self):
        """Nettoyage après les tests"""
        cache.clear()
    
    @patch('cart.orange_money_service.settings.ORANGE_MONEY_CONFIG')
    def test_is_enabled_true(self, mock_config):
        """Test que le service est activé avec une configuration valide"""
        mock_config.__getitem__.side_effect = lambda key: self.test_config[key]
        mock_config.get.side_effect = lambda key, default=None: self.test_config.get(key, default)
        
        self.assertTrue(self.service.is_enabled())
    
    @patch('cart.orange_money_service.settings.ORANGE_MONEY_CONFIG')
    def test_is_enabled_false_missing_credentials(self, mock_config):
        """Test que le service est désactivé avec des credentials manquants"""
        test_config = self.test_config.copy()
        test_config['merchant_key'] = ''
        mock_config.__getitem__.side_effect = lambda key: test_config[key]
        mock_config.get.side_effect = lambda key, default=None: test_config.get(key, default)
        
        self.assertFalse(self.service.is_enabled())
    
    @patch('cart.orange_money_service.requests.Session.post')
    @patch('cart.orange_money_service.settings.ORANGE_MONEY_CONFIG')
    def test_get_access_token_success(self, mock_config, mock_post):
        """Test de récupération réussie du token d'accès"""
        mock_config.__getitem__.side_effect = lambda key: self.test_config[key]
        mock_config.get.side_effect = lambda key, default=None: self.test_config.get(key, default)
        
        # Mock de la réponse API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'test_access_token',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response
        
        token = self.service.get_access_token()
        
        self.assertEqual(token, 'test_access_token')
        mock_post.assert_called_once()
    
    @patch('cart.orange_money_service.requests.Session.post')
    @patch('cart.orange_money_service.settings.ORANGE_MONEY_CONFIG')
    def test_get_access_token_failure(self, mock_config, mock_post):
        """Test d'échec de récupération du token d'accès"""
        mock_config.__getitem__.side_effect = lambda key: self.test_config[key]
        mock_config.get.side_effect = lambda key, default=None: self.test_config.get(key, default)
        
        # Mock de la réponse d'erreur
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = 'Unauthorized'
        mock_post.return_value = mock_response
        
        token = self.service.get_access_token()
        
        self.assertIsNone(token)
    
    def test_format_amount(self):
        """Test de formatage des montants"""
        # Test conversion FCFA vers centimes
        self.assertEqual(self.service.format_amount(1000.50), 100050)
        self.assertEqual(self.service.format_amount(0), 0)
        self.assertEqual(self.service.format_amount(1.99), 199)
    
    def test_parse_amount(self):
        """Test de parsing des montants"""
        # Test conversion centimes vers FCFA
        self.assertEqual(self.service.parse_amount(100050), 1000.50)
        self.assertEqual(self.service.parse_amount(0), 0.0)
        self.assertEqual(self.service.parse_amount(199), 1.99)
    
    def test_validate_webhook_notification_success(self):
        """Test de validation réussie d'une notification webhook"""
        notification_data = {
            'status': 'SUCCESS',
            'notif_token': 'test_token',
            'txnid': 'MP150709.1341.A00073'
        }
        
        result = self.service.validate_webhook_notification(notification_data, 'test_token')
        self.assertTrue(result)
    
    def test_validate_webhook_notification_invalid_token(self):
        """Test de validation échouée avec un token invalide"""
        notification_data = {
            'status': 'SUCCESS',
            'notif_token': 'test_token',
            'txnid': 'MP150709.1341.A00073'
        }
        
        result = self.service.validate_webhook_notification(notification_data, 'wrong_token')
        self.assertFalse(result)
    
    def test_validate_webhook_notification_invalid_status(self):
        """Test de validation échouée avec un statut invalide"""
        notification_data = {
            'status': 'INVALID_STATUS',
            'notif_token': 'test_token',
            'txnid': 'MP150709.1341.A00073'
        }
        
        result = self.service.validate_webhook_notification(notification_data, 'test_token')
        self.assertFalse(result)


class OrangeMoneyViewsTest(TestCase):
    """Tests pour les vues Orange Money"""
    
    def setUp(self):
        """Configuration des tests"""
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.shipping_address = ShippingAddress.objects.create(
            user=self.user,
            quarter='Quartier Test',
            street_address='Rue 123'
        )
        
        # Créer un produit de test
        self.product = Product.objects.create(
            title='Test Product',
            price=1000.00,
            is_salam=False,
            stock=10
        )
        
        # Créer un panier avec un article
        self.cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1
        )
    
    @patch('cart.views.orange_money_service.is_enabled')
    def test_orange_money_payment_disabled(self, mock_is_enabled):
        """Test d'accès à la vue de paiement quand Orange Money est désactivé"""
        mock_is_enabled.return_value = False
        
        self.client.force_login(self.user)
        response = self.client.get(reverse('cart:orange_money_payment'))
        
        self.assertEqual(response.status_code, 302)  # Redirection
        self.assertRedirects(response, reverse('cart:cart'))
    
    @patch('cart.views.orange_money_service.refresh_config')
    @patch('cart.views.orange_money_service.is_enabled')
    @patch('cart.views.orange_money_service.create_payment_session')
    def test_orange_money_payment_success(self, mock_create_session, mock_is_enabled, mock_refresh_config):
        """Test de création réussie d'une session de paiement"""
        mock_is_enabled.return_value = True
        mock_create_session.return_value = (True, {
            'pay_token': 'test_pay_token',
            'notif_token': 'test_notif_token',
            'payment_url': 'https://test.payment.url'
        })
        
        self.client.force_login(self.user)
        url = reverse('cart:orange_money_payment') + f'?shipping_address_id={self.shipping_address.id}'
        response = self.client.get(url)
        
        # Vérifier qu'une commande a été créée
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.payment_method, Order.MOBILE_MONEY)
        self.assertEqual(order.status, Order.DRAFT)
        
        # Vérifier que les tokens sont en session
        session = self.client.session
        self.assertEqual(session['orange_money_pay_token'], 'test_pay_token')
        self.assertEqual(session['orange_money_notif_token'], 'test_notif_token')
    
    def test_orange_money_cancel(self):
        """Test d'annulation de paiement Orange Money"""
        # Créer une commande de test
        order = Order.objects.create(
            user=self.user,
            subtotal=1000.00,
            shipping_cost=0,
            total=1000.00,
            payment_method=Order.MOBILE_MONEY,
            status=Order.DRAFT
        )
        
        # Simuler une session avec order_id
        session = self.client.session
        session['orange_money_order_id'] = order.id
        session.save()
        
        self.client.force_login(self.user)
        response = self.client.get(reverse('cart:orange_money_cancel'))
        
        # Vérifier que la commande est annulée
        order.refresh_from_db()
        self.assertEqual(order.status, Order.CANCELLED)
        
        # Vérifier la redirection
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('cart:cart'))
    
    def test_orange_money_webhook_invalid_method(self):
        """Test du webhook avec une méthode HTTP invalide"""
        response = self.client.get(reverse('cart:orange_money_webhook'))
        self.assertEqual(response.status_code, 405)
    
    def test_orange_money_webhook_invalid_json(self):
        """Test du webhook avec des données JSON invalides"""
        response = self.client.post(
            reverse('cart:orange_money_webhook'),
            data='invalid json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    @patch('cart.views.orange_money_service.validate_webhook_notification')
    def test_orange_money_webhook_success(self, mock_validate):
        """Test du webhook avec une notification valide"""
        mock_validate.return_value = True
        
        notification_data = {
            'status': 'SUCCESS',
            'notif_token': 'test_token',
            'txnid': 'MP150709.1341.A00073'
        }
        
        response = self.client.post(
            reverse('cart:orange_money_webhook'),
            data=json.dumps(notification_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'OK')


class OrangeMoneyIntegrationTest(TestCase):
    """Tests d'intégration pour Orange Money"""
    
    def setUp(self):
        """Configuration des tests d'intégration"""
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        # Créer des produits de test
        self.product1 = Product.objects.create(
            title='Product 1',
            price=1000.00,
            is_salam=False,
            stock=10
        )
        
        self.product2 = Product.objects.create(
            title='Product 2 (Salam)',
            price=2000.00,
            is_salam=True,
            stock=10
        )
    
    @patch('cart.orange_money_service.orange_money_service.refresh_config')
    @patch('cart.orange_money_service.orange_money_service.is_enabled')
    def test_payment_flow_salam_products(self, mock_is_enabled, mock_refresh_config):
        """Test du flux de paiement pour les produits Salam"""
        mock_is_enabled.return_value = True
        # Ajouter des produits Salam au panier
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product2, quantity=1)
        
        self.client.force_login(self.user)
        
        # Vérifier que Orange Money est disponible pour les produits Salam
        response = self.client.get(reverse('cart:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Orange Money')
    
    @patch('cart.orange_money_service.orange_money_service.refresh_config')
    @patch('cart.orange_money_service.orange_money_service.is_enabled')
    def test_payment_flow_mixed_cart(self, mock_is_enabled, mock_refresh_config):
        """Test du flux de paiement pour un panier mixte"""
        mock_is_enabled.return_value = True
        # Créer un panier mixte
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product1, quantity=1)
        CartItem.objects.create(cart=cart, product=self.product2, quantity=1)
        
        self.client.force_login(self.user)
        
        # Vérifier que la page panier mixte est affichée
        response = self.client.get(reverse('cart:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Panier mixte')
