from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver


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
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
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
        verbose_name_plural = "Categories"

    def get_full_path(self):
        path = [self.name]
        parent = self.parent
        while parent:
            path.append(parent.name)
            parent = parent.parent
        return ' > '.join(reversed(path))


class Product(models.Model):
    title = models.CharField(max_length=200, verbose_name='Titre')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Catégorie')
    price = models.DecimalField(max_digits=10,
                                decimal_places=0, verbose_name='Prix')  # Prix du produit
    description = models.TextField(blank=True, null=True, verbose_name='Description')  # Description du produit
    highlight = models.TextField(blank=True, null=True, verbose_name='Points forts')  # Points forts du produit
    image = models.ImageField(upload_to='product/', blank=True, null=True, verbose_name='Image')  # Image du produit
    supplier = models.ForeignKey('suppliers.Supplier', on_delete=models.CASCADE, related_name='products', verbose_name='Fournisseur')
    stripe_product_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title

    def get_highlights(self):
        if self.highlight:
            return self.highlight.splitlines()
        return []


class Color(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=7)

    def __str__(self):
        return self.name

    def get_hex_code(self):
        return self.code

    def get_rgb_code(self):
        return tuple(int(self.code.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))


class Size(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Clothing(models.Model):
    product = models.OneToOneField(Product, primary_key=True, on_delete=models.CASCADE, related_name='clothing_product',
                                   default=1)
    GENDER_CHOICES = [
        ('H', 'Homme'),
        ('F', 'Femme'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    size = models.ManyToManyField(Size, related_name='clothing_size', blank=True, null=True)
    color = models.ManyToManyField(Color, related_name='clothing_color', blank=True, null=True)

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


class ImageProduct(models.Model):
    image = models.ImageField(upload_to='product/galerie/', blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='image_products')  # Changement de related_name
    ordre = models.AutoField(primary_key=True)

    class Meta:
        ordering = ['ordre']

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


class PhoneVariant(models.Model):
    phone = models.ForeignKey('Phone', on_delete=models.CASCADE, related_name='variants', verbose_name='Téléphone')
    color = models.ForeignKey(Color, on_delete=models.CASCADE, verbose_name='Couleur')
    storage = models.PositiveIntegerField(verbose_name='Stockage (Go)')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Prix')
    stock = models.PositiveIntegerField(default=0, verbose_name='Stock disponible')
    sku = models.CharField(max_length=50, unique=True, verbose_name='SKU')

    def __str__(self):
        return f"{self.phone.model} - {self.color.name} - {self.storage}Go"

    class Meta:
        verbose_name = 'Variante de téléphone'
        verbose_name_plural = 'Variantes de téléphone'
        unique_together = ['phone', 'color', 'storage']

    def save(self, *args, **kwargs):
        # Générer le SKU automatiquement
        if not self.sku:
            self.sku = f"{self.phone.model}-{self.color.name}-{self.storage}GB"
        super().save(*args, **kwargs)

    @property
    def primary_image(self):
        return self.images.filter(is_primary=True).first() or self.images.first()

    @property
    def all_images(self):
        return self.images.all()


class Phone(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='phone', verbose_name='Produit associé')
    model = models.CharField(max_length=100, verbose_name='Modèle')
    operating_system = models.CharField(max_length=50, verbose_name='Système d\'exploitation')
    screen_size = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Taille d\'écran (pouces)')
    resolution = models.CharField(max_length=50, verbose_name='Résolution')
    processor = models.CharField(max_length=100, verbose_name='Processeur')
    ram = models.PositiveIntegerField(verbose_name='RAM (Go)')
    battery_capacity = models.PositiveIntegerField(verbose_name='Capacité batterie (mAh)')
    camera_main = models.CharField(max_length=100, verbose_name='Appareil photo principal')
    camera_front = models.CharField(max_length=100, verbose_name='Appareil photo frontal')
    network = models.CharField(max_length=100, verbose_name='Réseaux supportés')
    warranty = models.CharField(max_length=100, verbose_name='Garantie')
    imei = models.CharField(max_length=15, unique=True, verbose_name='IMEI', blank=True, null=True)
    is_new = models.BooleanField(default=True, verbose_name='Neuf')
    box_included = models.BooleanField(default=True, verbose_name='Boîte incluse')
    accessories = models.TextField(blank=True, null=True, verbose_name='Accessoires inclus')
    storage = models.PositiveIntegerField(verbose_name='Stockage (Go)', null=True, blank=True)

    def __str__(self):
        return f"{self.product.category.name} {self.model}"

    class Meta:
        verbose_name = 'Téléphone'
        verbose_name_plural = 'Téléphones'
        ordering = ['model']

    def get_available_variants(self):
        return self.variants.filter(stock__gt=0)

    def get_min_price(self):
        return self.variants.aggregate(min_price=models.Min('price'))['min_price']

    def get_max_price(self):
        return self.variants.aggregate(max_price=models.Max('price'))['max_price']


class PhoneVariantImage(models.Model):
    variant = models.ForeignKey(PhoneVariant, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='phone_variants/images/')
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


