from django.conf import settings
from django.db import models
from django.utils import timezone

class SiteConfiguration(models.Model):
    """Configuration globale du site"""
    site_name = models.CharField(max_length=100, default="BoliBana Sugu")
    phone_number = models.CharField(max_length=20, blank=True, help_text="Numéro de téléphone sans indicatif")
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    rccm = models.CharField(max_length=50, blank=True, help_text="Numéro RCCM")
    
    # Réseaux sociaux
    whatsapp_number = models.CharField(max_length=20, blank=True, help_text="Numéro WhatsApp (sans indicatif)")
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)
    
    # Informations légales
    company_name = models.CharField(max_length=100, default="BoliBana Sugu")
    company_type = models.CharField(max_length=50, default="Entreprise individuelle")
    company_address = models.CharField(max_length=200, default="Bamako, Mali")
    ninea_number = models.CharField(max_length=50, blank=True, help_text="Numéro NINEA")
    
    # Métadonnées
    meta_description = models.TextField(blank=True, help_text="Description pour les moteurs de recherche")
    meta_keywords = models.TextField(blank=True, help_text="Mots-clés pour les moteurs de recherche")
    
    # Configuration du site
    maintenance_mode = models.BooleanField(default=False, help_text="Activer le mode maintenance")
    google_analytics_id = models.CharField(max_length=50, blank=True)
    facebook_pixel_id = models.CharField(max_length=50, blank=True, help_text="ID du Facebook Pixel (Meta Pixel)")
    facebook_access_token = models.CharField(max_length=500, blank=True, help_text="Token d'accès Facebook pour l'API Conversions")
    
    # Horaires d'ouverture
    opening_hours = models.TextField(blank=True, help_text="Horaires d'ouverture (ex: Lun-Ven: 8h-18h)")
    opening_hours_detailed = models.TextField(blank=True, help_text="Horaires détaillés pour le footer")
    
    # Informations de livraison
    delivery_info = models.TextField(blank=True, help_text="Informations sur la livraison")
    return_policy = models.TextField(blank=True, help_text="Politique de retour")
    
    # Configuration visuelle
    logo_url = models.URLField(blank=True, help_text="URL du logo du site")
    logo_small_url = models.URLField(blank=True, help_text="URL du logo petit format (mobile)")
    favicon_url = models.URLField(blank=True, help_text="URL du favicon")
    
    # Identité visuelle - Couleurs de marque
    brand_primary_color = models.CharField(max_length=7, default="#008000", help_text="Couleur primaire (ex: #008000 vert)")
    brand_secondary_color = models.CharField(max_length=7, default="#FFD700", help_text="Couleur secondaire (ex: #FFD700 or)")
    brand_accent_color = models.CharField(max_length=7, default="#EF4444", help_text="Couleur d'accent (ex: #EF4444 rouge)")
    brand_tagline = models.CharField(max_length=200, default="Votre intermédiaire expert du marché", help_text="Slogan de la marque")
    brand_short_tagline = models.CharField(max_length=100, default="SuGu", help_text="Sous-titre court de la marque")
    
    class Meta:
        verbose_name = "Configuration du site"
        verbose_name_plural = "Configuration du site"
    
    def __str__(self):
        return f"Configuration - {self.site_name}"
    
    @classmethod
    def get_config(cls):
        """Récupère la configuration active (créée automatiquement si elle n'existe pas)"""
        config, created = cls.objects.get_or_create(
            id=1,
            defaults={
                'site_name': 'BoliBana Sugu',
                'company_name': 'BoliBana Sugu',
                'company_type': 'Entreprise individuelle',
                'company_address': 'Bamako, Mali',
                'opening_hours': 'Lun-Ven: 8h-18h, Sam: 9h-17h',
                'opening_hours_detailed': '8h>21h, dimanche 8h30>13h',
                'address': 'Rue 754, Kalaban Coro, Bamako',
            }
        )
        return config 

class StaticPage(models.Model):
    """Page statique gérée depuis l'admin, exposée via API."""
    slug = models.SlugField(max_length=100, unique=True, help_text="Identifiant unique (ex: cgv, about, help-center)")
    title = models.CharField(max_length=200, help_text="Titre de la page")
    content = models.TextField(blank=True, help_text="Contenu HTML de la page")
    is_published = models.BooleanField(default=True, help_text="Page visible via l'API")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Page statique"
        verbose_name_plural = "Pages statiques"
        ordering = ['title']

    def __str__(self):
        return self.title


class CookieConsent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    analytics = models.BooleanField(default=False)
    marketing = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"Consentement cookies de {self.user}" 
        return f"Consentement cookies (session {self.session_id})" 