from django.test import TestCase
from django.utils import timezone
from accounts.models import Shopper, LoginTwoFactorCode
from concurrent.futures import ThreadPoolExecutor
import time

class Test2FAPerformance(TestCase):
    def setUp(self):
        self.user = Shopper.objects.create_user(
            email='test@example.com',
            password='testpassword123',
            phone='+33612345678'
        )

    def test_code_generation_performance(self):
        """Test la performance de la génération de codes."""
        start_time = time.time()
        
        # Générer 1000 codes
        codes = []
        for _ in range(1000):
            code = LoginTwoFactorCode.generate_code()
            codes.append(code)
            
        end_time = time.time()
        generation_time = end_time - start_time
        
        # Vérifier que la génération est rapide (moins d'une seconde)
        self.assertLess(generation_time, 1.0)
        
        # Vérifier l'unicité des codes
        self.assertEqual(len(set(codes)), 1000)

    def test_concurrent_code_validation(self):
        """Test la performance de la validation concurrente des codes."""
        # Créer plusieurs codes
        codes = []
        for _ in range(10):
            code = LoginTwoFactorCode.generate_code()
            two_factor_code = LoginTwoFactorCode.objects.create(
                user=self.user,
                code=code
            )
            codes.append(two_factor_code)
        
        start_time = time.time()
        
        # Simuler des validations concurrentes
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for code in codes:
                futures.append(executor.submit(code.is_valid))
            
            # Attendre toutes les validations
            results = [f.result() for f in futures]
            
        end_time = time.time()
        validation_time = end_time - start_time
        
        # Vérifier que la validation est rapide (moins d'une seconde)
        self.assertLess(validation_time, 1.0)
        
        # Vérifier que tous les codes sont valides
        self.assertTrue(all(results))

    def test_database_performance(self):
        """Test la performance des opérations de base de données."""
        start_time = time.time()
        
        # Créer 100 codes
        for _ in range(100):
            code = LoginTwoFactorCode.generate_code()
            LoginTwoFactorCode.objects.create(
                user=self.user,
                code=code
            )
            
        # Mesurer le temps de création
        creation_time = time.time() - start_time
        
        # Vérifier que la création est rapide
        self.assertLess(creation_time, 1.0)
        
        # Test de la lecture
        start_time = time.time()
        codes = LoginTwoFactorCode.objects.filter(user=self.user)
        read_time = time.time() - start_time
        
        # Vérifier que la lecture est rapide
        self.assertLess(read_time, 0.1)
        
        # Vérifier le nombre de codes
        self.assertEqual(codes.count(), 100)

    def test_code_expiration_performance(self):
        """Test la performance de la vérification d'expiration."""
        # Créer un code
        code = LoginTwoFactorCode.generate_code()
        two_factor_code = LoginTwoFactorCode.objects.create(
            user=self.user,
            code=code
        )
        
        start_time = time.time()
        
        # Vérifier l'expiration 1000 fois
        for _ in range(1000):
            is_valid = two_factor_code.is_valid()
            
        end_time = time.time()
        check_time = end_time - start_time
        
        # Vérifier que la vérification est rapide
        self.assertLess(check_time, 1.0) 