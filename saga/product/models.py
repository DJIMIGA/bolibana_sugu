from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


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
    name = models.CharField(max_length=255)  # Nom de la catégorie
    image = models.ImageField(upload_to='categories/', blank=True)  # Image de la catégorie
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children',
        on_delete=models.CASCADE
    )  # Relation parent-enfant

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'

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


#
# class Electronics(models.Model):  # High-tech
#     product = GenericRelation(Product)
#     operating_system = models.CharField(max_length=50, blank=True, null=True)
#     power = models.CharField(max_length=50, blank=True, null=True)
#
#
# class Hardware(models.Model):  # Quincaillerie
#     product = GenericRelation(Product)
#     material = models.CharField(max_length=50, blank=True, null=True)
#     weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)


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
