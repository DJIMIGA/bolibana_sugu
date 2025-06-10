from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from accounts.models import Shopper, TOTPDevice
from django_otp.plugins.otp_totp.models import TOTPDevice as BaseTOTPDevice
from django_otp.oath import totp
import time

class TestTwoFactorService(TestCase):
    def setUp(self):
        """Configuration initiale pour les tests."""
        self.user = Shopper.objects.create_user(
            email='test@example.com',
            password='testpass123',
            phone='+33612345678'
        )
        # Créer et confirmer l'appareil TOTP
        self.device = self.user.enable_2fa()
        self.device.confirmed = True
        self.device.save()

    def test_device_creation(self):
        """Test la création d'un appareil TOTP."""
        self.assertIsNotNone(self.device)
        self.assertTrue(self.device.confirmed)
        self.assertTrue(self.device.name.startswith('Device'))

    def test_device_confirmation(self):
        """Test la confirmation d'un appareil TOTP."""
        # Créer un nouvel appareil non confirmé
        new_device = self.user.enable_2fa()
        self.assertFalse(new_device.confirmed)
        
        # Confirmer l'appareil
        new_device.confirmed = True
        new_device.save()
        self.assertTrue(new_device.confirmed)

    def test_device_deletion(self):
        """Test la suppression d'un appareil TOTP."""
        device_id = self.device.id
        self.device.delete()
        self.assertFalse(TOTPDevice.objects.filter(id=device_id).exists())

    def test_multiple_devices(self):
        """Test qu'un utilisateur peut avoir plusieurs appareils TOTP actifs."""
        # Créer et confirmer un deuxième appareil
        second_device = self.user.enable_2fa()
        second_device.confirmed = True
        second_device.save()
        
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

    def test_token_validation(self):
        """Test la validation d'un token TOTP."""
        bin_key = self.device.bin_key if hasattr(self.device, 'bin_key') else self.device.key
        token = str(totp(bin_key)).zfill(6)
        self.assertTrue(self.user.verify_2fa_code(token))
        self.assertFalse(self.user.verify_2fa_code('000000'))

    def test_token_expiration(self):
        """Test l'expiration d'un token TOTP."""
        bin_key = self.device.bin_key if hasattr(self.device, 'bin_key') else self.device.key
        token = str(totp(bin_key)).zfill(6)
        self.assertTrue(self.user.verify_2fa_code(token))
        
        # Attendre que le token expire
        time.sleep(31)
        self.assertFalse(self.user.verify_2fa_code(token))

    def test_disable_2fa(self):
        """Test la désactivation de la 2FA."""
        # Générer un token valide
        bin_key = self.device.bin_key if hasattr(self.device, 'bin_key') else self.device.key
        token = str(totp(bin_key)).zfill(6)
        
        # Désactiver la 2FA
        self.assertTrue(self.user.disable_2fa(token))
        
        # Vérifier que la 2FA est bien désactivée
        self.assertFalse(self.user.has_2fa_enabled())
        self.assertFalse(TOTPDevice.objects.filter(user=self.user).exists()) 