from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.urls import reverse
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
from django.db.models import Avg, Count

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
        storage=ProductImageStorage(),
        blank=True,
        null=True,
        help_text="Image de la catégorie"
    )
    description = models.TextField(blank=True, null=True)
    color = models.CharField(
        max_length=20,
        default='blue',
        choices=[
            ('blue', 'Bleu'),
            ('purple', 'Violet'),
            ('yellow', 'Jaune'),
            ('red', 'Rouge'),
            ('green', 'Vert'),
            ('indigo', 'Indigo'),
            ('pink', 'Rose'),
        ]
    )
    is_main = models.BooleanField(
        default=False,
        help_text="Indique si c'est une catégorie principale"
    )
    order = models.PositiveIntegerField(default=0, help_text="Ordre d'affichage")
    
    # Nouveaux champs
    category_type = models.CharField(
        max_length=20,
        choices=[
            ('MODEL', 'Catégorie liée à un modèle'),
            ('FILTER', 'Catégorie avec filtres'),
            ('MARKETING', 'Catégorie marketing'),
        ],
        default='MODEL',
        help_text="Type de catégorie",
        blank=True,
        null=True
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Modèle lié à cette catégorie",
        limit_choices_to={
            'app_label__in': ['product', 'suppliers'],
            'model__in': ['phone', 'clothing', 'fabric', 'culturalitem', 'product']
        }
    )
    filter_criteria = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        help_text="Critères de filtrage pour les sous-catégories"
    )

    def __str__(self):
        return self.name

    @classmethod
    def get_all_products_category(cls):
        """Retourne la catégorie 'Tous les produits' ou la crée si elle n'existe pas."""
        category, created = cls.objects.get_or_create(
            slug='tous-les-produits',
            defaults={
                'name': 'Tous les produits',
                'is_main': True,
                'category_type': 'MODEL',
                'color': 'green',
                'order': 0,
                'description': 'Découvrez tous nos produits disponibles sur la plateforme.'
            }
        )
        return category

    def get_products(self):
        """Retourne les produits de la catégorie."""
        if self.slug == 'tous-les-produits':
            return Product.objects.filter(
                is_available=True
            ).select_related(
                'phone',
                'phone__color',
                'supplier',
                'category',
                'fabric_product',
                'clothing_product',
                'cultural_product'
            )
        else:
            category_ids = self.get_all_children_ids()
            return Product.objects.filter(
                category_id__in=category_ids,
                is_available=True
            ).select_related(
                'phone',
                'phone__color',
                'supplier',
                'category',
                'fabric_product',
                'clothing_product',
                'cultural_product'
            )

    def delete(self, *args, **kwargs):
        """Supprime la catégorie et son image associée"""
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
                logger.error(f"Erreur lors de la suppression de l'image de la catégorie: {str(e)}")

    def save(self, *args, **kwargs):
        # Nettoyage et normalisation du nom
        self.name = self.name.strip().title()

        # Génération automatique du slug si vide
        if not self.slug:
            self.slug = slugify(self.name)
        elif self.slug != slugify(self.name):
            # Si le nom a changé, mettre à jour le slug
            self.slug = slugify(self.name)

        # Validation de la cohérence des champs uniquement pour les nouvelles catégories
        if not self.pk:  # Nouvelle catégorie
            if self.is_main and not self.content_type:
                raise ValidationError("Une catégorie principale doit avoir un modèle lié")
            
            if self.category_type == 'FILTER' and not self.filter_criteria:
                raise ValidationError("Une catégorie de type FILTER doit avoir des critères de filtrage")

        # Gestion de l'image
        if self.image and self.pk:
            try:
                old_instance = Category.objects.get(pk=self.pk)
                if old_instance.image and old_instance.image != self.image:
                    storage = ProductImageStorage()
                    storage.delete(old_instance.image.name)
            except Category.DoesNotExist:
                pass

        super().save(*args, **kwargs)

    def get_model_class(self):
        """Retourne la classe du modèle lié"""
        if self.content_type:
            return self.content_type.model_class()
        return None

    def get_filtered_queryset(self):
        """Retourne le queryset filtré selon les critères"""
        if not self.is_main and self.parent and self.filter_criteria:
            model_class = self.parent.get_model_class()
            if model_class:
                queryset = model_class.objects.all()
                for field, value in self.filter_criteria.items():
                    queryset = queryset.filter(**{field: value})
                return queryset
        return None

    def get_all_children_ids(self):
        """Récupère récursivement les IDs de toutes les sous-catégories"""
        ids = [self.id]
        for child in self.children.all():
            ids.extend(child.get_all_children_ids())
        return ids

    def get_all_parent_ids(self):
        """Récupère récursivement tous les IDs des catégories parents"""
        ids = []
        current = self
        while current.parent:
            ids.append(current.parent.id)
            current = current.parent
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
        if self.slug == 'tous-les-produits':
            return Product.objects.filter(is_available=True).count()
        category_ids = self.get_all_children_ids()
        return Product.objects.filter(category_id__in=category_ids).count()

    def get_full_path(self):
        """Retourne le chemin complet de la catégorie"""
        path = [self.name]
        current = self.parent
        while current:
            path.insert(0, current.name)
            current = current.parent
        return ' > '.join(path)

    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering = ['order', 'name']


def get_product_main_image_upload_path(instance, filename):
    return get_product_image_path(instance, filename, 'main')

def get_product_gallery_image_upload_path(instance, filename):
    return get_product_image_path(instance, filename, 'gallery')

class Product(models.Model):
    title = models.CharField(max_length=200, verbose_name='Titre')
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)
    description = models.TextField(verbose_name='Description', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='Prix (FCFA)')
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
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name='SKU')
    stock = models.PositiveIntegerField(default=0, verbose_name='Stock')
    specifications = models.JSONField(default=dict, blank=True, null=True, verbose_name='Spécifications')
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='Poids (kg)')
    dimensions = models.CharField(max_length=50, blank=True, null=True, verbose_name='Dimensions')
    shipping_methods = models.ManyToManyField(ShippingMethod, related_name='products', blank=True, verbose_name='Méthodes de livraison')

    # Nouveaux champs pour les filtres
    condition = models.CharField(max_length=20, choices=[
        ('new', 'Neuf'),
        ('used', 'Occasion'),
        ('refurbished', 'Reconditionné')
    ], null=True, blank=True, verbose_name='État du produit')
    
    has_warranty = models.BooleanField(default=False, verbose_name='Garantie')
    discount_price = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True, verbose_name='Prix promotionnel (FCFA)')
    is_trending = models.BooleanField(default=False, verbose_name='Produit tendance')
    sales_count = models.IntegerField(default=0, verbose_name='Nombre de ventes')

    def get_average_rating(self):
        """Calcule la moyenne des notes à partir des avis"""
        return self.reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    def get_review_count(self):
        """Retourne le nombre total d'avis"""
        return self.reviews.count()

    def get_ratings_distribution(self):
        """Retourne la distribution des notes"""
        return self.reviews.values('rating').annotate(
            count=Count('id')
        ).order_by('rating')

    # Méthodes pour le système de stock simplifié
    def get_stock_status(self):
        """Retourne le statut du stock selon le type de produit"""
        if self.is_salam:
            return {
                'status': 'salam',
                'message': 'Commande Salam - Livraison selon méthode configurée',
                'available': True,
                'delivery_days': None,
                'stock_type': 'salam'
            }
        else:
            if self.stock > 0:
                return {
                    'status': 'in_stock',
                    'message': f'En stock - {self.stock} disponible(s)',
                    'available': True,
                    'delivery_days': 3,
                    'stock_type': 'classic'
                }
            else:
                return {
                    'status': 'out_of_stock',
                    'message': 'Rupture de stock',
                    'available': False,
                    'delivery_days': None,
                    'stock_type': 'classic'
                }

    def can_order(self, quantity=1):
        """Vérifie si une commande peut être passée"""
        if self.is_salam:
            return True  # Salam = toujours possible
        else:
            return self.stock >= quantity

    def reserve_stock(self, quantity):
        """Réserve du stock pour une commande (uniquement pour les produits classiques)"""
        if not self.is_salam and self.stock >= quantity:
            self.stock -= quantity
            self.save()
            return True
        return False

    def release_stock(self, quantity):
        """Libère du stock réservé (uniquement pour les produits classiques)"""
        if not self.is_salam:
            self.stock += quantity
            self.save()
            return True
        return False

    def get_stock_display(self):
        """Retourne l'affichage du stock pour l'interface"""
        status = self.get_stock_status()
        return status['message']

    def has_stock(self):
        """Vérifie si le produit a du stock disponible"""
        if self.is_salam:
            return True  # Salam = toujours disponible
        else:
            return self.stock > 0

    def get_delivery_estimate(self):
        """Retourne l'estimation de délai de livraison"""
        status = self.get_stock_status()
        return status['delivery_days']

    class Meta:
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'
        ordering = ['-created_at']

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

    def generate_sku(self):
        """Génère un SKU unique pour le produit"""
        # Si c'est un produit de type tissu, on utilise le format spécial
        if hasattr(self, 'fabric_product'):
            fabric = self.fabric_product
            if fabric:
                # Obtenir le préfixe basé sur le type de tissu
                fabric_prefix = fabric.fabric_type[:3].upper()
                
                # Obtenir le préfixe de qualité
                quality_prefix = fabric.quality[:3].upper() if fabric.quality else "DEF"
                
                # Obtenir le dernier numéro utilisé pour ce type de tissu
                last_fabric = Fabric.objects.filter(
                    fabric_type=fabric.fabric_type
                ).order_by('-unique_id').first()
                
                if last_fabric and last_fabric.unique_id:
                    try:
                        last_number = int(last_fabric.unique_id.split('-')[-1])
                        new_number = last_number + 1
                    except (ValueError, IndexError):
                        new_number = 1
                else:
                    new_number = 1
                
                # Formater le numéro avec des zéros devant
                number_str = str(new_number).zfill(4)
                
                # Créer l'identifiant unique
                return f"{fabric_prefix}-{quality_prefix}-{number_str}"
        
        # Pour les autres types de produits, on utilise un format générique
        prefix = 'SKU'
        last_product = Product.objects.filter(
            sku__startswith=prefix
        ).order_by('-sku').first()
        
        if last_product and last_product.sku:
            try:
                last_number = int(last_product.sku.split('-')[-1])
                new_number = last_number + 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1
        
        return f"{prefix}-{str(new_number).zfill(4)}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Vérifier si le slug existe déjà
            if Product.objects.filter(slug=self.slug).exists():
                # Ajouter un suffixe numérique unique
                counter = 1
                while Product.objects.filter(slug=f"{self.slug}-{counter}").exists():
                    counter += 1
                self.slug = f"{self.slug}-{counter}"
        
        # Générer le SKU si nécessaire
        if not self.sku or self.sku == 'SKU-0000':
            self.sku = self.generate_sku()
        
        # Gestion de l'image principale
        if self.image and self.pk:
            try:
                old_instance = Product.objects.get(pk=self.pk)
                if old_instance.image and old_instance.image != self.image:
                    storage = ProductImageStorage()
                    storage.delete(old_instance.image.name)
            except Product.DoesNotExist:
                pass

        # Mettre à jour image_urls si une image principale est définie
        if self.image:
            if not self.image_urls:
                self.image_urls = {}
            storage = ProductImageStorage()
            path = get_product_main_image_upload_path(self, self.image.name)
            final_path = storage.get_available_name(path)
            self.image_urls['main'] = f"media/products/{final_path}"
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('price_checker:product_detail', args=[self.slug])

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

    def format_price(self):
        """Formate le prix en FCFA avec espace comme séparateur de milliers"""
        return f"{int(self.price):,}".replace(',', ' ') + ' FCFA'

    def format_discount_price(self):
        """Formate le prix promotionnel en FCFA avec espace comme séparateur de milliers"""
        if self.discount_price:
            return f"{int(self.discount_price):,}".replace(',', ' ') + ' FCFA'
        return None


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
        ('U', 'Unisexe'),
    ]
    
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    size = models.ManyToManyField(Size, related_name='clothing_size', blank=True)
    color = models.ManyToManyField(Color, related_name='clothing_color', blank=True)
    
    # Champs spécifiques aux vêtements industriels
    material = models.CharField(max_length=100, blank=True, null=True, help_text="Matériau du vêtement (coton, polyester, etc.)")
    style = models.CharField(max_length=100, blank=True, null=True, help_text="Style du vêtement (casual, formel, sport, etc.)")
    season = models.CharField(max_length=50, blank=True, null=True, help_text="Saison d'utilisation")
    care_instructions = models.TextField(blank=True, null=True, help_text="Instructions d'entretien")

    def __str__(self):
        return self.product.title

    class Meta:
        verbose_name = "Vêtement"
        verbose_name_plural = "Vêtements"


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

    class Meta:
        verbose_name = 'Livre et Culture'
        verbose_name_plural = 'Livres et Culture'


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
        # Gestion de l'image de la galerie
        if self.image and self.pk:
            try:
                old_instance = ImageProduct.objects.get(pk=self.pk)
                if old_instance.image and old_instance.image != self.image:
                    storage = ProductImageStorage()
                    storage.delete(old_instance.image.name)
            except ImageProduct.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Mettre à jour image_urls du produit après la sauvegarde
        if self.product:
            self.product.update_image_urls()

    def delete(self, *args, **kwargs):
        # Sauvegarder une référence au produit avant la suppression
        product = self.product
        
        # Supprimer l'image du stockage
        if self.image:
            try:
                storage = ProductImageStorage()
                storage.delete(self.image.name)
            except Exception as e:
                logger.error(f"Erreur lors de la suppression de l'image de la galerie: {str(e)}")
        
        # Supprimer l'instance
        super().delete(*args, **kwargs)
        
        # Mettre à jour image_urls du produit après la suppression
        if product:
            product.refresh_from_db()
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
    processor = models.CharField(max_length=100, default='Inconnu')
    battery_capacity = models.IntegerField(help_text="Capacité de la batterie en mAh", default=3000)
    camera_main = models.CharField(max_length=100, verbose_name="Caméra principale", default='Inconnue')
    camera_front = models.CharField(max_length=100, verbose_name="Caméra frontale", default='Inconnue')
    network = models.CharField(max_length=100, default='4G')
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


class Fabric(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='fabric_product')
    FABRIC_TYPES = [
        ('BAZIN', 'Bazin'),
        ('WAX', 'Wax'),
        ('KENTE', 'Kente'),
        ('BOGOLAN', 'Bogolan'),
        ('OTHER', 'Autre'),
    ]
    fabric_type = models.CharField(max_length=20, choices=FABRIC_TYPES, default='BAZIN')
    quality = models.CharField(max_length=100, default='Super Riche')
    length = models.DecimalField(max_digits=5, decimal_places=2, help_text="Longueur en mètres", default=3.0)
    width = models.DecimalField(max_digits=4, decimal_places=2, help_text="Largeur en mètres", default=1.5)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, blank=True)
    pattern = models.CharField(max_length=100, blank=True, null=True, help_text="Motif ou design du tissu")
    origin = models.CharField(max_length=100, blank=True, null=True, help_text="Pays d'origine du tissu")
    care_instructions = models.TextField(blank=True, null=True, help_text="Instructions d'entretien")
    unique_id = models.CharField(max_length=50, unique=True, blank=True, help_text="Identifiant unique du tissu")

    class Meta:
        verbose_name = "Tissu"
        verbose_name_plural = "Tissus"

    def __str__(self):
        return f"{self.get_fabric_type_display()} {self.quality} - {self.product.title}"

    def generate_unique_id(self):
        """Génère un identifiant unique pour le tissu"""
        # Obtenir le préfixe basé sur le type de tissu
        fabric_prefix = self.fabric_type[:3].upper()
        
        # Obtenir le préfixe de qualité
        quality_prefix = self.quality[:3].upper() if self.quality else "DEF"
        
        # Obtenir le dernier numéro utilisé pour ce type de tissu
        last_fabric = Fabric.objects.filter(
            fabric_type=self.fabric_type
        ).order_by('-unique_id').first()
        
        if last_fabric and last_fabric.unique_id:
            try:
                last_number = int(last_fabric.unique_id.split('-')[-1])
                new_number = last_number + 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1
        
        # Formater le numéro avec des zéros devant
        number_str = str(new_number).zfill(4)
        
        # Créer l'identifiant unique
        return f"{fabric_prefix}-{quality_prefix}-{number_str}"

    def save(self, *args, **kwargs):
        # Générer l'identifiant unique si nécessaire
        if not self.unique_id:
            self.unique_id = self.generate_unique_id()
        
        # Mettre à jour le SKU du produit associé seulement si le produit n'a pas de SKU
        if self.product and not self.product.sku:
            self.product.sku = self.unique_id
            self.product.save(update_fields=['sku'])
        
        super().save(*args, **kwargs)

    def get_price_per_meter(self):
        """Calcule le prix au mètre"""
        if self.length and self.product.discount_price:
            price = self.product.discount_price
        elif self.length and self.product.price:
            price = self.product.price
        else:
            return None
        return price / self.length


class Favorite(models.Model):
    """Modèle pour gérer les favoris des utilisateurs"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']
        verbose_name = 'Favori'
        verbose_name_plural = 'Favoris'

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"


