from django.db import models
from django.conf import settings
from django.utils import timezone
from cryptography.fernet import Fernet
import base64
import logging

logger = logging.getLogger(__name__)


class ApiKey(models.Model):
    """
    Stockage sécurisé des clés API pour l'intégration B2B
    
    Les clés API sont chiffrées avant stockage pour des raisons de sécurité.
    """
    # Clé API chiffrée
    key_encrypted = models.TextField(verbose_name='Clé API (chiffrée)')
    
    # Nom/description de la clé
    name = models.CharField(
        max_length=255,
        verbose_name='Nom de la clé',
        help_text='Ex: "Clé principale - Site Bamako"',
        default='Clé API'
    )
    
    # Statut
    is_active = models.BooleanField(default=True, verbose_name='Active')
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créée le')
    last_used_at = models.DateTimeField(null=True, blank=True, verbose_name='Dernière utilisation')
    
    class Meta:
        verbose_name = 'Clé API'
        verbose_name_plural = 'Clés API'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active']),
        ]
    
    def set_key(self, api_key: str):
        """Chiffre et stocke la clé API"""
        if not api_key:
            raise ValueError("La clé API ne peut pas être vide")
        
        encryption_key = self._get_encryption_key()
        f = Fernet(encryption_key)
        encrypted = f.encrypt(api_key.encode())
        self.key_encrypted = base64.b64encode(encrypted).decode()
    
    def get_key(self) -> str:
        """Déchiffre et retourne la clé API"""
        if not self.key_encrypted:
            return ''
        
        try:
            encryption_key = self._get_encryption_key()
            f = Fernet(encryption_key)
            encrypted = base64.b64decode(self.key_encrypted.encode())
            decrypted = f.decrypt(encrypted)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Erreur lors du déchiffrement de la clé API {self.id}: {str(e)}")
            raise ValueError(f"Impossible de déchiffrer la clé API: {str(e)}")
    
    def _get_encryption_key(self):
        """Récupère la clé de chiffrement depuis settings"""
        encryption_key = getattr(settings, 'INVENTORY_ENCRYPTION_KEY', None)
        
        if not encryption_key:
            # Générer une clé par défaut (en production, utiliser une clé fixe dans .env)
            encryption_key = Fernet.generate_key()
            logger.warning(
                "INVENTORY_ENCRYPTION_KEY non configuré. "
                "Une clé temporaire a été générée. Configurez INVENTORY_ENCRYPTION_KEY dans .env pour la production."
            )
        
        if isinstance(encryption_key, str):
            encryption_key = encryption_key.encode()
        
        return encryption_key
    
    def record_usage(self):
        """Enregistre une utilisation de la clé"""
        self.last_used_at = timezone.now()
        self.save(update_fields=['last_used_at'])
    
    @classmethod
    def get_active_key(cls):
        """Récupère la clé API active"""
        api_key = cls.objects.filter(is_active=True).first()
        if api_key:
            return api_key.get_key()
        # Fallback vers la clé globale depuis settings
        return getattr(settings, 'B2B_API_KEY', '')
    
    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.name} - {status}"


class ExternalProduct(models.Model):
    """
    Mapping entre les produits de l'app B2B et Product de SagaKore
    
    Ce modèle fait le lien entre un produit SagaKore et son équivalent
    dans l'application B2B (BoliBanaStock).
    """
    SYNC_STATUS_CHOICES = [
        ('synced', 'Synchronisé'),
        ('pending', 'En attente'),
        ('error', 'Erreur'),
    ]

    product = models.OneToOneField(
        'product.Product',
        on_delete=models.CASCADE,
        related_name='external_product',
        verbose_name='Produit'
    )
    external_id = models.IntegerField(verbose_name='ID externe (B2B)')
    external_sku = models.CharField(max_length=100, verbose_name='SKU externe')
    external_category_id = models.IntegerField(null=True, blank=True, verbose_name='ID catégorie externe')
    is_b2b = models.BooleanField(
        default=False,
        verbose_name='Produit B2B',
        help_text='Cocher si ce produit est destiné au B2B (sinon c\'est un produit B2C)'
    )
    last_synced_at = models.DateTimeField(null=True, blank=True, verbose_name='Dernière synchronisation')
    sync_status = models.CharField(
        max_length=20,
        choices=SYNC_STATUS_CHOICES,
        default='pending',
        verbose_name='Statut de synchronisation'
    )
    sync_error = models.TextField(null=True, blank=True, verbose_name='Erreur de synchronisation')

    class Meta:
        verbose_name = 'Produit externe (B2B)'
        verbose_name_plural = 'Produits externes (B2B)'
        unique_together = ['external_id']
        indexes = [
            models.Index(fields=['external_id']),
            models.Index(fields=['sync_status']),
        ]

    def __str__(self):
        return f"{self.product.title} (ID B2B: {self.external_id})"


class ExternalCategory(models.Model):
    """
    Mapping des catégories de l'app B2B vers Category de SagaKore
    
    Ce modèle fait le lien entre une catégorie SagaKore et son équivalent
    dans l'application B2B (BoliBanaStock).
    """
    category = models.OneToOneField(
        'product.Category',
        on_delete=models.CASCADE,
        related_name='external_category',
        verbose_name='Catégorie'
    )
    external_id = models.IntegerField(verbose_name='ID externe (B2B)')
    external_parent_id = models.IntegerField(null=True, blank=True, verbose_name='ID parent externe')
    last_synced_at = models.DateTimeField(null=True, blank=True, verbose_name='Dernière synchronisation')

    class Meta:
        verbose_name = 'Catégorie externe (B2B)'
        verbose_name_plural = 'Catégories externes (B2B)'
        unique_together = ['external_id']
        indexes = [
            models.Index(fields=['external_id']),
        ]

    def __str__(self):
        return f"{self.category.name} (ID B2B: {self.external_id})"
