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
        # on set les valeur sur notre dictionnaire
        kwargs["is_staff"] = True
        kwargs["is_superuser"] = True
        kwargs["is_active"] = True

        # on passe la dictionnaire a la fonction create_user
        return self.create_user(email=email, password=password, **kwargs)


class Shopper(AbstractUser):
    username = None
    email = models.EmailField(max_length=240, unique=True, verbose_name="Adresse email")
    phone_number = PhoneNumberField(null=True, blank=True, unique=True, help_text="ex: +223 76 00 00 00",
                                    verbose_name="Numéro de téléphone")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Date de naissance")
    fidelys_number = models.CharField(max_length=240, null=True, blank=True, unique=True, verbose_name="Numéro Fidelys")
    profile_picture = models.ImageField(
        upload_to='profile_pics/%Y/%m/%d/',
        storage=default_storage,
        blank=True,
        null=True,
        help_text="Photo de profil de l'utilisateur"
    )
    USERNAME_FIELD = "email"
    # d'autres champs requis en + de email
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if not self.fidelys_number:
            self.fidelys_number = ''.join(str(random.randint(0, 9)) for _ in range(7))
        super().save(*args, **kwargs)


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
        if self.is_default:
            # Désactiver toutes les autres adresses par défaut pour cet utilisateur
            ShippingAddress.objects.filter(user=self.user, is_default=True).update(is_default=False)
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


