# TODO: Ajouter la validation du format du numéro de téléphone
# FIXME: Optimiser la génération du numéro Fidelys pour éviter les doublons
# BUG: Les superusers n'ont pas de numéro Fidelys par défaut
# TODO: Ajouter un champ pour le type de compte (particulier/professionnel)
# FIXME: Le champ is_verified est redondant avec la méthode is_verified()
# BUG: Risque de collision pour la génération du numéro Fidelys
# TODO: Ajouter la validation du format du code postal
# FIXME: Ajouter un champ pour les instructions de livraison
# TODO: Ajouter un système de rate limiting pour les tentatives de code
# FIXME: Réduire la durée de validité du code à 3 minutes

import random

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.timezone import now
from phonenumber_field.modelfields import PhoneNumberField
from .utils.validators import validate_password
import random
import uuid

from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
from django_otp.plugins.otp_totp.models import TOTPDevice as BaseTOTPDevice
from django.contrib.auth import get_user_model


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('L\'adresse email est obligatoire'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **kwargs):
        kwargs["is_staff"] = True
        kwargs["is_superuser"] = True
        kwargs["is_active"] = True
        return self.create_user(email=email, password=password, **kwargs)


class Shopper(AbstractUser):
    username = None
    email = models.EmailField(max_length=240, unique=True, verbose_name="Adresse email")
    phone = PhoneNumberField(verbose_name=_("Numéro de téléphone"), null=True, blank=True)
    address = models.TextField(verbose_name=_("Adresse"), null=True, blank=True)
    city = models.CharField(max_length=100, verbose_name=_("Ville"), null=True, blank=True)
    country = models.CharField(max_length=100, verbose_name=_("Pays"), null=True, blank=True)
    postal_code = models.CharField(max_length=20, verbose_name=_("Code postal"), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()
    fidelys_number = models.CharField(max_length=240, null=True, blank=True, unique=True, verbose_name="Numéro Fidelys")
    profile_picture = models.ImageField(
        upload_to='profile_pics/%Y/%m/%d/',
        storage=default_storage,
        blank=True,
        null=True,
        help_text="Photo de profil de l'utilisateur"
    )
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Date de naissance")
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def get_email(self):
        """Retourne l'email de l'utilisateur ou une chaîne vide pour l'utilisateur anonyme."""
        return self.email if hasattr(self, 'email') else ''

    def save(self, *args, **kwargs):
        if not self.fidelys_number:
            self.fidelys_number = ''.join(str(random.randint(0, 9)) for _ in range(7))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email if hasattr(self, 'email') else ''

    def get_totp_device(self):
        """Récupère un appareil TOTP actif de l'utilisateur."""
        return TOTPDevice.objects.filter(
            user=self,
            confirmed=True
        ).first()

    def has_2fa_enabled(self):
        """Vérifie si l'utilisateur a activé la 2FA."""
        return TOTPDevice.objects.filter(user=self, confirmed=True).exists()

    def enable_2fa(self):
        """Active la 2FA pour l'utilisateur."""
        # Créer un nouvel appareil
        device = TOTPDevice.objects.create(
            user=self,
            name=f'Device {TOTPDevice.objects.filter(user=self).count() + 1}',
            confirmed=False  # L'appareil doit être confirmé après vérification
        )
        return device

    def disable_2fa(self, token):
        """Désactive la 2FA pour l'utilisateur après vérification du token."""
        device = self.get_totp_device()
        if device and device.verify_token(token):
            device.delete()
            return True
        return False

    def verify_2fa_code(self, code):
        """Vérifie un code 2FA sur n'importe quel appareil actif."""
        devices = TOTPDevice.objects.filter(user=self, confirmed=True)
        for device in devices:
            if device.verify_token(code):
                return True
        return False

    def is_verified(self):
        """Vérifie si l'utilisateur est vérifié via 2FA."""
        return getattr(self, '_otp_verified', False)

    def set_verified(self, verified=True):
        """Définit l'état de vérification 2FA de l'utilisateur."""
        self._otp_verified = verified

    def sync_admin_totp(self):
        """Synchronise l'appareil TOTP avec celui de l'admin si l'utilisateur est admin."""
        if self.is_staff:
            from django.contrib.admin.models import LogEntry
            admin_device = LogEntry.objects.filter(
                user_id=self.id,
                action_flag=1  # Action de connexion réussie
            ).exists()
            if admin_device:
                device = self.get_totp_device()
                if not device or not device.confirmed:
                    if device:
                        device.delete()
                    device = TOTPDevice.objects.create(
                        user=self,
                        name='default',
                        confirmed=True,
                        key=self.get_totp_device().key if hasattr(self, 'get_totp_device') else None
                    )
                return device
        return None


LOYALTY_LEVEL_CHOICES = [
    ("Bronze", "Bronze"),
    ("Argent", "Argent"),
    ("Or", "Or"),
    ("Diamant", "Diamant"),
]


class LoyaltyHistory(models.Model):
    user = models.ForeignKey(Shopper, on_delete=models.CASCADE, related_name="loyalty_history")
    loyalty_points = models.PositiveIntegerField(default=0)
    loyalty_level = models.CharField(max_length=20, choices=LOYALTY_LEVEL_CHOICES)
    total_spent = models.FloatField(default=0)
    total_orders = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name = "Historique fidélité"
        verbose_name_plural = "Historique fidélité"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.loyalty_level} - {self.loyalty_points} pts"


class ShippingAddress(models.Model):
    CITY_CHOICES = [
        ('BKO', 'Bamako'),
        ('KAY', 'Kayes'),
        ('KOU', 'Koulikoro'),
        ('SIK', 'Sikasso'),
        ('SEG', 'Ségou'),
        ('MOP', 'Mopti'),
        ('TOM', 'Tombouctou'),
        ('GAO', 'Gao'),
        ('KID', 'Kidal'),
        ('MEN', 'Ménaka'),
        ('TAO', 'Taoudénit'),
    ]

    ADDRESS_TYPE_CHOICES = [
        ('DOM', 'Domicile'),
        ('BUR', 'Bureau'),
        ('AUT', 'Autre'),
    ]
    user = models.ForeignKey(Shopper, on_delete=models.CASCADE, related_name="shipping_addresses")
    full_name = models.CharField(max_length=100, verbose_name="Nom complet", help_text="ex: mahi watara", blank=True,
                                 null=True)
    address_type = models.CharField(max_length=3, choices=ADDRESS_TYPE_CHOICES, default='DOM',
                                    verbose_name="Type d'adresse", help_text="ex: Domicile, Bureau, Autre", blank=True, null=True)
    quarter = models.CharField(max_length=100, verbose_name="Quartier", help_text="ex: Hamdallaye ACI 2000")
    street_address = models.CharField(max_length=255, verbose_name="Adresse", help_text="ex: Rue 123, porte 456")
    city = models.CharField(max_length=3, choices=CITY_CHOICES, verbose_name="Ville", default="BKO")
    additional_info = models.CharField(max_length=255, blank=True, null=True,
                                       verbose_name="Informations complémentaires",
                                       help_text="ex: Bâtiment, étage, etc.")
    is_default = models.BooleanField(default=False, verbose_name="Adresse par défaut")

    class Meta:
        verbose_name = "Adresse de livraison"
        verbose_name_plural = "Adresses de livraison"

    def save(self, *args, **kwargs):
        # Si c'est une nouvelle adresse (pas encore enregistrée)
        if not self.pk:
            # Si c'est la première adresse de l'utilisateur ou si l'utilisateur a choisi de la définir par défaut
            if not ShippingAddress.objects.filter(user=self.user).exists() or self.is_default:
                # Mettre à False toutes les autres adresses de l'utilisateur
                ShippingAddress.objects.filter(user=self.user).update(is_default=False)
                # Définir cette adresse comme adresse par défaut
                self.is_default = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.full_name} - {self.street_address} - {self.city}'


class TwoFactorCode(models.Model):
    user = models.ForeignKey(Shopper, on_delete=models.CASCADE, related_name='two_factor_codes', default=1)
    code = models.CharField(max_length=6)
    reset_token = models.CharField(max_length=64, null=True, blank=True)
    uidb64 = models.CharField(max_length=64, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() < self.created_at + timedelta(minutes=5)  # Expire après 5 minutes

    @staticmethod
    def generate_code():
        return str(random.randint(100000, 999999))  # Code à 6 chiffres

    @staticmethod
    def generate_reset_token():
        return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=64))


class TOTPDevice(BaseTOTPDevice):
    # Ce modèle étend le modèle TOTPDevice de django_otp.plugins.otp_totp
    # pour gérer la liaison entre un utilisateur Django et son appareil OTP
    pass


class AllowedIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    description = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='added_ips'
    )

    class Meta:
        verbose_name = 'IP autorisée'
        verbose_name_plural = 'IPs autorisées'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.ip_address} ({self.description})"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=30)
        super().save(*args, **kwargs)


