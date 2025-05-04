from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Sum, F
from product.models import Product, Color, Size, ShippingMethod
from django.conf import settings

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
                cart = cls.objects.create(session_key=session_key)
        
        return cart


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='cart_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey('product.Phone', on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    colors = models.ManyToManyField(Color, blank=True)
    sizes = models.ManyToManyField(Size, blank=True)

    def __str__(self):
        if self.variant:
            return f"{self.quantity} de {self.product.title} - {self.variant.color.name} {self.variant.storage}Go/{self.variant.ram}Go RAM dans le panier {self.cart.id}"
        return f"{self.quantity} de {self.product.title} dans le panier {self.cart.id}"
    
    def get_total_price(self):
        if self.variant:
            return self.variant.price * self.quantity
        return self.product.price * self.quantity
    



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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Statut et paiement
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default=CASH_ON_DELIVERY)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Livraison
    shipping_address = models.ForeignKey('accounts.ShippingAddress', on_delete=models.PROTECT)
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


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('product.Product', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    colors = models.ManyToManyField('product.Color', blank=True)
    sizes = models.ManyToManyField('product.Size', blank=True)

    def __str__(self):
        return f"{self.quantity} of {self.product.title} in Order {self.order.id}"
    
    def get_total_price(self):
        return self.product.price * self.quantity

    def save(self, *args, **kwargs):
        self.total_price = self.price * self.quantity
        super().save(*args, **kwargs)
