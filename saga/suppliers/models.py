from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.utils import timezone
import os
from django.core.files.storage import default_storage

# Create your models here.

SUPPLIER_SPECIALTY_CHOICES = [
    ('Fournisseur de TELEPHONE', 'Fournisseur de TELEPHONE'),
    ('Fournisseur de TELEVISION', 'Fournisseur de TELEVISION'),
]

class Supplier(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    address = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    website = models.URLField(blank=True, null=True)
    image = models.ImageField(
        upload_to='suppliers/%Y/%m/%d/',
        storage=default_storage,
        blank=True,
        null=True
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0
    )
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    specialty = models.CharField(max_length=100, choices=SUPPLIER_SPECIALTY_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.company_name or str(self.user)

    def save(self, *args, **kwargs):
        if not self.slug and self.company_name:
            self.slug = slugify(self.company_name)
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Fournisseur'
        verbose_name_plural = 'Fournisseurs'
        ordering = ['company_name']

