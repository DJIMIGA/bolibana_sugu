from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import Shopper
from behave import given, when, then
import time

class TestLoginFlow(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Shopper.objects.create_user(
            email='test@example.com',
            password='testpassword123',
            phone='+33612345678'
        )
        self.login_url = reverse('accounts:login')
        self.verify_2fa_url = reverse('accounts:verify_2fa')

    @given('un utilisateur avec email "{email}" et mot de passe "{password}"')
    def create_user(self, email, password):
        self.user = Shopper.objects.create_user(
            email=email,
            password=password,
            phone='+33612345678'
        )

    @when('je me connecte avec email "{email}" et mot de passe "{password}"')
    def login(self, email, password):
        self.response = self.client.post(self.login_url, {
            'username': email,
            'password': password
        })

    @then('je suis redirigé vers la page de vérification 2FA')
    def verify_2fa_redirect(self):
        self.assertEqual(self.response.status_code, 302)
        self.assertIn('verify-2fa', self.response.url)

    @when('j\'entre le code de vérification "{code}"')
    def enter_verification_code(self, code):
        self.verify_response = self.client.post(self.verify_2fa_url, {
            'code': code
        })

    @then('je suis connecté et redirigé vers la page d\'accueil')
    def verify_successful_login(self):
        self.assertEqual(self.verify_response.status_code, 302)
        self.assertIn('supplier_index', self.verify_response.url)
        self.assertTrue(self.verify_response.wsgi_request.user.is_authenticated)

    def test_complete_login_flow(self):
        """Test le flux complet de connexion."""
        # 1. Connexion initiale
        response = self.client.post(self.login_url, {
            'username': 'test@example.com',
            'password': 'testpassword123'
        })
        
        # Vérifier la redirection vers 2FA
        self.assertEqual(response.status_code, 302)
        self.assertIn('verify-2fa', response.url)
        
        # 2. Vérification 2FA
        two_factor_code = LoginTwoFactorCode.objects.filter(user=self.user).first()
        response = self.client.post(self.verify_2fa_url, {
            'code': two_factor_code.code
        })
        
        # Vérifier la connexion réussie
        self.assertEqual(response.status_code, 302)
        self.assertIn('supplier_index', response.url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_with_invalid_credentials(self):
        """Test la connexion avec des identifiants invalides."""
        response = self.client.post(self.login_url, {
            'username': 'test@example.com',
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, 200)  # Reste sur la page de login
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_without_2fa_setup(self):
        """Test la connexion d'un utilisateur sans 2FA configuré."""
        # Créer un utilisateur sans numéro de téléphone
        user = Shopper.objects.create_user(
            email='no2fa@example.com',
            password='testpassword123'
        )
        
        response = self.client.post(self.login_url, {
            'username': 'no2fa@example.com',
            'password': 'testpassword123'
        })
        
        # Vérifier la connexion directe sans 2FA
        self.assertEqual(response.status_code, 302)
        self.assertIn('supplier_index', response.url)
        self.assertTrue(response.wsgi_request.user.is_authenticated) 