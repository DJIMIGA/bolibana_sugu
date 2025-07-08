from django.db import models

class SiteConfiguration(models.Model):
    """Configuration globale du site"""
    site_name = models.CharField(max_length=100, default="BoliBana Sugu")
    phone_number = models.CharField(max_length=20, blank=True, help_text="Numéro de téléphone sans indicatif")
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    rccm = models.CharField(max_length=50, blank=True, help_text="Numéro RCCM")
    
    # Réseaux sociaux
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    
    # Informations légales
    company_name = models.CharField(max_length=100, default="BoliBana Sugu")
    company_type = models.CharField(max_length=50, default="Entreprise individuelle")
    company_address = models.CharField(max_length=200, default="Bamako, Mali")
    
    # Métadonnées
    meta_description = models.TextField(blank=True, help_text="Description pour les moteurs de recherche")
    meta_keywords = models.TextField(blank=True, help_text="Mots-clés pour les moteurs de recherche")
    
    # Configuration du site
    maintenance_mode = models.BooleanField(default=False, help_text="Activer le mode maintenance")
    google_analytics_id = models.CharField(max_length=50, blank=True)
    
    # Horaires d'ouverture
    opening_hours = models.TextField(blank=True, help_text="Horaires d'ouverture (ex: Lun-Ven: 8h-18h)")
    
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
            }
        )
        return config 