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
from .models import CookieConsent
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
    Affiche une page de maintenance si MAINTENANCE_MODE=true,
    sauf pour les superusers/admins connectés.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        maintenance_mode = os.environ.get('MAINTENANCE_MODE', 'false').lower() == 'true'
        # Autoriser les superusers/admins à accéder au site même en maintenance
        if maintenance_mode and not (request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff)):
            return render(request, 'core/maintenance.html', status=503)
        return self.get_response(request) 