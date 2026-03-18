from .models import SiteConfiguration
from datetime import datetime

def site_config(request):
    """
    Context processor pour exposer la configuration du site à tous les templates
    """
    try:
        config = SiteConfiguration.get_config()
        return {
            'site_config': config,
            'site_name': config.site_name,
            'site_phone': config.phone_number,
            'site_email': config.email,
            'site_address': config.address,
            'site_rccm': config.rccm,
            'company_name': config.company_name,
            'company_type': config.company_type,
            'company_address': config.company_address,
            'maintenance_mode': config.maintenance_mode,
            
            # Réseaux sociaux
            'site_whatsapp': config.whatsapp_number or config.phone_number,
            'site_facebook': config.facebook_url,
            'site_instagram': config.instagram_url,
            'site_twitter': config.twitter_url,
            'site_tiktok': config.tiktok_url,
            
            # Informations légales
            'site_ninea': config.ninea_number,
            
            # Horaires
            'site_opening_hours': config.opening_hours,
            'site_opening_hours_detailed': config.opening_hours_detailed,
            
            # Informations de livraison
            'site_delivery_info': config.delivery_info,
            'site_return_policy': config.return_policy,
            
            # Configuration visuelle
            'site_logo_url': config.logo_url,
            'site_logo_small_url': config.logo_small_url,
            'site_favicon_url': config.favicon_url,
            
            # Identité visuelle
            'brand_primary_color': config.brand_primary_color,
            'brand_secondary_color': config.brand_secondary_color,
            'brand_accent_color': config.brand_accent_color,
            'brand_tagline': config.brand_tagline,
            'brand_short_tagline': config.brand_short_tagline,
            
            # Métadonnées SEO
            'site_meta_description': config.meta_description,
            'site_meta_keywords': config.meta_keywords,
            
            # Année courante
            'current_year': datetime.now().year,
        }
    except Exception:
        # En cas d'erreur (migration non effectuée), retourner des valeurs par défaut
        return {
            'site_config': None,
            'site_name': 'BoliBana Sugu',
            'site_phone': '',
            'site_email': '',
            'site_address': 'Rue 754, Kalaban Coro, Bamako',
            'site_rccm': '',
            'company_name': 'BoliBana Sugu',
            'company_type': 'Entreprise individuelle',
            'company_address': 'Bamako, Mali',
            'maintenance_mode': False,
            
            # Réseaux sociaux
            'site_whatsapp': '',
            'site_facebook': '',
            'site_instagram': '',
            'site_twitter': '',
            'site_tiktok': '',
            
            # Informations légales
            'site_ninea': '',
            
            # Horaires
            'site_opening_hours': 'Lun-Ven: 8h-18h, Sam: 9h-17h',
            'site_opening_hours_detailed': '8h>21h, dimanche 8h30>13h',
            
            # Informations de livraison
            'site_delivery_info': '',
            'site_return_policy': '',
            
            # Configuration visuelle
            'site_logo_url': '',
            'site_logo_small_url': '',
            'site_favicon_url': '',
            
            # Identité visuelle
            'brand_primary_color': '#008000',
            'brand_secondary_color': '#FFD700',
            'brand_accent_color': '#EF4444',
            'brand_tagline': 'Votre intermédiaire expert du marché',
            'brand_short_tagline': 'SuGu',
            
            # Métadonnées SEO
            'site_meta_description': '',
            'site_meta_keywords': '',
            
            # Année courante
            'current_year': datetime.now().year,
        } 