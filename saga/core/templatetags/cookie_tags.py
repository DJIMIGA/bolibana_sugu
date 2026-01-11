from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag(takes_context=True)
def has_cookie_consent(context, cookie_type):
    """
    Vérifie si l'utilisateur a donné son consentement pour un type de cookie spécifique.
    
    Usage:
    {% has_cookie_consent 'analytics' as analytics_consent %}
    {% has_cookie_consent 'marketing' as marketing_consent %}
    """
    request = context.get('request')
    if not request or not hasattr(request, 'cookie_consent') or not request.cookie_consent:
        return False
    
    if cookie_type == 'analytics':
        return request.cookie_consent.analytics
    elif cookie_type == 'marketing':
        return request.cookie_consent.marketing
    elif cookie_type == 'essential':
        return True  # Les cookies essentiels sont toujours autorisés
    
    return False

@register.simple_tag(takes_context=True)
def render_analytics_scripts(context):
    """
    Affiche les scripts Google Analytics si le consentement est donné.
    
    Usage:
    {% render_analytics_scripts %}
    """
    request = context.get('request')
    if not request or not hasattr(request, 'cookie_consent') or not request.cookie_consent:
        return ""
    
    if not request.cookie_consent.analytics:
        return ""
    
    # Récupérer l'ID Google Analytics depuis la configuration
    try:
        from core.models import SiteConfiguration
        config = SiteConfiguration.get_config()
        ga_id = config.google_analytics_id
        if not ga_id:
            return ""
    except Exception:
        return ""
    
    # Configuration des cookies selon l'environnement
    from django.conf import settings
    if settings.DEBUG:
        # En développement local, pas de restrictions de cookies
        cookie_config = ""
    else:
        # En production, cookies sécurisés
        cookie_config = "'cookie_flags': 'SameSite=None;Secure'"
    
    # Récupérer les événements stockés en session
    analytics_events = request.session.get('analytics_events', [])
    events_script = ""
    
    if analytics_events:
        events_script = """
        // Envoyer les événements stockés en session
        const storedEvents = """ + str(analytics_events) + """;
        storedEvents.forEach(function(eventData) {
            gtag('event', eventData.event_type, eventData.parameters);
        });
        """
        # Vider les événements après envoi
        request.session['analytics_events'] = []
        request.session.modified = True
    
    return f"""
    <!-- Google Analytics 4 -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', '{ga_id}', {{
            'anonymize_ip': true,
            'send_page_view': true,
            'debug_mode': {str(settings.DEBUG).lower()}
            {',' + cookie_config if cookie_config else ''}
        }});
        
        // Logs désactivés en production
        
        {events_script}
    </script>
    """

@register.simple_tag(takes_context=True)
def render_marketing_scripts(context):
    """
    Affiche les scripts marketing (Facebook Pixel, etc.) si le consentement est donné.
    
    Usage:
    {% render_marketing_scripts %}
    """
    request = context.get('request')
    if not request or not hasattr(request, 'cookie_consent') or not request.cookie_consent:
        return ""
    
    if not request.cookie_consent.marketing:
        return ""
    
    # Récupérer l'ID Facebook Pixel depuis la configuration
    try:
        from core.models import SiteConfiguration
        config = SiteConfiguration.get_config()
        pixel_id = config.facebook_pixel_id
        if not pixel_id:
            return ""
    except Exception:
        return ""
    
    # Récupérer les événements stockés en session
    marketing_events = request.session.get('marketing_events', [])
    events_script = ""
    
    if marketing_events:
        events_script = """
        // Envoyer les événements stockés en session
        const storedMarketingEvents = """ + str(marketing_events) + """;
        storedMarketingEvents.forEach(function(eventData) {
            fbq('track', eventData.event_type, eventData.parameters);
        });
        """
        # Vider les événements après envoi
        request.session['marketing_events'] = []
        request.session.modified = True
    
    return f"""
    <!-- Facebook Pixel -->
    <script>
        !function(f,b,e,v,n,t,s)
        {{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?
        n.callMethod.apply(n,arguments):n.queue.push(arguments)}};
        if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
        n.queue=[];t=b.createElement(e);t.async=!0;
        t.src=v;s=b.getElementsByTagName(e)[0];
        s.parentNode.insertBefore(t,s)}}(window, document,'script',
        'https://connect.facebook.net/en_US/fbevents.js');
        fbq('init', '{pixel_id}');
        fbq('track', 'PageView');
        
        // Logs désactivés en production
        
        {events_script}
    </script>
    <noscript>
        <img height="1" width="1" style="display:none"
        src="https://www.facebook.com/tr?id={pixel_id}&ev=PageView&noscript=1"/>
    </noscript>
    """

@register.simple_tag(takes_context=True)
def render_cookie_conditional_scripts(context):
    """
    Affiche tous les scripts conditionnels selon le consentement.
    
    Usage:
    {% render_cookie_conditional_scripts %}
    """
    analytics_script = render_analytics_scripts(context)
    marketing_script = render_marketing_scripts(context)
    
    return f"{analytics_script}\n{marketing_script}" 