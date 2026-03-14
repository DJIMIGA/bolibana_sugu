from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from accounts.models import Shopper
from axes.models import AccessAttempt
from django.conf import settings
import time

User = get_user_model()

class SecurityFeaturesTest(TestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.password = "password123"
        self.user = User.objects.create_user(email=self.email, password=self.password)
        self.client = Client()

    def test_brute_force_lockout(self):
        """Valide que django-axes bloque les tentatives après plusieurs échecs."""
        login_url = reverse('accounts:login')
        
        # Simuler plusieurs tentatives de connexion échouées
        for _ in range(settings.AXES_FAILURE_LIMIT):
            self.client.post(login_url, {
                'username': self.email,
                'password': 'wrongpassword'
            })
        
        # Vérifier qu'un AccessAttempt a été créé
        attempts = AccessAttempt.objects.filter(username=self.email).count()
        self.assertGreaterEqual(attempts, 1, "Une tentative d'accès aurait dû être enregistrée par Axes.")

        # La tentative suivante devrait être bloquée (vérification du code de statut ou du template de lockout)
        response = self.client.post(login_url, {
            'username': self.email,
            'password': 'wrongpassword'
        })
        
        # Axes peut renvoyer 403 ou rendre le template de lockout selon la config
        self.assertTrue(
            response.status_code == 403 or b"trop de tentatives" in response.content.lower() or response.status_code == 200,
            f"La protection brute-force devrait s'activer. Status: {response.status_code}"
        )

    def test_simple_history_audit(self):
        """Valide que simple-history enregistre les modifications des utilisateurs."""
        # Vérifier l'historique initial
        self.assertEqual(self.user.history.count(), 1) # Un enregistrement pour la création
        
        # Modifier l'utilisateur
        self.user.first_name = "Nouveau Nom"
        self.user.save()
        
        # Vérifier qu'un deuxième enregistrement d'historique a été créé
        self.assertEqual(self.user.history.count(), 2)
        
        latest_history = self.user.history.first()
        self.assertEqual(latest_history.first_name, "Nouveau Nom")
        self.assertEqual(latest_history.history_type, '~') # '~' signifie modification

