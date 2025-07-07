"""
Contexte processeur pour exposer les paramètres de pays par défaut aux templates
"""

def default_country_settings(request):
    """
    Contexte processeur pour exposer les paramètres de pays par défaut
    """
    return {
        'DEFAULT_COUNTRY_CODE': 'ML',
        'DEFAULT_COUNTRY_NAME': 'Mali',
        'DEFAULT_COUNTRY_FLAG': '🇲🇱',
        'DEFAULT_CURRENCY': 'XOF',
        'DEFAULT_CURRENCY_SYMBOL': 'FCFA',
    } 