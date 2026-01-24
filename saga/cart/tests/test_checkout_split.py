from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import ShippingAddress
from cart.models import Cart, CartItem, Order
from product.models import Category, Product


User = get_user_model()


class CartCheckoutSplitTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='split@test.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(name='Split', slug='split')

        self.product_a = Product.objects.create(
            title='Produit A',
            slug='produit-a',
            price=Decimal('10000'),
            category=self.category,
            stock=10,
            specifications={
                'delivery_methods': [
                    {
                        'id': 3,
                        'name': 'Express',
                        'slug': 'express',
                        'base_price': '5000.00',
                        'effective_price': '5000.00',
                        'site_configuration': 18,
                    }
                ]
            }
        )

        self.product_b = Product.objects.create(
            title='Produit B',
            slug='produit-b',
            price=Decimal('15000'),
            category=self.category,
            stock=10,
            specifications={
                'delivery_methods': [
                    {
                        'id': 7,
                        'name': 'Standard',
                        'slug': 'standard',
                        'base_price': '2000.00',
                        'effective_price': '2000.00',
                        'site_configuration': 22,
                    }
                ]
            }
        )

        self.address = ShippingAddress.objects.create(
            user=self.user,
            full_name='Split User',
            quarter='Test Quarter',
            street_address='123 Test',
            city='BKO',
            is_default=True
        )

        self.cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=self.cart, product=self.product_a, quantity=1)
        CartItem.objects.create(cart=self.cart, product=self.product_b, quantity=1)

    def _reset_cart_items(self, products):
        self.cart.cart_items.all().delete()
        for product in products:
            CartItem.objects.create(cart=self.cart, product=product, quantity=1)

    def test_checkout_splits_by_site_and_method(self):
        url = reverse('cart-checkout')
        response = self.client.post(url, {
            'payment_method': 'cash_on_delivery',
            'shipping_address_id': self.address.id,
            'product_type': 'all',
        }, format='json')

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertTrue(data.get('split'))
        orders = data.get('orders') or []
        self.assertEqual(len(orders), 2)

        order_ids = [order.get('order_id') for order in orders]
        self.assertEqual(Order.objects.filter(id__in=order_ids).count(), 2)

        costs = sorted([Decimal(order.get('shipping_cost')) for order in orders])
        self.assertEqual(costs, [Decimal('2000.00'), Decimal('5000.00')])

        sites = sorted([order.get('site_configuration') for order in orders])
        self.assertEqual(sites, [18, 22])

    def test_checkout_no_split_when_common_method(self):
        common_method = {
            'id': 3,
            'name': 'Express',
            'slug': 'express',
            'base_price': '5000.00',
            'effective_price': '5000.00',
            'site_configuration': 18,
        }
        self.product_a.specifications = {'delivery_methods': [common_method]}
        self.product_a.save(update_fields=['specifications'])
        self.product_b.specifications = {'delivery_methods': [common_method]}
        self.product_b.save(update_fields=['specifications'])

        self._reset_cart_items([self.product_a, self.product_b])

        url = reverse('cart-checkout')
        response = self.client.post(url, {
            'payment_method': 'cash_on_delivery',
            'shipping_address_id': self.address.id,
            'product_type': 'all',
        }, format='json')

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertFalse(data.get('split'))
        orders = data.get('orders') or []
        self.assertEqual(len(orders), 1)
        self.assertEqual(Decimal(orders[0].get('shipping_cost')), Decimal('5000.00'))
        self.assertEqual(orders[0].get('site_configuration'), 18)

    def test_checkout_respects_selected_common_method(self):
        method_express = {
            'id': 3,
            'name': 'Express',
            'slug': 'express',
            'base_price': '5000.00',
            'effective_price': '5000.00',
            'site_configuration': 18,
        }
        method_standard = {
            'id': 7,
            'name': 'Standard',
            'slug': 'standard',
            'base_price': '2000.00',
            'effective_price': '2000.00',
            'site_configuration': 18,
        }
        self.product_a.specifications = {'delivery_methods': [method_express, method_standard]}
        self.product_a.save(update_fields=['specifications'])
        self.product_b.specifications = {'delivery_methods': [method_express, method_standard]}
        self.product_b.save(update_fields=['specifications'])

        self._reset_cart_items([self.product_a, self.product_b])

        url = reverse('cart-checkout')
        response = self.client.post(url, {
            'payment_method': 'cash_on_delivery',
            'shipping_address_id': self.address.id,
            'product_type': 'all',
            'shipping_method_id': 7,
        }, format='json')

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertFalse(data.get('split'))
        orders = data.get('orders') or []
        self.assertEqual(len(orders), 1)
        self.assertEqual(Decimal(orders[0].get('shipping_cost')), Decimal('2000.00'))
        method = orders[0].get('shipping_method') or {}
        self.assertEqual(method.get('id'), 7)

    @patch('cart.api.views.stripe.checkout.Session.create')
    def test_checkout_split_stripe(self, mock_stripe_create):
        mock_stripe_create.return_value = MagicMock(id='sess_test', url='https://stripe.test/checkout')

        url = reverse('cart-checkout')
        response = self.client.post(url, {
            'payment_method': 'stripe',
            'shipping_address_id': self.address.id,
            'product_type': 'all',
        }, format='json')

        self.assertEqual(response.status_code, 200)
        data = response.json()

        orders = data.get('orders') or []
        self.assertEqual(len(orders), 2)
        self.assertTrue(all(order.get('checkout_url') for order in orders))
        self.assertTrue(all(order.get('payment_method') == 'stripe' for order in orders))
        self.assertEqual(mock_stripe_create.call_count, 2)

    @patch('cart.api.views.orange_money_service.get_payment_url')
    @patch('cart.api.views.orange_money_service.create_payment_session')
    def test_checkout_split_orange_money(self, mock_create_session, mock_get_url):
        mock_create_session.return_value = (True, {'pay_token': 'token', 'payment_url': 'https://om.test'})
        mock_get_url.return_value = 'https://om.test/redirect'

        url = reverse('cart-checkout')
        response = self.client.post(url, {
            'payment_method': 'orange_money',
            'shipping_address_id': self.address.id,
            'product_type': 'all',
        }, format='json')

        self.assertEqual(response.status_code, 200)
        data = response.json()

        orders = data.get('orders') or []
        self.assertEqual(len(orders), 2)
        self.assertTrue(all(order.get('checkout_url') for order in orders))
        self.assertTrue(all(order.get('payment_method') == 'orange_money' for order in orders))
        self.assertEqual(mock_create_session.call_count, 2)
        self.assertEqual(mock_get_url.call_count, 2)
