from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.db.models.signals import pre_save, post_delete
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

    class Meta:
        app_label = 'product'
        verbose_name = 'Méthode de livraison'
        verbose_name_plural = 'Méthodes de livraison'

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

    def get_all_parent_ids(self):
        """Récupère récursivement tous les IDs des catégories parents"""
        ids = []
        if self.parent:
            ids.append(self.parent.id)
            ids.extend(self.parent.get_all_parent_ids())
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
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)
    description = models.TextField(verbose_name='Description', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Prix')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products', verbose_name='Catégorie')
    supplier = models.ForeignKey('suppliers.Supplier', on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name='Fournisseur')
    brand = models.CharField(max_length=100, blank=True, null=True, verbose_name='Marque')
    is_available = models.BooleanField(default=True, verbose_name='Disponible')
    is_salam = models.BooleanField(default=False, verbose_name='Produit Salam')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(
        upload_to=get_product_main_image_upload_path,
        storage=ProductImageStorage(),
        null=True,
        blank=True,
        verbose_name='Image principale'
    )
    image_urls = models.JSONField(default=dict, blank=True, null=True, verbose_name='URLs des images')
    sku = models.CharField(max_length=50, unique=True, default='SKU-0000', verbose_name='SKU')
    stock = models.PositiveIntegerField(default=0, verbose_name='Stock')
    specifications = models.JSONField(default=dict, blank=True, null=True, verbose_name='Spécifications')
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='Poids (kg)')
    dimensions = models.CharField(max_length=50, blank=True, null=True, verbose_name='Dimensions')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'

    def __str__(self):
        return self.title

    def _remove_file_suffix(self, filename):
        """Supprime le suffixe numérique du nom de fichier (ex: _12)"""
        if not filename:
            return filename
        # Trouve le dernier point avant l'extension
        last_dot = filename.rfind('.')
        if last_dot == -1:
            return filename
        
        # Trouve le dernier underscore avant l'extension
        last_underscore = filename.rfind('_', 0, last_dot)
        if last_underscore == -1:
            return filename
        
        # Vérifie si le suffixe est numérique
        suffix = filename[last_underscore + 1:last_dot]
        if suffix.isdigit():
            # Retourne le nom de fichier sans le suffixe
            return filename[:last_underscore] + filename[last_dot:]
        
        return filename

    def _normalize_image_path(self, path):
        """Normalise le chemin de l'image pour stocker uniquement la partie relative après media/products/"""
        if not path:
            return ''
        
        # Supprimer le préfixe media/products/ s'il existe
        if 'media/products/' in path:
            path = path.split('media/products/')[-1]
        
        # Supprimer tout préfixe media/ s'il reste
        if path.startswith('media/'):
            path = path[6:]
        
        # Supprimer le suffixe numérique du nom de fichier
        path_parts = path.split('/')
        if path_parts:
            filename = path_parts[-1]
            path_parts[-1] = self._remove_file_suffix(filename)
            path = '/'.join(path_parts)
        
        return path

    def _get_relative_path(self, image, image_type='main'):
        """Obtient le chemin relatif d'une image"""
        if not image:
            return None
        try:
            # Utilise la fonction appropriée selon le type d'image
            if image_type == 'main':
                path = get_product_main_image_upload_path(self, image.name)
            else:
                path = get_product_gallery_image_upload_path(self, image.name)
            
            # Conserve le préfixe media/products/ pour l'accès aux images
            return path
        except Exception as e:
            logger.error(f"Erreur lors de la génération du chemin relatif: {str(e)}")
            return None

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self.title, Product)
        
        # Mettre à jour image_urls si une image principale est définie
        if self.image:
            if not self.image_urls:
                self.image_urls = {}
            # Utilise le chemin final après l'ajout du numéro par le stockage
            storage = ProductImageStorage()
            path = get_product_main_image_upload_path(self, self.image.name)
            final_path = storage.get_available_name(path)
            # Ajoute le préfixe media/products/
            self.image_urls['main'] = f"media/products/{final_path}"
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product:product_detail', args=[self.id])

    def get_highlights(self):
        if self.specifications:
            return self.specifications.get('highlights', [])
        return []

    def get_main_image_url(self):
        """Retourne l'URL complète de l'image principale"""
        if self.image:
            return self.image.url
        if self.image_urls and 'main' in self.image_urls:
            storage = ProductImageStorage()
            return storage.url(self.image_urls['main'])
        return None

    def get_gallery_urls(self):
        """Retourne la liste des URLs complètes de la galerie"""
        if self.image_urls and 'gallery' in self.image_urls:
            storage = ProductImageStorage()
            return [storage.url(url) for url in self.image_urls['gallery']]
        return None

    def get_all_image_urls(self):
        """Retourne un dictionnaire avec toutes les URLs d'images"""
        urls = {}
        if main_url := self.get_main_image_url():
            urls['main'] = main_url
        if gallery_urls := self.get_gallery_urls():
            urls['gallery'] = gallery_urls
        return urls

    def update_image_urls(self):
        """Met à jour le champ image_urls avec les chemins des images"""
        if not self.image_urls:
            self.image_urls = {}
        
        # Mettre à jour le chemin de l'image principale
        if self.image:
            storage = ProductImageStorage()
            path = get_product_main_image_upload_path(self, self.image.name)
            final_path = storage.get_available_name(path)
            # Ajoute le préfixe media/products/
            self.image_urls['main'] = f"media/products/{final_path}"
        else:
            # Supprimer l'URL de l'image principale si elle n'existe plus
            self.image_urls.pop('main', None)
        
        # Mettre à jour les chemins de la galerie
        gallery_urls = set()  # Utiliser un set pour éviter les doublons
        for image in self.images.all().order_by('ordre'):
            if image.image:
                storage = ProductImageStorage()
                path = get_product_gallery_image_upload_path(self, image.image.name)
                final_path = storage.get_available_name(path)
                # Ajoute le préfixe media/products/
                gallery_urls.add(f"media/products/{final_path}")
        
        # Mettre à jour ou supprimer la galerie
        if gallery_urls:
            self.image_urls['gallery'] = list(gallery_urls)  # Convertir le set en liste
        else:
            self.image_urls.pop('gallery', None)
        
        self.save(update_fields=['image_urls'])

    def _get_s3_url(self, relative_path):
        """Construit l'URL S3 complète à partir du chemin relatif"""
        if not relative_path:
            return None
        try:
            storage = ProductImageStorage()
            # Le chemin contient déjà media/products/, donc on l'utilise directement
            return storage.url(relative_path)
        except Exception as e:
            logger.error(f"Erreur lors de la construction de l'URL S3: {str(e)}")
            return None

    def delete(self, *args, **kwargs):
        """Supprime le produit et ses images associées"""
        # Sauvegarder une référence à l'image avant la suppression
        image_to_delete = self.image
        
        # Supprimer l'instance
        super().delete(*args, **kwargs)
        
        # Supprimer l'image du stockage après la suppression de l'instance
        if image_to_delete:
            try:
                storage = ProductImageStorage()
                storage.delete(image_to_delete.name)
            except Exception as e:
                logger.error(f"Erreur lors de la suppression de l'image principale: {str(e)}")


@receiver(post_delete, sender=Product)
def handle_product_deletion(sender, instance, **kwargs):
    """Gère la suppression d'un produit et de ses images associées"""
    try:
        # Supprimer l'image principale si elle existe
        if instance.image:
            storage = ProductImageStorage()
            storage.delete(instance.image.name)
        
        # Supprimer les images de la galerie
        for image in instance.images.all():
            if image.image:
                storage = ProductImageStorage()
                storage.delete(image.image.name)
        
        # Réinitialiser image_urls
        if instance.image_urls:
            instance.image_urls = {}
            instance.save(update_fields=['image_urls'])
    except Exception as e:
        logger.error(f"Erreur lors de la suppression des images du produit: {str(e)}")


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
        
        # Mettre à jour image_urls du produit
        if self.image:
            self.product.update_image_urls()

    def delete(self, *args, **kwargs):
        # Sauvegarder une référence au produit avant la suppression
        product = self.product
        
        # Supprimer l'image du stockage
        if self.image:
            storage = ProductImageStorage()
            storage.delete(self.image.name)
        
        # Supprimer l'instance
        super().delete(*args, **kwargs)
        
        # Mettre à jour image_urls du produit après la suppression
        product.refresh_from_db()  # Rafraîchir pour avoir l'état actuel
        product.update_image_urls()

    def get_image_url(self):
        """Retourne l'URL de l'image"""
        if self.image:
            return self.image.url
        return None


@receiver(post_delete, sender=ImageProduct)
def update_product_image_urls_on_delete(sender, instance, **kwargs):
    """Met à jour les URLs des images du produit après la suppression d'une image"""
    if instance.product:
        instance.product.update_image_urls()


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


