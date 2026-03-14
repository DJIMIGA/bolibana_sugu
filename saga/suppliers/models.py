from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.utils import timezone
import os
from django.core.files.storage import default_storage
from django.core.validators import FileExtensionValidator
from saga.storage_backends import HeroImageStorage
from saga.utils.image_optimizer import ImageOptimizer
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image
import logging

logger = logging.getLogger(__name__)

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

class HeroImage(models.Model):
    """Modèle pour gérer les images du hero"""
    hero = models.ForeignKey('Hero', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(
        upload_to='hero/',
        storage=HeroImageStorage(),
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
        verbose_name="Image"
    )
    ordre = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ordre', 'created_at']
        verbose_name = "Image du hero"
        verbose_name_plural = "Images du hero"

    def __str__(self):
        return f"Image {self.ordre} pour {self.hero.title}"

    def save(self, *args, **kwargs):
        # Gestion de l'image
        if self.image and self.pk:
            try:
                old_instance = HeroImage.objects.get(pk=self.pk)
                if old_instance.image and old_instance.image != self.image:
                    storage = HeroImageStorage()
                    storage.delete(old_instance.image.name)
            except HeroImage.DoesNotExist:
                pass

        # Optimisation de l'image
        if self.image and hasattr(self.image, 'file'):
            try:
                img = Image.open(self.image)
                
                # Redimensionner l'image si nécessaire (max 1920x1080)
                max_width = 1920
                max_height = 1080
                if img.width > max_width or img.height > max_height:
                    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                # Sauvegarder l'image optimisée
                output = BytesIO()
                img.save(output, format='JPEG', quality=85, optimize=True)
                output.seek(0)
                
                # Créer un nouveau fichier avec le contenu optimisé
                self.image.save(
                    os.path.basename(self.image.name),
                    ContentFile(output.getvalue()),
                    save=False
                )
            except Exception as e:
                logger.error(f"Erreur lors de l'optimisation de l'image du hero: {str(e)}")

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Sauvegarder une référence à l'image avant la suppression
        image_to_delete = self.image
        
        # Supprimer l'instance
        super().delete(*args, **kwargs)
        
        # Supprimer l'image du stockage après la suppression de l'instance
        if image_to_delete:
            try:
                storage = HeroImageStorage()
                storage.delete(image_to_delete.name)
            except Exception as e:
                logger.error(f"Erreur lors de la suppression de l'image du hero: {str(e)}")

class Hero(models.Model):
    """Modèle pour gérer les sections hero du site"""
    title = models.CharField(max_length=200, verbose_name="Titre")
    subtitle = models.TextField(verbose_name="Sous-titre")
    background_image = models.ImageField(
        upload_to='hero/',
        storage=HeroImageStorage(),
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
        verbose_name="Image d'arrière-plan",
        null=True,
        blank=True
    )
    primary_button_text = models.CharField(max_length=50, verbose_name="Texte du bouton principal")
    primary_button_url = models.CharField(max_length=200, verbose_name="URL du bouton principal")
    secondary_button_text = models.CharField(max_length=50, verbose_name="Texte du bouton secondaire")
    secondary_button_url = models.CharField(max_length=200, verbose_name="URL du bouton secondaire")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name = "Hero"
        verbose_name_plural = "Heros"
        ordering = ['-is_active', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"hero-{self.title}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({'Actif' if self.is_active else 'Inactif'})"

    @property
    def background_image(self):
        """Retourne l'image active du hero"""
        active_image = self.images.filter(is_active=True).first()
        return active_image.image if active_image else None

