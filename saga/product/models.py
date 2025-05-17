from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver
from suppliers.models import Supplier
from saga.utils.image_optimizer import ImageOptimizer
from saga.utils.path_utils import get_product_image_path
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .utils import generate_unique_slug
from decimal import Decimal
import logging
import os
import boto3
from storages.backends.s3boto3 import S3Boto3Storage
from saga.storage_backends import ProductImageStorage
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)


class ShippingMethod(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    min_delivery_days = models.PositiveSmallIntegerField()
    max_delivery_days = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name

    def get_delivery_time(self):
        return f"{self.min_delivery_days} - {self.max_delivery_days} jours"

    def get_price(self):
        return f"{self.price} €"

    def get_shipping_method(self):
        return f"{self.name}"


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to='categories/%Y/%m/%d/',
        storage=default_storage,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Nettoyage et normalisation du nom
        self.name = self.name.strip().title()

        # Génération automatique du slug si vide
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def get_all_children_ids(self):
        """Récupère récursivement les IDs de toutes les sous-catégories"""
        ids = [self.id]
        for child in self.children.all():
            ids.extend(child.get_all_children_ids())
        return ids

    def get_all_children(self):
        """Récupère récursivement toutes les sous-catégories"""
        categories = [self]
        for child in self.children.all():
            categories.extend(child.get_all_children())
        return categories

    @property
    def product_count(self):
        """Retourne le nombre total de produits dans cette catégorie et ses sous-catégories"""
        category_ids = self.get_all_children_ids()
        return Product.objects.filter(category_id__in=category_ids).count()

    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'

    def get_full_path(self):
        path = [self.name]
        parent = self.parent
        while parent:
            path.append(parent.name)
            parent = parent.parent
        return ' > '.join(reversed(path))


def get_product_main_image_upload_path(instance, filename):
    return get_product_image_path(instance, filename, 'main')

def get_product_gallery_image_upload_path(instance, filename):
    return get_product_image_path(instance, filename, 'gallery')

class Product(models.Model):
    title = models.CharField(max_length=200, verbose_name='Titre')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='Prix')
    description = models.TextField(verbose_name='Description', blank=True, null=True)
    highlight = models.TextField(verbose_name='Points forts', blank=True, null=True)
    image = models.ImageField(
        upload_to=get_product_main_image_upload_path,
        storage=ProductImageStorage(),
        null=True,
        blank=True
    )
    image_urls = models.JSONField(default=dict, blank=True, null=True, verbose_name='URLs des images')
    supplier = models.ForeignKey('suppliers.Supplier', on_delete=models.SET_NULL, related_name='products', null=True, blank=True)
    stripe_product_id = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    disponible_salam = models.BooleanField(default=False, verbose_name='Disponible en Salam')
    stock = models.PositiveIntegerField(default=0, verbose_name='Stock')
    sku = models.CharField(max_length=100, unique=True, verbose_name='SKU', default='SKU-0000')
    color = models.ForeignKey('Color', on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)

    class Meta:
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'
        ordering = ['-created_at']
        unique_together = [['title', 'category']]

    def __str__(self):
        return self.title

    def clean(self):
        if Product.objects.filter(title=self.title, category=self.category).exclude(pk=self.pk).exists():
            raise ValidationError(
                {'title': 'Un produit avec ce titre existe déjà dans cette catégorie.'}
            )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        if self.image:
            logger.info(f"Début du traitement de l'image pour le produit {self.title}")
            
            # Créer une instance de ProductImageStorage
            storage = ProductImageStorage()
            
            # Lire le contenu du fichier
            image_content = self.image.read()
            logger.info(f"Image lue, taille: {len(image_content)} bytes")
            
            # Optimiser l'image principale avec suppression du fond
            optimizer = ImageOptimizer()
            
            # Forcer la suppression du fond pour l'image principale
            img = Image.open(BytesIO(image_content))
            output = optimizer.remove_background(img)
            if output:
                main_content = output
                logger.info("Fond supprimé avec succès")
            else:
                main_content = BytesIO(image_content)
                logger.info("Utilisation de l'image originale (pas de suppression de fond)")
            
            # Générer le chemin
            main_path = get_product_image_path(self, self.image.name, 'main')
            logger.info(f"Chemin généré - Main: {main_path}")
            
            # Sauvegarder l'image principale optimisée
            storage.save(main_path, ContentFile(main_content.getvalue()))
            self.image.name = main_path
            logger.info("Image principale sauvegardée")
            
            # Mettre à jour les URLs dans image_urls
            self.image_urls = {
                'main': storage.url(main_path)
            }
            logger.info(f"URL mise à jour: {self.image_urls}")
            
            # Supprimer l'ancienne image si elle existe
            if self.pk:
                old_instance = Product.objects.get(pk=self.pk)
                if old_instance.image and old_instance.image != self.image:
                    storage.delete(old_instance.image.name)
                    logger.info("Ancienne image supprimée")
        
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Supprimer l'image du stockage
        if self.image:
            storage = ProductImageStorage()
            storage.delete(self.image.name)
        super().delete(*args, **kwargs)

    def get_highlights(self):
        if self.highlight:
            return self.highlight.splitlines()
        return []

    def get_image_url(self):
        """Retourne l'URL de l'image principale"""
        if self.image:
            return self.image.url
        return None

    def get_thumbnail_url(self):
        """Retourne l'URL de la miniature"""
        if self.image_urls and 'thumb' in self.image_urls:
            return self.image_urls['thumb']
        return None

    def save_image(self, image_file, image_type='main'):
        """
        Sauvegarde une image pour le produit.
        
        Args:
            image_file: Le fichier image à sauvegarder
            image_type: Le type d'image ('main', 'thumb', ou 'gallery')
        """
        if not image_file:
            return None
            
        # Créer une instance de ProductImageStorage
        storage = ProductImageStorage()
        
        # Générer le chemin de l'image
        filename = os.path.basename(image_file.name)
        path = get_product_image_path(self, filename, image_type)
        
        # Sauvegarder l'image
        storage.save(path, image_file)
        
        # Si c'est une image principale, créer la miniature
        if image_type == 'main':
            self.create_thumbnail(image_file)
            
        return path

    def create_thumbnail(self, image_file):
        """
        Crée une miniature à partir de l'image principale.
        
        Args:
            image_file: Le fichier image source
        """
        try:
            # Créer une instance de ProductImageStorage
            storage = ProductImageStorage()
            
            # Ouvrir l'image
            img = Image.open(image_file)
            
            # Convertir en RGB si nécessaire
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            
            # Redimensionner l'image
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            
            # Optimiser l'image
            optimizer = ImageOptimizer()
            img = optimizer.optimize_image(img)
            
            # Sauvegarder la miniature
            thumb_io = BytesIO()
            img.save(thumb_io, format='JPEG', quality=85)
            thumb_io.seek(0)
            
            # Générer le chemin de la miniature
            filename = os.path.basename(image_file.name)
            thumb_path = get_product_image_path(self, filename, 'thumb')
            
            # Sauvegarder la miniature
            storage.save(thumb_path, ContentFile(thumb_io.getvalue()))
            
            return thumb_path
            
        except Exception as e:
            print(f"Erreur lors de la création de la miniature : {str(e)}")
            return None


class Color(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=7)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Nettoyage et normalisation du nom
        self.name = self.name.strip().title()
        super().save(*args, **kwargs)

    def get_hex_code(self):
        return self.code

    def get_rgb_code(self):
        return tuple(int(self.code.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))

    @property
    def first_word(self):
        """Retourne le premier mot du nom de la couleur"""
        if not self.name:
            return ''
        return self.name.split()[0].strip()


class Size(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Nettoyage et normalisation du nom
        self.name = self.name.strip().title()
        super().save(*args, **kwargs)


class Clothing(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='clothing_product')
    GENDER_CHOICES = [
        ('H', 'Homme'),
        ('F', 'Femme'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    size = models.ManyToManyField(Size, related_name='clothing_size', blank=True)
    color = models.ManyToManyField(Color, related_name='clothing_color', blank=True)

    def __str__(self):
        return self.product.title


class CulturalItem(models.Model):  # Espace Culturel
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='cultural_product')
    author = models.CharField(max_length=255, blank=True, null=True)  # Auteur
    isbn = models.CharField(max_length=20, blank=True, null=True)  # ISBN
    date = models.DateField(blank=True, null=True)  # Date de publication

    def __str__(self):
        return self.product.title

    def save(self, *args, **kwargs):
        # Nettoyage et normalisation de l'auteur
        if self.author:
            self.author = self.author.strip().title()
        super().save(*args, **kwargs)


class ImageProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(
        upload_to=get_product_gallery_image_upload_path,
        storage=ProductImageStorage(),
        null=True,
        blank=True
    )
    ordre = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ordre', 'created_at']
        verbose_name = 'Image produit'
        verbose_name_plural = 'Images produit'

    def __str__(self):
        return f"Image {self.ordre} pour {self.product.title}"

    def save(self, *args, **kwargs):
        if self.image and self.pk:
            # Supprimer l'ancienne image si elle existe
            old_instance = ImageProduct.objects.get(pk=self.pk)
            if old_instance.image and old_instance.image != self.image:
                storage = ProductImageStorage()
                storage.delete(old_instance.image.name)
        
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Supprimer l'image du stockage
        if self.image:
            storage = ProductImageStorage()
            storage.delete(self.image.name)
        super().delete(*args, **kwargs)

    def get_image_url(self):
        """Retourne l'URL de l'image"""
        if self.image:
            return self.image.url
        return None


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('accounts.Shopper', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        ordering = ['-created_at']
        unique_together = ['product', 'user']

    def __str__(self):
        return f"Avis de {self.user} sur {self.product}"


class Phone(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    brand = models.CharField(max_length=100, default='Inconnu')
    model = models.CharField(max_length=100, default='Inconnu')
    operating_system = models.CharField(max_length=50, default='Android')
    screen_size = models.DecimalField(max_digits=4, decimal_places=2, default=6.0)
    resolution = models.CharField(max_length=100, blank=True, null=True)
    processor = models.CharField(max_length=100, default='Inconnu')
    battery_capacity = models.IntegerField(help_text="Capacité de la batterie en mAh", default=3000)
    camera_main = models.CharField(max_length=100, verbose_name="Caméra principale", default='Inconnue')
    camera_front = models.CharField(max_length=100, verbose_name="Caméra frontale", default='Inconnue')
    network = models.CharField(max_length=100, default='4G')
    warranty = models.CharField(max_length=100, default='12 mois')
    imei = models.CharField(max_length=15, unique=True, null=True, blank=True)
    is_new = models.BooleanField(default=True)
    box_included = models.BooleanField(default=True)
    accessories = models.TextField(blank=True, null=True)
    storage = models.IntegerField(help_text="Capacité de stockage en GB", default=64)
    ram = models.IntegerField(help_text="RAM en GB", default=4)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = "Téléphone"
        verbose_name_plural = "Téléphones"

    def __str__(self):
        return f"{self.brand} {self.model}"


