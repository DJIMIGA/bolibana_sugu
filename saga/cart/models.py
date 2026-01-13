from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Sum, F
from product.models import Product, Color, Size, ShippingMethod
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal

User = get_user_model()


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"Panier de {self.user.email}"
        return f"Panier anonyme ({self.session_key})"

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.cart_items.all())

    def get_classic_products_total(self):
        """Calcule le total des produits classiques (non Salam)"""
        return sum(item.get_total_price() for item in self.cart_items.all() if not item.product.is_salam)

    def get_salam_products_total(self):
        """Calcule le total des produits Salam"""
        return sum(item.get_total_price() for item in self.cart_items.all() if item.product.is_salam)

    def get_classic_items(self):
        """Retourne les items de produits classiques"""
        return [item for item in self.cart_items.all() if not item.product.is_salam]

    def get_salam_items(self):
        """Retourne les items de produits Salam"""
        return [item for item in self.cart_items.all() if item.product.is_salam]

    def validate_classic_products(self):
        """Valide les produits classiques (vérification du stock)"""
        errors = []
        for item in self.get_classic_items():
            if not item.product.has_stock():
                errors.append(f"Le produit '{item.product.title}' n'est plus en stock")
            else:
                # Pour les produits au poids, vérifier le poids disponible
                if hasattr(item.product, 'specifications') and item.product.specifications:
                    specs = item.product.specifications
                    if specs.get('sold_by_weight') or specs.get('unit_type') in ['weight', 'kg', 'kilogram']:
                        available_weight = specs.get('available_weight_kg', 0)
                        from decimal import Decimal
                        if Decimal(str(available_weight)) < Decimal(str(item.quantity)):
                            errors.append(f"Poids insuffisant pour '{item.product.title}' (disponible: {available_weight} kg, demandé: {item.quantity} kg)")
                    else:
                        # Produit normal : vérifier le stock en unités
                        if item.product.stock < float(item.quantity):
                            errors.append(f"Stock insuffisant pour '{item.product.title}' (disponible: {item.product.stock}, demandé: {int(item.quantity)})")
                else:
                    # Pas de spécifications, vérifier le stock normal
                    if item.product.stock < float(item.quantity):
                        errors.append(f"Stock insuffisant pour '{item.product.title}' (disponible: {item.product.stock}, demandé: {int(item.quantity)})")
        return errors

    def validate_salam_products(self):
        """Valide les produits Salam (pas de vérification de stock)"""
        errors = []
        for item in self.get_salam_items():
            if not item.product.is_available:
                errors.append(f"Le produit Salam '{item.product.title}' n'est plus disponible")
        return errors

    def can_checkout(self):
        """Vérifie si le panier peut être commandé"""
        classic_errors = self.validate_classic_products()
        salam_errors = self.validate_salam_products()
        return len(classic_errors) == 0 and len(salam_errors) == 0

    def get_validation_errors(self):
        """Retourne toutes les erreurs de validation"""
        return {
            'classic_errors': self.validate_classic_products(),
            'salam_errors': self.validate_salam_products()
        }

    @classmethod
    def get_or_create_cart(cls, request):
        if request.user.is_authenticated:
            cart, created = cls.objects.get_or_create(user=request.user)
        else:
            # S'assurer que la session existe et est sauvegardée
            if not request.session.session_key:
                request.session.create()
                request.session.save()  # Force la sauvegarde de la session
            
            session_key = request.session.session_key
            
            # Rechercher un panier existant
            cart = cls.objects.filter(session_key=session_key).first()
            
            if not cart:
                # Vérifier qu'il n'y a pas trop de paniers anonymes (protection anti-spam)
                anonymous_carts_count = cls.objects.filter(session_key__isnull=False).count()
                if anonymous_carts_count > 1000:  # Limite arbitraire
                    # Supprimer les anciens paniers anonymes
                    old_carts = cls.objects.filter(
                        session_key__isnull=False,
                        created_at__lt=timezone.now() - timezone.timedelta(hours=24)
                    )
                    old_carts.delete()
                
                cart = cls.objects.create(session_key=session_key)
        
        return cart


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='cart_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    variant = models.ForeignKey('product.Phone', on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=3, default=1, validators=[MinValueValidator(0.001)])
    colors = models.ManyToManyField(Color, blank=True)
    sizes = models.ManyToManyField(Size, blank=True)

    def __str__(self):
        if self.variant:
            return f"{self.quantity} de {self.product.title} - {self.variant.color.name} {self.variant.storage}Go/{self.variant.ram}Go RAM dans le panier {self.cart.id}"
        return f"{self.quantity} de {self.product.title} dans le panier {self.cart.id}"
    
    def get_total_price(self):
        # Pour les produits au poids, utiliser le prix au kg depuis les spécifications
        if self.product and hasattr(self.product, 'specifications') and self.product.specifications:
            specs = self.product.specifications
            if specs.get('sold_by_weight') or specs.get('unit_type') in ['weight', 'kg', 'kilogram']:
                # Produit au poids : utiliser price_per_kg
                price_per_kg = specs.get('discount_price_per_kg') or specs.get('price_per_kg')
                if price_per_kg:
                    from decimal import Decimal
                    return Decimal(str(price_per_kg)) * Decimal(str(self.quantity))
        
        if self.variant:
            # Utiliser le prix promotionnel si disponible, sinon le prix normal
            price = self.variant.discount_price if hasattr(self.variant, 'discount_price') and self.variant.discount_price else self.variant.price
            from decimal import Decimal
            return Decimal(str(price)) * Decimal(str(self.quantity))
        # Utiliser le prix promotionnel si disponible, sinon le prix normal
        price = self.product.discount_price if hasattr(self.product, 'discount_price') and self.product.discount_price else self.product.price
        from decimal import Decimal
        return Decimal(str(price)) * Decimal(str(self.quantity))
    
    def get_unit_price(self):
        """Retourne le prix unitaire (promo si disponible)"""
        # Pour les produits au poids, utiliser le prix au kg depuis les spécifications
        if self.product and hasattr(self.product, 'specifications') and self.product.specifications:
            specs = self.product.specifications
            if specs.get('sold_by_weight') or specs.get('unit_type') in ['weight', 'kg', 'kilogram']:
                # Produit au poids : utiliser price_per_kg
                price_per_kg = specs.get('discount_price_per_kg') or specs.get('price_per_kg')
                if price_per_kg:
                    from decimal import Decimal
                    return Decimal(str(price_per_kg))
        
        if self.variant:
            from decimal import Decimal
            price = self.variant.discount_price if hasattr(self.variant, 'discount_price') and self.variant.discount_price else self.variant.price
            return Decimal(str(price))
        from decimal import Decimal
        price = self.product.discount_price if hasattr(self.product, 'discount_price') and self.product.discount_price else self.product.price
        return Decimal(str(price))
    



class Order(models.Model):
    # Statuts de commande
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'
    REFUNDED = 'refunded'
    
    STATUS_CHOICES = [
        (PENDING, 'En attente'),
        (CONFIRMED, 'Confirmée'),
        (PROCESSING, 'En préparation'),
        (SHIPPED, 'Expédiée'),
        (DELIVERED, 'Livrée'),
        (CANCELLED, 'Annulée'),
        (REFUNDED, 'Remboursée'),
    ]

    # Méthodes de paiement
    CASH_ON_DELIVERY = 'cash_on_delivery'
    ONLINE_PAYMENT = 'online_payment'
    MOBILE_MONEY = 'mobile_money'

    PAYMENT_CHOICES = [
        (CASH_ON_DELIVERY, 'Paiement à la livraison'),
        (ONLINE_PAYMENT, 'Paiement en ligne'),
        (MOBILE_MONEY, 'Mobile Money'),
    ]

    # Informations de base
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders', null=True, blank=True)
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Statut et paiement
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default=CASH_ON_DELIVERY)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Livraison
    shipping_address = models.ForeignKey('accounts.ShippingAddress', on_delete=models.PROTECT, null=True, blank=True)
    shipping_method = models.ForeignKey('product.ShippingMethod', on_delete=models.PROTECT, null=True, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Montants
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)  # Total des articles
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)  # Frais de livraison
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # TVA ou autres taxes
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Réductions
    total = models.DecimalField(max_digits=10, decimal_places=2)  # Montant final
    
    # Notes et métadonnées
    notes = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)  # Pour stocker des données supplémentaires
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_payment_status = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self):
        return f"Commande #{self.order_number} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Sauvegarder d'abord pour avoir un ID
            super().save(*args, **kwargs)
            # Générer le numéro de commande
            self.order_number = f"CMD-{self.created_at.strftime('%Y%m%d')}-{self.id:04d}"
            # Sauvegarder à nouveau avec le numéro de commande
            kwargs['force_insert'] = False
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    def get_total_items(self):
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0

    def calculate_total(self):
        """Calcule le montant total de la commande"""
        return self.subtotal + self.shipping_cost + self.tax - self.discount

    def mark_as_paid(self):
        """Marque la commande comme payée"""
        from django.utils import timezone
        self.is_paid = True
        self.paid_at = timezone.now()
        self.status = self.CONFIRMED
        self.save()

    def mark_as_shipped(self, tracking_number=None):
        """Marque la commande comme expédiée"""
        from django.utils import timezone
        self.status = self.SHIPPED
        self.shipped_at = timezone.now()
        if tracking_number:
            self.tracking_number = tracking_number
        self.save()

    def mark_as_delivered(self):
        """Marque la commande comme livrée"""
        from django.utils import timezone
        self.status = self.DELIVERED
        self.delivered_at = timezone.now()
        self.save()

    def cancel(self, reason=''):
        """Annule la commande"""
        self.status = self.CANCELLED
        self.cancellation_reason = reason
        self.save()

    def clean(self):
        if not self.user:
            raise ValidationError("Un utilisateur est requis pour la commande.")
        if not self.user.is_active:
            raise ValidationError("L'utilisateur doit être actif pour créer une commande.")


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey('product.Product', on_delete=models.PROTECT, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=3, validators=[MinValueValidator(Decimal('0.001'))])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    colors = models.ManyToManyField('product.Color', blank=True)
    sizes = models.ManyToManyField('product.Size', blank=True)

    def __str__(self):
        return f"{self.quantity} of {self.product.title} in Order {self.order.id}"
    
    def get_total_price(self):
        # Pour les produits au poids, utiliser le prix au kg depuis les spécifications
        if self.product and hasattr(self.product, 'specifications') and self.product.specifications:
            specs = self.product.specifications
            if specs.get('sold_by_weight') or specs.get('unit_type') in ['weight', 'kg', 'kilogram']:
                # Produit au poids : utiliser price_per_kg
                price_per_kg = specs.get('discount_price_per_kg') or specs.get('price_per_kg')
                if price_per_kg:
                    from decimal import Decimal
                    return Decimal(str(price_per_kg)) * Decimal(str(self.quantity))
        
        # Utiliser le prix promotionnel si disponible, sinon le prix normal
        price = self.product.discount_price if hasattr(self.product, 'discount_price') and self.product.discount_price else self.product.price
        from decimal import Decimal
        return Decimal(str(price)) * Decimal(str(self.quantity))

    def save(self, *args, **kwargs):
        from decimal import Decimal
        self.total_price = Decimal(str(self.price)) * Decimal(str(self.quantity))
        super().save(*args, **kwargs)
