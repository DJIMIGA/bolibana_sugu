from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import Shopper, LoginTwoFactorCode
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

class Test2FAFlow(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Shopper.objects.create_user(
            email='test@example.com',
            password='testpassword123',
            phone='+33612345678'
        )
        self.login_url = reverse('accounts:login')
        self.verify_2fa_url = reverse('accounts:verify_2fa')

    def test_complete_2fa_flow(self):
        """Test le flux complet de connexion avec 2FA."""
        # 1. Tentative de connexion
        response = self.client.post(self.login_url, {
            'username': 'test@example.com',
            'password': 'testpassword123'
        })
        
        # Vérifier la redirection vers la page 2FA
        self.assertEqual(response.status_code, 302)
        self.assertIn('verify-2fa', response.url)
        
        # Vérifier que le code 2FA a été généré
        two_factor_code = LoginTwoFactorCode.objects.filter(user=self.user).first()
        self.assertIsNotNone(two_factor_code)
        
        # 2. Vérification du code 2FA
        response = self.client.post(self.verify_2fa_url, {
            'code': two_factor_code.code
        })
        
        # Vérifier la redirection vers la page d'accueil
        self.assertEqual(response.status_code, 302)
        self.assertIn('supplier_index', response.url)
        
        # Vérifier que l'utilisateur est connecté
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_invalid_2fa_code(self):
        """Test le rejet d'un code 2FA invalide."""
        # 1. Connexion initiale
        self.client.post(self.login_url, {
            'username': 'test@example.com',
            'password': 'testpassword123'
        })
        
        # 2. Tentative avec un code invalide
        response = self.client.post(self.verify_2fa_url, {
            'code': '000000'
        })
        
        # Vérifier que l'utilisateur n'est pas connecté
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        
        # Vérifier le message d'erreur
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertTrue(any('invalide' in str(msg) for msg in messages_list))

    def test_expired_2fa_code(self):
        """Test le rejet d'un code 2FA expiré."""
        # 1. Connexion initiale
        self.client.post(self.login_url, {
            'username': 'test@example.com',
            'password': 'testpassword123'
        })
        
        # 2. Récupérer le code
        two_factor_code = LoginTwoFactorCode.objects.filter(user=self.user).first()
        
        # 3. Simuler l'expiration
        two_factor_code.created_at = timezone.now() - timedelta(minutes=6)
        two_factor_code.save()
        
        # 4. Tentative avec le code expiré
        response = self.client.post(self.verify_2fa_url, {
            'code': two_factor_code.code
        })
        
        # Vérifier que l'utilisateur n'est pas connecté
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        
        # Vérifier le message d'erreur
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertTrue(any('expiré' in str(msg) for msg in messages_list)) 