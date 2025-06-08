from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from accounts.models import LoginTwoFactorCode

class TestTwoFactorService(TestCase):
    def setUp(self):
        self.code = LoginTwoFactorCode.generate_code()

    def test_generate_code_returns_six_digits(self):
        """Test que le code généré contient exactement 6 chiffres."""
        self.assertEqual(len(self.code), 6)
        self.assertTrue(self.code.isdigit())

    def test_code_expiration(self):
        """Test que le code expire après 5 minutes."""
        # Créer un code
        two_factor_code = LoginTwoFactorCode.objects.create(
            code=self.code,
            user=None  # On peut tester sans utilisateur
        )
        
        # Vérifier que le code est valide initialement
        self.assertTrue(two_factor_code.is_valid())
        
        # Simuler le passage du temps (6 minutes)
        two_factor_code.created_at = timezone.now() - timedelta(minutes=6)
        two_factor_code.save()
        
        # Vérifier que le code est expiré
        self.assertFalse(two_factor_code.is_valid())

    def test_code_uniqueness(self):
        """Test que les codes générés sont uniques."""
        codes = set()
        for _ in range(100):
            code = LoginTwoFactorCode.generate_code()
            self.assertNotIn(code, codes)
            codes.add(code) 