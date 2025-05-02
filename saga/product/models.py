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

    class Meta:
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'
        ordering = ['-created_at']
        unique_together = [['title', 'category']]  # Un produit ne peut pas avoir le même titre dans la même catégorie

    def __str__(self):
        return self.title

    def clean(self):
        # Vérification de l'unicité du titre dans la catégorie
        if Product.objects.filter(title=self.title, category=self.category).exclude(pk=self.pk).exists():
            raise ValidationError(
                {'title': 'Un produit avec ce titre existe déjà dans cette catégorie.'}
            )

    def save(self, *args, **kwargs):
        # Nettoyage et normalisation du titre
        self.title = self.title.strip().title()

        # Nettoyage et normalisation de la description et des points forts
        if self.description:
            self.description = self.description.strip()
        if self.highlight:
            self.highlight = self.highlight.strip()

        # Optimisation de l'image si elle est fournie
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
    author = models.ForeignKey('accounts.Shopper', on_delete=models.CASCADE, related_name='reviews')
    note = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # pour éviter qu'un utilisateur ne puisse pas laisser plusieurs avis sur un même produit
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author} - {self.product.title} - {self.note}/5"

    # sera utilisé dans le template pour afficher une étoile pleine ou vide
    @property
    def is_positive(self):
        return self.note >= 4


class Phone(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='phone', verbose_name='Produit associé')
    model = models.CharField(max_length=100, verbose_name='Modèle')
    brand = models.CharField(max_length=50, verbose_name='Marque')
    operating_system = models.CharField(max_length=50, verbose_name='Système d\'exploitation')
    screen_size = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Taille d\'écran (pouces)')
    resolution = models.CharField(max_length=50, verbose_name='Résolution')
    processor = models.CharField(max_length=100, verbose_name='Processeur')
    battery_capacity = models.PositiveIntegerField(verbose_name='Capacité batterie (mAh)')
    camera_main = models.CharField(max_length=100, verbose_name='Appareil photo principal')
    camera_front = models.CharField(max_length=100, verbose_name='Appareil photo frontal')
    network = models.CharField(max_length=100, verbose_name='Réseaux supportés')
    warranty = models.CharField(max_length=100, verbose_name='Garantie')
    imei = models.CharField(max_length=15, unique=True, verbose_name='IMEI', blank=True, null=True)
    is_new = models.BooleanField(default=True, verbose_name='Neuf')
    box_included = models.BooleanField(default=True, verbose_name='Boîte incluse')
    accessories = models.TextField(blank=True, null=True, verbose_name='Accessoires inclus')

    def __str__(self):
        return f"{self.brand} {self.model}"

    def save(self, *args, **kwargs):
        # Nettoyage et normalisation des champs textuels
        self.model = self.model.strip().title()
        self.brand = self.brand.strip().title()
        self.operating_system = self.operating_system.strip().title()
        self.resolution = self.resolution.strip().title()
        self.processor = self.processor.strip().title()
        self.camera_main = self.camera_main.strip().title()
        self.camera_front = self.camera_front.strip().title()
        self.network = self.network.strip().title()
        self.warranty = self.warranty.strip().title()
        if self.accessories:
            self.accessories = self.accessories.strip()

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Téléphone'
        verbose_name_plural = 'Téléphones'
        ordering = ['brand', 'model']

    def get_available_variants(self):
        return self.variants.filter(stock__gt=0)

    def get_min_price(self):
        return self.variants.aggregate(min_price=models.Min('price'))['min_price']

    def get_max_price(self):
        return self.variants.aggregate(max_price=models.Max('price'))['max_price']


class PhoneVariant(models.Model):
    phone = models.ForeignKey(Phone, on_delete=models.CASCADE, related_name='variants')
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='phone_variants')
    storage = models.PositiveIntegerField(verbose_name='Stockage (Go)')
    ram = models.PositiveIntegerField(verbose_name='RAM (Go)')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Prix')
    stock = models.PositiveIntegerField(default=0, verbose_name='Stock')
    sku = models.CharField(max_length=100, unique=True, verbose_name='SKU')
    disponible_salam = models.BooleanField(default=False, verbose_name='Disponible en Salam')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Variante de téléphone'
        verbose_name_plural = 'Variantes de téléphones'
        ordering = ['phone', 'storage', 'ram', 'color']
        unique_together = [['phone', 'color', 'storage', 'ram']]  # Une variante ne peut pas avoir la même combinaison phone-couleur-stockage-ram

    def __str__(self):
        return f"{self.phone} - {self.color} - {self.storage}Go/{self.ram}Go"

    def clean(self):
        # Vérification de l'unicité de la combinaison phone-couleur-stockage-ram
        if PhoneVariant.objects.filter(
            phone=self.phone,
            color=self.color,
            storage=self.storage,
            ram=self.ram
        ).exclude(pk=self.pk).exists():
            raise ValidationError(
                'Une variante avec cette combinaison de téléphone, couleur, stockage et RAM existe déjà.'
            )

    @property
    def primary_image(self):
        return self.images.filter(is_primary=True).first() or self.images.first()

    @property
    def all_images(self):
        return self.images.all()


class PhoneVariantImage(models.Model):
    variant = models.ForeignKey(PhoneVariant, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField('image')
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'Image de variante'
        verbose_name_plural = 'Images de variantes'

    def __str__(self):
        return f"Image pour {self.variant}"

    def save(self, *args, **kwargs):
        # Si c'est la première image ou si c'est marquée comme primaire
        if not self.variant.images.exists() or self.is_primary:
            # Désactiver toutes les autres images primaires
            self.variant.images.filter(is_primary=True).update(is_primary=False)
            self.is_primary = True
        super().save(*args, **kwargs)


