from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import Shopper, TOTPDevice
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django_otp.oath import totp
import time

class Test2FAFlow(TestCase):
    def setUp(self):
        """Configuration initiale pour les tests."""
        self.client = Client()
        self.user = Shopper.objects.create_user(
            email='test@example.com',
            password='testpass123',
            phone='+33612345678'
        )
        self.device = self.user.enable_2fa()
        # Vérifier que la 2FA est bien activée
        self.assertTrue(self.user.has_2fa_enabled())

    def test_login_with_2fa(self):
        """Test le processus de connexion complet avec 2FA."""
        # Étape 1: Connexion avec email/mot de passe
        response = self.client.post(reverse('accounts:login'), {
            'username': self.user.email,
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('2fa', response.url)
        # Vérifier que l'ID de l'utilisateur est bien en session
        self.assertIn('2fa_user_id', self.client.session)

        # Étape 2: Vérification 2FA
        bin_key = self.device.bin_key if hasattr(self.device, 'bin_key') else self.device.key
        token = str(totp(bin_key)).zfill(6)
        response = self.client.post(reverse('accounts:verify_2fa'), {
            'token': token
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')  # Redirection vers la page d'accueil
        # Vérifier que l'utilisateur est bien authentifié
        self.assertTrue(self.client.session.get('_auth_user_id'))

    def test_login_without_2fa(self):
        """Test le processus de connexion sans 2FA."""
        # Désactiver 2FA
        self.device.delete()
        # Vérifier que la 2FA est bien désactivée
        self.assertFalse(self.user.has_2fa_enabled())
        
        response = self.client.post(reverse('accounts:login'), {
            'username': self.user.email,
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')  # Redirection vers la page d'accueil
        # Vérifier que l'utilisateur est bien authentifié
        self.assertTrue(self.client.session.get('_auth_user_id'))

    def test_invalid_2fa_code(self):
        """Test la connexion avec un code 2FA invalide."""
        # Étape 1: Connexion avec email/mot de passe
        response = self.client.post(reverse('accounts:login'), {
            'username': self.user.email,
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('2fa', response.url)

        # Étape 2: Tentative avec un code invalide
        response = self.client.post(response.url, {
            'token': '000000'
        })
        # La vue redirige vers la même page avec un message d'erreur
        self.assertEqual(response.status_code, 302)
        self.assertIn('2fa', response.url)
        self.assertFalse(self.client.session.get('_auth_user_id'))

    def test_expired_2fa_code(self):
        """Test le rejet d'un code 2FA expiré."""
        # Étape 1: Connexion avec email/mot de passe
        response = self.client.post(reverse('accounts:login'), {
            'username': self.user.email,
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('2fa', response.url)

        # Étape 2: Attendre l'expiration du token
        time.sleep(31)
        
        # Étape 3: Tentative avec le token expiré
        bin_key = self.device.bin_key if hasattr(self.device, 'bin_key') else self.device.key
        token = str(totp(bin_key)).zfill(6)
        response = self.client.post(response.url, {
            'token': token
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('2fa', response.url)
        self.assertFalse(self.client.session.get('_auth_user_id'))

    def test_multiple_devices(self):
        """Test qu'un utilisateur peut avoir plusieurs appareils 2FA."""
        # Créer un deuxième appareil
        second_device = self.user.enable_2fa()
        
        # Vérifier que les deux appareils sont actifs
        active_devices = TOTPDevice.objects.filter(user=self.user, confirmed=True)
        self.assertEqual(active_devices.count(), 2)
        
        # Vérifier que les deux appareils fonctionnent
        bin_key1 = self.device.bin_key if hasattr(self.device, 'bin_key') else self.device.key
        bin_key2 = second_device.bin_key if hasattr(second_device, 'bin_key') else second_device.key
        token1 = str(totp(bin_key1)).zfill(6)
        token2 = str(totp(bin_key2)).zfill(6)
        
        self.assertTrue(self.user.verify_2fa_code(token1))
        self.assertTrue(self.user.verify_2fa_code(token2)) 