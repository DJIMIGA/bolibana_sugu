from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver
from cloudinary.models import CloudinaryField
from suppliers.models import Supplier
from saga.utils.image_optimizer import ImageOptimizer
from django.utils import timezone
from django.core.exceptions import ValidationError


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
    image = CloudinaryField('image', blank=True, null=True)

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


class Product(models.Model):
    title = models.CharField(max_length=200, verbose_name='Titre')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='Prix')
    description = models.TextField(verbose_name='Description', blank=True, null=True)
    highlight = models.TextField(verbose_name='Points forts', blank=True, null=True)
    image = CloudinaryField('image', blank=True, null=True)
    supplier = models.ForeignKey('suppliers.Supplier', on_delete=models.CASCADE, related_name='products')
    stripe_product_id = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    disponible_salam = models.BooleanField(default=False, verbose_name='Disponible en Salam')
    stock = models.PositiveIntegerField(default=0, verbose_name='Stock')
    sku = models.CharField(max_length=100, unique=True, verbose_name='SKU')
    color = models.ForeignKey('Color', on_delete=models.CASCADE, related_name='products', null=True, blank=True)

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
        self.title = self.title.strip().title()
        if self.description:
            self.description = self.description.strip()
        if self.highlight:
            self.highlight = self.highlight.strip()
        if self.image and hasattr(self.image, 'file'):
            optimizer = ImageOptimizer()
            if optimizer.validate_image(self.image.file):
                self.image.file = optimizer.optimize_image(self.image.file)
        super().save(*args, **kwargs)

    def get_highlights(self):
        if self.highlight:
            return self.highlight.splitlines()
        return []


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
    product = models.OneToOneField(Product, primary_key=True, on_delete=models.CASCADE, related_name='clothing_product',
                                   default=1)
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
    product = models.OneToOneField(Product, primary_key=True, on_delete=models.CASCADE, related_name='cultural_product',
                                   default=1)
    author = models.CharField(max_length=255, blank=True, null=True)  # Auteur
    isbn = models.CharField(max_length=20, blank=True, null=True)  # ISBN (International Standard Book Number)
    date = models.DateField(blank=True, null=True)  # Date de publication

    def __str__(self):
        return self.product.title

    def save(self, *args, **kwargs):
        # Nettoyage et normalisation de l'auteur
        if self.author:
            self.author = self.author.strip().title()
        super().save(*args, **kwargs)


class ImageProduct(models.Model):
    image = CloudinaryField('image', blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='image_products')
    ordre = models.AutoField(primary_key=True)

    class Meta:
        ordering = ['ordre']
        verbose_name = 'Image du produit'
        verbose_name_plural = 'Images du produit'

    def __str__(self):
        return f"{self.product.title} - Image {self.ordre}"


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


