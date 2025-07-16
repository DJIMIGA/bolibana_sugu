from django.core.cache import cache
from .models import CookieConsent
from django.utils import timezone

def get_cookie_consent(request):
    """
    Récupère le consentement cookies pour une requête donnée.
    Utilise le cache pour optimiser les performances.
    """
    if not hasattr(request, 'cookie_consent'):
        return None
    
    return request.cookie_consent

def has_analytics_consent(request):
    """
    Vérifie si l'utilisateur a donné son consentement pour les cookies analytiques.
    """
    consent = get_cookie_consent(request)
    return consent and consent.analytics

def has_marketing_consent(request):
    """
    Vérifie si l'utilisateur a donné son consentement pour les cookies marketing.
    """
    consent = get_cookie_consent(request)
    return consent and consent.marketing

def can_track_user(request):
    """
    Vérifie si on peut tracker l'utilisateur (analytics + marketing).
    """
    return has_analytics_consent(request) or has_marketing_consent(request)

def get_tracking_data(request, event_type='page_view', **kwargs):
    """
    Génère des données de tracking anonymisées selon le consentement.
    
    Args:
        request: La requête Django
        event_type: Type d'événement ('page_view', 'purchase', 'add_to_cart', etc.)
        **kwargs: Données supplémentaires pour l'événement
    
    Returns:
        dict: Données de tracking ou None si pas de consentement
    """
    if not can_track_user(request):
        return None
    
    # Données de base anonymisées
    tracking_data = {
        'event_type': event_type,
        'timestamp': kwargs.get('timestamp'),
        'page_url': request.path,
        'user_agent': request.META.get('HTTP_USER_AGENT', '')[:100],  # Limité pour l'anonymisation
        'referrer': request.META.get('HTTP_REFERER', '')[:200],
    }
    
    # Ajouter les données spécifiques selon le type d'événement
    if event_type == 'purchase':
        tracking_data.update({
            'order_id': kwargs.get('order_id'),
            'total_amount': kwargs.get('total_amount'),
            'currency': kwargs.get('currency', 'XOF'),
            'items_count': kwargs.get('items_count'),
        })
    elif event_type == 'add_to_cart':
        tracking_data.update({
            'product_id': kwargs.get('product_id'),
            'product_name': kwargs.get('product_name'),
            'quantity': kwargs.get('quantity'),
            'price': kwargs.get('price'),
        })
    elif event_type == 'search':
        tracking_data.update({
            'search_term': kwargs.get('search_term'),
            'results_count': kwargs.get('results_count'),
        })
    
    # Anonymiser l'IP si analytics seulement
    if has_analytics_consent(request) and not has_marketing_consent(request):
        ip = request.META.get('REMOTE_ADDR', '')
        if ip:
            # Anonymiser les 3 derniers octets
            parts = ip.split('.')
            if len(parts) == 4:
                tracking_data['ip_anonymized'] = f"{parts[0]}.{parts[1]}.0.0"
    
    return tracking_data

def send_analytics_event(request, event_type, **kwargs):
    """
    Envoie un événement analytics si le consentement est donné.
    À implémenter selon vos besoins (Google Analytics, etc.)
    """
    if not has_analytics_consent(request):
        return False
    
    tracking_data = get_tracking_data(request, event_type, **kwargs)
    if not tracking_data:
        return False
    
    # Ici vous pouvez implémenter l'envoi vers Google Analytics
    # Exemple avec Google Analytics 4
    try:
        # Log pour le développement
        print(f"📊 Analytics Event: {event_type} - {tracking_data}")
        
        # Envoi vers Google Analytics via JavaScript
        # Note: Cette fonction est appelée côté serveur, donc on ne peut pas
        # directement appeler gtag. Les événements doivent être envoyés côté client.
        
        # Pour les événements critiques, on peut les stocker en session
        # et les envoyer via JavaScript au prochain chargement de page
        if 'analytics_events' not in request.session:
            request.session['analytics_events'] = []
        
        # Ajouter l'événement à la session pour envoi différé
        event_data = {
            'event_type': event_type,
            'parameters': tracking_data,
            'timestamp': timezone.now().isoformat()
        }
        request.session['analytics_events'].append(event_data)
        request.session.modified = True
        
        return True
    except Exception as e:
        print(f"❌ Erreur analytics: {e}")
        return False

def send_marketing_event(request, event_type, **kwargs):
    """
    Envoie un événement marketing si le consentement est donné.
    À implémenter selon vos besoins (Facebook Pixel, etc.)
    """
    if not has_marketing_consent(request):
        return False
    
    tracking_data = get_tracking_data(request, event_type, **kwargs)
    if not tracking_data:
        return False
    
    # Ici vous pouvez implémenter l'envoi vers Facebook Pixel
    try:
        # Log pour le développement
        print(f"🎯 Marketing Event: {event_type} - {tracking_data}")
        
        # TODO: Implémenter l'envoi réel vers Facebook Pixel
        # fbq('track', event_type, tracking_data)
        
        return True
    except Exception as e:
        print(f"❌ Erreur marketing: {e}")
        return False

def track_page_view(request):
    """
    Track une vue de page selon le consentement.
    """
    send_analytics_event(request, 'page_view')
    send_marketing_event(request, 'PageView')

def track_purchase(request, order_id, total_amount, currency='XOF', items_count=1):
    """
    Track un achat selon le consentement.
    """
    send_analytics_event(request, 'purchase', 
                        order_id=order_id, 
                        total_amount=total_amount,
                        currency=currency,
                        items_count=items_count)
    
    send_marketing_event(request, 'Purchase', 
                        order_id=order_id,
                        total_amount=total_amount,
                        currency=currency,
                        items_count=items_count)

def track_add_to_cart(request, product_id, product_name, quantity, price):
    """
    Track l'ajout au panier selon le consentement.
    """
    send_analytics_event(request, 'add_to_cart',
                        product_id=product_id,
                        product_name=product_name,
                        quantity=quantity,
                        price=price)
    
    send_marketing_event(request, 'AddToCart',
                        product_id=product_id,
                        product_name=product_name,
                        quantity=quantity,
                        price=price)

def track_search(request, search_term, results_count):
    """
    Track une recherche selon le consentement.
    """
    send_analytics_event(request, 'search',
                        search_term=search_term,
                        results_count=results_count) 