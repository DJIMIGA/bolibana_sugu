from django.db import models

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
    
    # Horaires d'ouverture
    opening_hours = models.TextField(blank=True, help_text="Horaires d'ouverture (ex: Lun-Ven: 8h-18h)")
    opening_hours_detailed = models.TextField(blank=True, help_text="Horaires détaillés pour le footer")
    
    # Informations de livraison
    delivery_info = models.TextField(blank=True, help_text="Informations sur la livraison")
    return_policy = models.TextField(blank=True, help_text="Politique de retour")
    
    # Configuration visuelle
    logo_url = models.URLField(blank=True, help_text="URL du logo du site")
    favicon_url = models.URLField(blank=True, help_text="URL du favicon")
    
    # Contenu personnalisable du footer - À propos
    about_story_title = models.CharField(max_length=100, default="Notre histoire", help_text="Titre du lien 'Notre histoire'")
    about_story_content = models.TextField(blank=True, help_text="Contenu de la page 'Notre histoire'")
    about_values_title = models.CharField(max_length=100, default="Nos valeurs", help_text="Titre du lien 'Nos valeurs'")
    about_values_content = models.TextField(blank=True, help_text="Contenu de la page 'Nos valeurs'")
    
    # Contenu personnalisable du footer - Services
    service_loyalty_title = models.CharField(max_length=100, default="Fidélité Bolibana", help_text="Titre du lien 'Fidélité Bolibana'")
    service_loyalty_content = models.TextField(blank=True, help_text="Contenu de la page 'Fidélité Bolibana'")
    service_express_title = models.CharField(max_length=100, default="Livraison express", help_text="Titre du lien 'Livraison express'")
    service_express_content = models.TextField(blank=True, help_text="Contenu de la page 'Livraison express'")
    
    # Contenu personnalisable du footer - Assistance
    help_center_title = models.CharField(max_length=100, default="Centre d'aide", help_text="Titre du lien 'Centre d'aide'")
    help_center_content = models.TextField(blank=True, help_text="Contenu de la page 'Centre d'aide'")
    help_returns_title = models.CharField(max_length=100, default="Retours faciles", help_text="Titre du lien 'Retours faciles'")
    help_returns_content = models.TextField(blank=True, help_text="Contenu de la page 'Retours faciles'")
    help_warranty_title = models.CharField(max_length=100, default="Garantie qualité", help_text="Titre du lien 'Garantie qualité'")
    help_warranty_content = models.TextField(blank=True, help_text="Contenu de la page 'Garantie qualité'")
    
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