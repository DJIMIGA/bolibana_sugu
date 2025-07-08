from .models import SiteConfiguration

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
        }
    except Exception:
        # En cas d'erreur (migration non effectuée), retourner des valeurs par défaut
        return {
            'site_config': None,
            'site_name': 'BoliBana Sugu',
            'site_phone': '',
            'site_email': '',
            'site_address': '',
            'site_rccm': '',
            'company_name': 'BoliBana Sugu',
            'company_type': 'Entreprise individuelle',
            'company_address': 'Bamako, Mali',
            'maintenance_mode': False,
        } 