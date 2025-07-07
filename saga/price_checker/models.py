from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q, Avg, Max, Min
from django.utils.text import slugify
from django.conf import settings
from product.models import Product
from saga.utils.image_optimizer import ImageOptimizer
from datetime import timedelta
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from accounts.models import Shopper

class City(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nom de la ville')
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Active')

    class Meta:
        verbose_name = 'Ville'
        verbose_name_plural = 'Villes'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Nettoyage et normalisation du nom
        self.name = self.name.strip().title()

        # Génération automatique du slug si vide
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

class PriceSubmission(models.Model):
    """Modèle pour les soumissions de prix en attente de validation"""
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('APPROVED', 'Validé'),
        ('REJECTED', 'Rejeté'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_submissions')
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='price_submissions')
    price = models.DecimalField(max_digits=10, decimal_places=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='price_submissions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    validation_notes = models.TextField(blank=True, null=True)
    validated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='validated_prices')
    created_at = models.DateTimeField(auto_now_add=True)
    validated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Soumission de prix'
        verbose_name_plural = 'Soumissions de prix'
        ordering = ['-created_at']

    def __str__(self):
        try:
            product_title = self.product.title if self.product else "Produit non spécifié"
            city_name = self.city.name if self.city else "Ville non spécifiée"
            return f"{product_title} - {self.price} FCFA ({city_name})"
        except Exception:
            return f"Soumission #{self.id} - {self.price} FCFA"

    def approve(self, admin_user, notes=None):
        """Approuve la soumission et crée un PriceEntry"""
        self.status = 'APPROVED'
        self.validated_by = admin_user
        self.validated_at = timezone.now()
        self.validation_notes = notes
        self.save()
        
        # Créer un PriceEntry à partir de la soumission
        PriceEntry.objects.create(
            product=self.product,
            city=self.city,
            price=self.price,
            user=self.user,
            submission=self,
            validated_by=admin_user
        )

    def reject(self, admin_user, notes=None):
        """Rejette la soumission"""
        self.status = 'REJECTED'
        self.validated_by = admin_user
        self.validated_at = timezone.now()
        self.validation_notes = notes
        self.save()

class PriceEntry(models.Model):
    """Modèle pour les prix validés et actifs"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_entries')
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='price_entries')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='XOF')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='price_entries')
    validated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='validated_price_entries')
    submission = models.OneToOneField(PriceSubmission, on_delete=models.SET_NULL, null=True, blank=True, related_name='price_entry')
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Entrée de prix'
        verbose_name_plural = 'Entrées de prix'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.title} - {self.price} {self.currency} ({self.city.name})"

    @classmethod
    def get_average_price(cls, product, city):
        """Calcule le prix moyen pour un produit et une ville donnés"""
        prices = cls.objects.filter(
            product=product,
            city=city,
            is_active=True
        ).order_by('-created_at')

        if not prices.exists():
            return {'average_price': None, 'count': 0}

        # Récupérer le prix le plus récent
        latest_price = prices.first()
        
        # Si c'est le seul prix, retourner ce prix
        if prices.count() == 1:
            return {
                'average_price': latest_price.price,
                'count': 1
            }

        # Calculer la moyenne des prix des 7 derniers jours
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_prices = prices.filter(created_at__gte=seven_days_ago)
        
        if recent_prices.exists():
            avg_price = recent_prices.aggregate(avg_price=Avg('price'))['avg_price']
            return {
                'average_price': avg_price,
                'count': recent_prices.count()
            }
        
        # Si aucun prix dans les 7 derniers jours, retourner le prix le plus récent
        return {
            'average_price': latest_price.price,
            'count': 1
        }

    @property
    def price_change(self):
        """Calcule la variation de prix par rapport au prix précédent"""
        if not self.product or not self.city:
            return None
            
        previous_price = PriceEntry.objects.filter(
            product=self.product,
            city=self.city,
            created_at__lt=self.created_at,
            is_active=True
        ).order_by('-created_at').first()
        
        if previous_price:
            return self.price - previous_price.price
        return None

    @property
    def price_change_percentage(self):
        """Calcule le pourcentage de variation du prix par rapport au prix précédent"""
        if not self.product or not self.city:
            return None
            
        previous_price = PriceEntry.objects.filter(
            product=self.product,
            city=self.city,
            created_at__lt=self.created_at,
            is_active=True
        ).order_by('-created_at').first()
        
        if previous_price and previous_price.price > 0:
            return ((self.price - previous_price.price) / previous_price.price) * 100
        return None

    def deactivate(self, admin_user, notes=None):
        """Désactive le prix"""
        self.is_active = False
        self.save()
        
        # Créer un enregistrement de désactivation
        PriceDeactivation.objects.create(
            price_entry=self,
            admin_user=admin_user,
            notes=notes
        )

class PriceDeactivation(models.Model):
    """Historique des désactivations de prix"""
    price_entry = models.ForeignKey(PriceEntry, on_delete=models.CASCADE, related_name='deactivations')
    admin_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='price_deactivations')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Désactivation de prix'
        verbose_name_plural = 'Désactivations de prix'
        ordering = ['-created_at']

    def __str__(self):
        return f"Désactivation de {self.price_entry} par {self.admin_user}"

class ProductStatus(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Brouillon'),
        ('APPROVED', 'Approuvé'),
        ('PUBLISHED', 'Publié'),
    ]

    VISIBILITY_CHOICES = [
        ('PRIVATE', 'Privé'),
        ('PUBLIC', 'Public'),
    ]

    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='status')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT',
        verbose_name='Statut'
    )
    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default='PRIVATE',
        verbose_name='Visibilité'
    )
    target_price = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name='Prix cible'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Statut du produit'
        verbose_name_plural = 'Statuts des produits'
        ordering = ['-created_at']

    def __str__(self):
        return f"Statut de {self.product.title}"

class PriceValidation(models.Model):
    """Modèle pour suivre les validations des prix par les administrateurs"""
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('APPROVED', 'Approuvé'),
        ('REJECTED', 'Rejeté'),
    ]
    
    price_entry = models.ForeignKey(PriceEntry, on_delete=models.CASCADE, related_name='validations', null=True, blank=True)
    admin_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='price_validations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Validation de prix'
        verbose_name_plural = 'Validations de prix'
        ordering = ['-created_at']

    def __str__(self):
        return f"Validation de {self.price_entry} par {self.admin_user}" 