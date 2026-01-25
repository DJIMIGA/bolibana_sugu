from django.test import TestCase, override_settings
from cryptography.fernet import Fernet

from inventory.models import ApiKey


class ApiKeyTestCase(TestCase):
    def test_get_active_key_from_db(self):
        encryption_key = Fernet.generate_key()
        original_key = 'test-api-key-123'

        with override_settings(INVENTORY_ENCRYPTION_KEY=encryption_key):
            api_key = ApiKey.objects.create(name='Clé active', is_active=True)
            api_key.set_key(original_key)
            api_key.save()

            self.assertEqual(ApiKey.get_active_key(), original_key)

    def test_get_active_key_fallback_on_decrypt_error(self):
        encryption_key = Fernet.generate_key()
        wrong_key = Fernet.generate_key()
        original_key = 'test-api-key-xyz'
        fallback_key = 'fallback-key-001'

        with override_settings(INVENTORY_ENCRYPTION_KEY=encryption_key):
            api_key = ApiKey.objects.create(name='Clé active', is_active=True)
            api_key.set_key(original_key)
            api_key.save()

        with override_settings(INVENTORY_ENCRYPTION_KEY=wrong_key, B2B_API_KEY=fallback_key):
            self.assertEqual(ApiKey.get_active_key(), fallback_key)

    def test_get_key_accepts_raw_fernet_token(self):
        encryption_key = Fernet.generate_key()
        original_key = 'raw-token-key-456'

        with override_settings(INVENTORY_ENCRYPTION_KEY=encryption_key):
            f = Fernet(encryption_key)
            raw_encrypted = f.encrypt(original_key.encode()).decode()

            api_key = ApiKey.objects.create(name='Clé brute', is_active=True)
            api_key.key_encrypted = raw_encrypted
            api_key.save(update_fields=['key_encrypted'])

            self.assertEqual(ApiKey.get_active_key(), original_key)

    def test_get_active_keys_returns_multiple(self):
        encryption_key = Fernet.generate_key()
        key_1 = 'key-001'
        key_2 = 'key-002'

        with override_settings(INVENTORY_ENCRYPTION_KEY=encryption_key):
            api_key_1 = ApiKey.objects.create(name='Key 1', is_active=True)
            api_key_1.set_key(key_1)
            api_key_1.save()

            api_key_2 = ApiKey.objects.create(name='Key 2', is_active=True)
            api_key_2.set_key(key_2)
            api_key_2.save()

            keys = ApiKey.get_active_keys()
            self.assertEqual(len(keys), 2)
            keys_values = {item['key'] for item in keys}
            self.assertIn(key_1, keys_values)
            self.assertIn(key_2, keys_values)
