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
            'site_favicon_url': config.favicon_url,
            
            # Contenu personnalisable du footer - À propos
            'about_story_title': config.about_story_title,
            'about_story_content': config.about_story_content,
            'about_values_title': config.about_values_title,
            'about_values_content': config.about_values_content,
            
            # Contenu personnalisable du footer - Services
            'service_loyalty_title': config.service_loyalty_title,
            'service_loyalty_content': config.service_loyalty_content,
            'service_express_title': config.service_express_title,
            'service_express_content': config.service_express_content,
            
            # Contenu personnalisable du footer - Assistance
            'help_center_title': config.help_center_title,
            'help_center_content': config.help_center_content,
            'help_returns_title': config.help_returns_title,
            'help_returns_content': config.help_returns_content,
            'help_warranty_title': config.help_warranty_title,
            'help_warranty_content': config.help_warranty_content,
            
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
            'site_favicon_url': '',
            
            # Contenu personnalisable du footer - À propos
            'about_story_title': 'Notre histoire',
            'about_story_content': '',
            'about_values_title': 'Nos valeurs',
            'about_values_content': '',
            
            # Contenu personnalisable du footer - Services
            'service_loyalty_title': 'Fidélité Bolibana',
            'service_loyalty_content': '',
            'service_express_title': 'Livraison express',
            'service_express_content': '',
            
            # Contenu personnalisable du footer - Assistance
            'help_center_title': 'Centre d\'aide',
            'help_center_content': '',
            'help_returns_title': 'Retours faciles',
            'help_returns_content': '',
            'help_warranty_title': 'Garantie qualité',
            'help_warranty_content': '',
            
            # Année courante
            'current_year': datetime.now().year,
        } 