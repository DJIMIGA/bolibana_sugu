"""
Tests pour la synchronisation des commandes SagaKore ↔ B2B
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import json
from unittest.mock import patch

from cart.models import Order, OrderItem
from product.models import Product, Category
from inventory.models import ExternalProduct, ApiKey
from inventory.services import OrderSyncService, InventoryAPIError
from inventory.api.views import b2b_order_status_webhook

User = get_user_model()


class OrderSyncServiceTestCase(TestCase):
    """Tests pour OrderSyncService"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        # Créer une catégorie
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        
        # Créer un produit au poids (g) avec mapping B2B
        self.product = Product.objects.create(
            title='Test Product (g)',
            price=Decimal('100.00'),
            stock=10,
            category=self.category,
            is_available=True,
            specifications={
                'sold_by_weight': True,
                'weight_unit': 'g',
                'unit_display': 'g'
            }
        )
        
        # Créer le mapping externe (produit au poids)
        self.external_product = ExternalProduct.objects.create(
            product=self.product,
            external_id=123,
            external_sku='SKU-123',
            sync_status='synced',
            is_b2b=True
        )

        # Créer un produit à l'unité avec mapping B2B
        self.unit_product = Product.objects.create(
            title='Test Product (unit)',
            price=Decimal('50.00'),
            stock=20,
            category=self.category,
            is_available=True,
            specifications={
                'sold_by_weight': False,
                'unit_display': 'unité'
            }
        )
        self.external_unit_product = ExternalProduct.objects.create(
            product=self.unit_product,
            external_id=456,
            external_sku='SKU-456',
            sync_status='synced',
            is_b2b=True
        )
        
        # Créer une clé API pour les tests
        self.api_key = ApiKey.objects.create(
            name='Test API Key',
            is_active=True
        )
        self.api_key.set_key('test-api-key-123')
        self.api_key.save()
        
        # Créer une commande
        from accounts.models import ShippingAddress
        self.shipping_address = ShippingAddress.objects.create(
            user=self.user,
            full_name='Test User',
            quarter='Hamdallaye',
            street_address='Rue 123, porte 456',
            city='BKO'
        )
        
        self.order = Order.objects.create(
            user=self.user,
            shipping_address=self.shipping_address,
            subtotal=Decimal('100.00'),
            shipping_cost=Decimal('10.00'),
            total=Decimal('110.00'),
            is_paid=True,
            status=Order.CONFIRMED,
            metadata={'delivery_site_configuration': 1}
        )
        
        # Créer un item de commande (produit au poids)
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=Decimal('1.0'),
            price=Decimal('100.00')
        )

        # Créer un item de commande (produit à l'unité)
        self.unit_order_item = OrderItem.objects.create(
            order=self.order,
            product=self.unit_product,
            quantity=Decimal('2.0'),
            price=Decimal('50.00')
        )
    
    @patch('inventory.services.InventoryAPIClient.get_sites_list')
    @patch('inventory.services.InventoryAPIClient.create_sale')
    def test_sync_order_to_b2b_success(self, mock_create_sale, mock_get_sites):
        """Test de synchronisation réussie d'une commande vers B2B"""
        # Mock des réponses API
        mock_get_sites.return_value = [{'id': 1, 'name': 'Site 1'}]
        mock_create_sale.return_value = {
            'id': 456,
            'sale_id': 456,
            'order_number': self.order.order_number
        }
        
        # Synchroniser
        sync_service = OrderSyncService()
        result = sync_service.sync_order_to_b2b(self.order)
        
        # Vérifications
        self.assertEqual(result['external_sale_id'], 456)
        self.assertEqual(result['status'], 'synced')
        
        # Vérifier que les métadonnées ont été mises à jour
        self.order.refresh_from_db()
        metadata = self.order.metadata
        self.assertEqual(metadata.get('b2b_sync_status'), 'synced')
        self.assertEqual(metadata.get('b2b_sale_id'), 456)
        self.assertIn('b2b_synced_at', metadata)
        
        # Vérifier que create_sale a été appelé avec les bonnes données
        mock_create_sale.assert_called_once()
        payload = mock_create_sale.call_args[0][0]
        self.assertEqual(payload['order_number'], self.order.order_number)
        self.assertEqual(len(payload['items']), 2)
        items_by_product = {item['product_id']: item for item in payload['items']}

        weighted_item = items_by_product[123]
        self.assertEqual(weighted_item['quantity'], 1.0)
        self.assertEqual(weighted_item['sale_unit_type'], 'weight')
        self.assertEqual(weighted_item.get('weight_unit'), 'g')

        unit_item = items_by_product[456]
        self.assertEqual(unit_item['quantity'], 2.0)
        self.assertEqual(unit_item['sale_unit_type'], 'unit')
        self.assertIsNone(unit_item.get('weight_unit'))
    
    @patch('inventory.services.InventoryAPIClient.get_sites_list')
    @patch('inventory.services.InventoryAPIClient.create_sale')
    def test_sync_order_already_synced(self, mock_create_sale, mock_get_sites):
        """Test que la synchronisation ne se fait pas si déjà synchronisée"""
        # Marquer la commande comme déjà synchronisée
        self.order.metadata = {
            'b2b_sync_status': 'synced',
            'b2b_sale_id': 789
        }
        self.order.save()
        
        # Synchroniser
        sync_service = OrderSyncService()
        result = sync_service.sync_order_to_b2b(self.order)
        
        # Vérifications
        self.assertEqual(result['status'], 'already_synced')
        self.assertEqual(result['external_sale_id'], 789)
        
        # Vérifier que create_sale n'a pas été appelé
        mock_create_sale.assert_not_called()
    
    def test_sync_order_not_paid(self):
        """Test que la synchronisation échoue si la commande n'est pas payée"""
        self.order.is_paid = False
        self.order.status = Order.PENDING
        self.order.save()
        
        sync_service = OrderSyncService()
        
        with self.assertRaises(ValueError) as context:
            sync_service.sync_order_to_b2b(self.order)
        
        self.assertIn('doit être payée', str(context.exception))
    
    def test_sync_order_no_external_product(self):
        """Test que la synchronisation échoue si le produit n'a pas de mapping B2B"""
        # Supprimer les mappings externes
        self.external_product.delete()
        self.external_unit_product.delete()
        
        sync_service = OrderSyncService()
        
        with self.assertRaises(InventoryAPIError) as context:
            sync_service.sync_order_to_b2b(self.order)
        
        self.assertIn('Aucun produit avec mapping B2B', str(context.exception))


class B2BOrderStatusWebhookTestCase(TestCase):
    """Tests pour le webhook de statut de commande B2B"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        # Créer une clé API
        self.api_key = ApiKey.objects.create(
            name='Test API Key',
            is_active=True
        )
        self.api_key.set_key('test-api-key-123')
        self.api_key.save()
        
        # Créer une commande
        from accounts.models import ShippingAddress
        self.shipping_address = ShippingAddress.objects.create(
            user=self.user,
            full_name='Test User',
            quarter='Hamdallaye',
            street_address='Rue 123, porte 456',
            city='BKO'
        )
        
        self.order = Order.objects.create(
            user=self.user,
            shipping_address=self.shipping_address,
            subtotal=Decimal('100.00'),
            shipping_cost=Decimal('10.00'),
            total=Decimal('110.00'),
            is_paid=True,
            status=Order.CONFIRMED,
            metadata={
                'b2b_sync_status': 'synced',
                'b2b_sale_id': 456
            }
        )
    
    def test_webhook_missing_api_key(self):
        """Test que le webhook rejette les requêtes sans clé API"""
        response = self.client.post(
            '/api/inventory/webhooks/order-status/',
            data=json.dumps({
                'external_sale_id': 456,
                'status': Order.SHIPPED,
                'order_number': self.order.order_number
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.content)
        self.assertIn('Missing X-API-Key', data.get('error', ''))
    
    def test_webhook_invalid_api_key(self):
        """Test que le webhook rejette les requêtes avec une clé API invalide"""
        response = self.client.post(
            '/api/inventory/webhooks/order-status/',
            data=json.dumps({
                'external_sale_id': 456,
                'status': Order.SHIPPED,
                'order_number': self.order.order_number
            }),
            content_type='application/json',
            HTTP_X_API_KEY='invalid-key'
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.content)
        self.assertIn('Invalid API key', data.get('error', ''))
    
    def test_webhook_missing_fields(self):
        """Test que le webhook rejette les requêtes avec des champs manquants"""
        response = self.client.post(
            '/api/inventory/webhooks/order-status/',
            data=json.dumps({
                'external_sale_id': 456
                # status et order_number manquants
            }),
            content_type='application/json',
            HTTP_X_API_KEY='test-api-key-123'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('Missing required fields', data.get('error', ''))
    
    def test_webhook_order_not_found(self):
        """Test que le webhook retourne 404 si la commande n'existe pas"""
        response = self.client.post(
            '/api/inventory/webhooks/order-status/',
            data=json.dumps({
                'external_sale_id': 456,
                'status': Order.SHIPPED,
                'order_number': 'CMD-NONEXISTENT'
            }),
            content_type='application/json',
            HTTP_X_API_KEY='test-api-key-123'
        )
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertIn('Order not found', data.get('error', ''))
    
    def test_webhook_update_status_success(self):
        """Test de mise à jour réussie du statut de commande"""
        old_status = self.order.status
        
        response = self.client.post(
            '/api/inventory/webhooks/order-status/',
            data=json.dumps({
                'external_sale_id': 456,
                'status': Order.SHIPPED,
                'order_number': self.order.order_number,
                'tracking_number': 'TRACK-123'
            }),
            content_type='application/json',
            HTTP_X_API_KEY='test-api-key-123'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
        self.assertEqual(data.get('old_status'), old_status)
        self.assertEqual(data.get('new_status'), Order.SHIPPED)
        
        # Vérifier que la commande a été mise à jour
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.SHIPPED)
        self.assertEqual(self.order.tracking_number, 'TRACK-123')
        
        # Vérifier les métadonnées
        metadata = self.order.metadata
        self.assertIn('b2b_last_status_update', metadata)
        self.assertEqual(metadata.get('b2b_status_update_source'), 'webhook')
    
    def test_webhook_invalid_status(self):
        """Test que le webhook rejette les statuts invalides"""
        response = self.client.post(
            '/api/inventory/webhooks/order-status/',
            data=json.dumps({
                'external_sale_id': 456,
                'status': 'invalid_status',
                'order_number': self.order.order_number
            }),
            content_type='application/json',
            HTTP_X_API_KEY='test-api-key-123'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('Invalid status', data.get('error', ''))
    
    def test_webhook_external_id_mismatch(self):
        """Test que le webhook rejette si external_sale_id ne correspond pas"""
        response = self.client.post(
            '/api/inventory/webhooks/order-status/',
            data=json.dumps({
                'external_sale_id': 999,  # Différent de celui dans metadata
                'status': Order.SHIPPED,
                'order_number': self.order.order_number
            }),
            content_type='application/json',
            HTTP_X_API_KEY='test-api-key-123'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('external_sale_id mismatch', data.get('error', ''))
