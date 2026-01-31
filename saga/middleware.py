import logging
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseForbidden
import time
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import REDIRECT_FIELD_NAME
from django_otp import user_has_device
from django_otp.middleware import OTPMiddleware
from django.contrib.auth.models import User
from django_otp import devices_for_user
from ipaddress import ip_address, ip_network
from django.utils import timezone
from accounts.models import AllowedIP

logger = logging.getLogger(__name__)

class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        timezone.activate(timezone.get_default_timezone())
        try:
            return self.get_response(request)
        finally:
            timezone.deactivate()

class SecurityMiddleware:
    """Middleware de sécurité pour la protection contre les attaques"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('security')
    
    def __call__(self, request):
        # Vérifications de sécurité
        if self._is_suspicious_request(request):
            self.logger.warning(f"Requête suspecte détectée: {request.path} depuis {self._get_client_ip(request)}")
            return HttpResponseForbidden('Requête suspecte détectée')
        
        response = self.get_response(request)
        
        # Journalisation des accès sensibles
        if self._is_sensitive_path(request.path):
            self._log_sensitive_access(request, response)
        
        return response
    
    def _is_suspicious_request(self, request):
        """Détecte les requêtes suspectes"""
        # Vérifier les en-têtes suspects
        suspicious_headers = [
            'HTTP_X_FORWARDED_FOR',
            'HTTP_X_REAL_IP',
            'HTTP_CLIENT_IP'
        ]
        
        for header in suspicious_headers:
            if header in request.META:
                ip = request.META[header]
                if self._is_blacklisted_ip(ip):
                    return True
        
        # Vérifier les patterns d'URL suspects
        suspicious_patterns = [
            '/admin/',
            '/wp-admin/',
            '/phpmyadmin/',
            '/.env',
            '/config.php',
            '/shell.php'
        ]
        
        for pattern in suspicious_patterns:
            if pattern in request.path.lower():
                return True
        
        return False
    
    def _is_blacklisted_ip(self, ip):
        """Vérifie si l'IP est blacklistée"""
        # Liste d'IPs blacklistées (à étendre selon vos besoins)
        blacklisted_ips = [
            '194.26.192.144',  # IP malveillante détectée le 17/07/2025 - tentative d'accès à .env
        ]
        return ip in blacklisted_ips
    
    def _is_sensitive_path(self, path):
        """Détermine si le chemin est sensible"""
        sensitive_paths = [
            '/admin/',
            '/accounts/login/',
            '/accounts/signup/',
            '/cart/payment/',
            '/api/'
        ]
        return any(sensitive in path for sensitive in sensitive_paths)
    
    def _log_sensitive_access(self, request, response):
        """Journalise les accès aux ressources sensibles"""
        client_ip = self._get_client_ip(request)
        user = getattr(request, 'user', None)
        user_email = getattr(user, 'email', 'Anonymous') if user and user.is_authenticated else 'Anonymous'
        
        self.logger.info(
            f"Accès sensible: {request.method} {request.path} - "
            f"IP: {client_ip} - User: {user_email} - "
            f"Status: {response.status_code}"
        )
    
    def _get_client_ip(self, request):
        """Récupère l'IP réelle du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

class FileRequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('file_requests')

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith('/media/') or request.path.startswith('/static/'):
            self.logger.info(f"Fichier demandé: {request.path} - Status: {response.status_code}")
        return response

class AdminIPRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('admin_access')

    def __call__(self, request):
        if request.path.startswith(f'/{settings.ADMIN_URL}'):
            client_ip = self.get_client_ip(request)
            if not self.is_ip_allowed(client_ip):
                self.logger.warning(f"Tentative d'accès non autorisé depuis l'IP: {client_ip}")
                return HttpResponseForbidden('Accès non autorisé')
            
            # Mise à jour de la dernière utilisation
            try:
                allowed_ip = AllowedIP.objects.get(ip_address=client_ip, is_active=True)
                if not allowed_ip.is_expired():
                    allowed_ip.update_last_used()
            except AllowedIP.DoesNotExist:
                pass

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    def is_ip_allowed(self, client_ip):
        try:
            # Vérifier d'abord les IPs dans settings.py (priorité haute)
            config_ips = settings.ADMIN_ALLOWED_IPS
            client_ip = ip_address(client_ip)
            
            # Vérifier si l'IP est dans la configuration
            if any(client_ip in ip_network(allowed_ip) for allowed_ip in config_ips):
                self.logger.info(f"IP {client_ip} autorisée via configuration")
                return True

            # Si non trouvée dans la config, vérifier la base de données
            try:
                allowed_ips = AllowedIP.objects.filter(
                    is_active=True,
                    expires_at__gt=timezone.now()
                ).values_list('ip_address', flat=True)

                if any(client_ip in ip_network(allowed_ip) for allowed_ip in allowed_ips):
                    self.logger.info(f"IP {client_ip} autorisée via base de données")
                    return True
            except Exception as e:
                self.logger.error(f"Erreur lors de la vérification en base de données: {str(e)}")
                # En cas d'erreur de base de données, on continue avec les IPs de configuration
                return any(client_ip in ip_network(allowed_ip) for allowed_ip in config_ips)

            self.logger.warning(f"IP {client_ip} non autorisée")
            return False

        except ValueError as e:
            self.logger.error(f"Erreur de validation d'IP: {client_ip} - {str(e)}")
            return False 