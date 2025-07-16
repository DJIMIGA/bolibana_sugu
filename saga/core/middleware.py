"""
Middlewares personnalisés pour l'app core.

- CookieConsentMiddleware : gestion du consentement cookies
- AnalyticsMiddleware : tracking automatique
- MaintenanceModeMiddleware : affiche une page de maintenance si MAINTENANCE_MODE=true
"""
import os
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from .models import CookieConsent, SiteConfiguration
from .utils import track_page_view

class CookieConsentMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
        session_id = request.session.session_key or request.session._get_or_create_session_key()
        consent = None
        try:
            # Chercher d'abord par utilisateur, puis par session
            if user:
                consent = CookieConsent.objects.filter(user=user).order_by('-updated_at').first()
                print(f"🔍 Middleware - Cherche par utilisateur: {user}")
            if not consent:
                consent = CookieConsent.objects.filter(session_id=session_id).order_by('-updated_at').first()
                print(f"🔍 Middleware - Cherche par session: {session_id[:10]}...")
            
            print(f"🔍 Middleware - User: {user}, Session: {session_id[:10]}..., Consent: {consent}")
            if consent:
                print(f"🔍 Middleware - Analytics: {consent.analytics}, Marketing: {consent.marketing}")
        except Exception as e:
            print(f"❌ Erreur middleware: {e}")
            consent = None
        request.cookie_consent = consent
        response = self.get_response(request)
        return response

class AnalyticsMiddleware:
    """
    Middleware pour tracker automatiquement les vues de pages.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Tracker la vue de page si c'est une requête GET normale
        if request.method == 'GET' and not request.headers.get('HX-Request'):
            # Exclure les pages d'administration et les fichiers statiques
            if not request.path.startswith('/admin/') and not request.path.startswith('/static/'):
                try:
                    track_page_view(request)
                except Exception as e:
                    # Log l'erreur mais ne pas bloquer la requête
                    print(f"❌ Erreur tracking page view: {e}")
        
        return response 

class MaintenanceModeMiddleware:
    """
    Affiche une page de maintenance si maintenance_mode est activé dans la config du site,
    sauf pour les superusers/admins connectés et les URLs d'authentification.
    Fallback sur la variable d'environnement MAINTENANCE_MODE si la base n'est pas accessible.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            config = SiteConfiguration.get_config()
            maintenance_mode = getattr(config, 'maintenance_mode', False)
        except Exception:
            # Fallback Heroku (ex: migration KO)
            maintenance_mode = os.environ.get('MAINTENANCE_MODE', 'false').lower() == 'true'
        
        # Si le mode maintenance n'est pas activé, continuer normalement
        if not maintenance_mode:
            return self.get_response(request)
        
        # URLs autorisées même en mode maintenance
        allowed_urls = [
            '/accounts/login/',  # Page de connexion
            '/accounts/logout/',  # Page de déconnexion
            '/accounts/2fa/setup/',  # Configuration 2FA
            '/accounts/2fa/verify/',  # Vérification 2FA
            '/bismillah/',  # Admin Django
            '/bismillah/login/',  # Login admin Django
            '/bismillah/logout/',  # Logout admin Django
            '/static/',  # Fichiers statiques
            '/media/',  # Fichiers médias
        ]
        
        # Vérifier si l'URL actuelle est autorisée
        current_path = request.path
        is_allowed_url = any(current_path.startswith(url) for url in allowed_urls)
        
        # Autoriser l'accès si :
        # 1. L'utilisateur est connecté ET est admin/staff, OU
        # 2. L'URL est dans la liste des URLs autorisées
        if (request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)) or is_allowed_url:
            return self.get_response(request)
        
        # Sinon, afficher la page de maintenance
        return render(request, 'core/maintenance.html', status=503) 