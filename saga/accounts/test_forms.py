import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
from unittest import TestCase
from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from saga.accounts.forms import PasswordChangeForm

User = get_user_model()


class TestPasswordChangeForm(TestCase):
    def setUp(self):
        # Créez un utilisateur fictif pour les tests
        self.user = User.objects.create_user(username='testuser', password='old_password')

    def test_clean_current_password_valid(self):
        form_data = {
            'current_password': 'old_password',
            'new_password': 'NewPassword1!',
            'confirm_new_password': 'NewPassword1!'
        }
        form = PasswordChangeForm(user=self.user, data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['current_password'], 'old_password')

    def test_clean_current_password_invalid(self):
        form_data = {
            'current_password': 'wrong_password',
            'new_password': 'NewPassword1!',
            'confirm_new_password': 'NewPassword1!'
        }
        form = PasswordChangeForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('current_password', form.errors)
        self.assertEqual(form.errors['current_password'], [_("Mot de passe actuel invalide.")])

    def test_clean_new_password_too_short(self):
        form_data = {
            'current_password': 'old_password',
            'new_password': 'short',
            'confirm_new_password': 'short'
        }
        form = PasswordChangeForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_password', form.errors)
        self.assertEqual(form.errors['new_password'], [_("Le mot de passe doit contenir au moins 8 caractères.")])

    def test_clean_new_password_no_uppercase(self):
        form_data = {
            'current_password': 'old_password',
            'new_password': 'newpassword1!',
            'confirm_new_password': 'newpassword1!'
        }
        form = PasswordChangeForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_password', form.errors)
        self.assertEqual(form.errors['new_password'],
                         [_("Le mot de passe doit contenir au moins une lettre majuscule.")])

    def test_clean_new_password_no_lowercase(self):
        form_data = {
            'current_password': 'old_password',
            'new_password': 'NEWPASSWORD1!',
            'confirm_new_password': 'NEWPASSWORD1!'
        }
        form = PasswordChangeForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_password', form.errors)
        self.assertEqual(form.errors['new_password'],
                         [_("Le mot de passe doit contenir au moins une lettre minuscule.")])

    def test_clean_new_password_no_digit(self):
        form_data = {
            'current_password': 'old_password',
            'new_password': 'NewPassword!',
            'confirm_new_password': 'NewPassword!'
        }
        form = PasswordChangeForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_password', form.errors)
        self.assertEqual(form.errors['new_password'], [_("Le mot de passe doit contenir au moins un chiffre.")])

    def test_clean_new_password_no_special_char(self):
        form_data = {
            'current_password': 'old_password',
            'new_password': 'NewPassword1',
            'confirm_new_password': 'NewPassword1'
        }
        form = PasswordChangeForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_password', form.errors)
        self.assertEqual(form.errors['new_password'],
                         [_("Le mot de passe doit contenir au moins un caractère spécial.")])

    def test_clean_passwords_do_not_match(self):
        form_data = {
            'current_password': 'old_password',
            'new_password': 'NewPassword1!',
            'confirm_new_password': 'DifferentPassword1!'
        }
        form = PasswordChangeForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('non_field_errors', form.errors)
        self.assertEqual(form.errors['non_field_errors'], [_("Les nouveaux mots de passe ne correspondent pas.")])
