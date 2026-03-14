from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import Shopper
from django_otp.oath import totp

class TestLoginFlow(TestCase):
    def setUp(self):
        """Configuration initiale pour les tests."""
        self.client = Client()
        self.user = Shopper.objects.create_user(
            email='test@example.com',
            password='testpass123',
            phone='+33612345678'
        )

    def test_login_with_2fa(self):
        """Test le processus de connexion complet avec 2FA."""
        # Activer 2FA
        device = self.user.enable_2fa()
        
        # Étape 1: Connexion avec email/mot de passe
        response = self.client.post(reverse('accounts:login'), {
            'username': self.user.email,
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('2fa', response.url)

        # Étape 2: Vérification 2FA
        bin_key = device.bin_key if hasattr(device, 'bin_key') else device.key
        token = str(totp(bin_key)).zfill(6)
        response = self.client.post(response.url, {
            'token': token
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('suppliers:supplier_index'))

    def test_login_without_2fa(self):
        """Test le processus de connexion sans 2FA."""
        response = self.client.post(reverse('accounts:login'), {
            'username': self.user.email,
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('suppliers:supplier_index')) 