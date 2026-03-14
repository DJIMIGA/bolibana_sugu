from django.http import HttpResponseForbidden
from django.conf import settings
from django.core.cache import cache
import hashlib
import time

class PaymentSecurityMiddleware:
    """
    Middleware pour sécuriser les vues de paiement
    - Limite le taux de requêtes
    - Vérifie les tentatives de fraude
    - Bloque les IPs suspectes
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Vérifier si c'est une vue de paiement
        if self._is_payment_view(request.path):
            # Vérifier le taux de requêtes
            if not self._check_rate_limit(request):
                return HttpResponseForbidden("Trop de requêtes. Veuillez réessayer plus tard.")
            
            # Vérifier les tentatives de fraude
            if self._is_suspicious_request(request):
                return HttpResponseForbidden("Requête suspecte détectée.")
        
        # Vérifier si c'est une vue du panier
        if self._is_cart_view(request.path):
            # Protection contre les attaques sur le panier
            if not self._check_cart_security(request):
                return HttpResponseForbidden("Action non autorisée sur le panier.")
        
        response = self.get_response(request)
        return response
    
    def _is_payment_view(self, path):
        """Vérifie si le chemin correspond à une vue de paiement"""
        payment_paths = [
            '/cart/payment/',
            '/cart/create-checkout-session/',
            '/cart/stripe/webhook/',
            '/cart/payment-success/',
            '/cart/payment-cancel/',
        ]
        return any(payment_path in path for payment_path in payment_paths)
    
    def _is_cart_view(self, path):
        """Vérifie si le chemin correspond à une vue du panier"""
        cart_paths = [
            '/cart/add_to_cart/',
            '/cart/increase-quantity/',
            '/cart/decrease-quantity/',
            '/cart/remove-item/',
        ]
        return any(cart_path in path for cart_path in cart_paths)
    
    def _check_cart_security(self, request):
        """Vérifie la sécurité des actions sur le panier"""
        client_ip = self._get_client_ip(request)
        cache_key = f"cart_security:{client_ip}"
        
        # Limite : 100 actions par minute sur le panier
        current_time = int(time.time())
        minute_ago = current_time - 60
        
        # Récupérer les actions récentes
        actions = cache.get(cache_key, [])
        
        # Filtrer les actions de la dernière minute
        recent_actions = [action for action in actions if action > minute_ago]
        
        if len(recent_actions) >= 100:
            return False
        
        # Ajouter l'action actuelle
        recent_actions.append(current_time)
        cache.set(cache_key, recent_actions, 60)
        
        return True
    
    def _check_rate_limit(self, request):
        """Vérifie le taux de requêtes par IP"""
        client_ip = self._get_client_ip(request)
        cache_key = f"payment_rate_limit:{client_ip}"
        
        # Limite: 10 requêtes par minute
        current_time = int(time.time())
        minute_ago = current_time - 60
        
        # Récupérer les timestamps des requêtes récentes
        timestamps = cache.get(cache_key, [])
        
        # Filtrer les requêtes de la dernière minute
        recent_requests = [ts for ts in timestamps if ts > minute_ago]
        
        if len(recent_requests) >= 10:
            return False
        
        # Ajouter la requête actuelle
        recent_requests.append(current_time)
        cache.set(cache_key, recent_requests, 60)  # Expire dans 1 minute
        
        return True
    
    def _is_suspicious_request(self, request):
        """Détecte les requêtes suspectes"""
        # Vérifier l'User-Agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if not user_agent or len(user_agent) < 10:
            return True
        
        # Vérifier les en-têtes suspects
        suspicious_headers = [
            'HTTP_X_FORWARDED_FOR',
            'HTTP_CLIENT_IP',
            'HTTP_X_REAL_IP',
        ]
        
        for header in suspicious_headers:
            if header in request.META:
                ip = request.META[header]
                if self._is_blacklisted_ip(ip):
                    return True
        
        return False
    
    def _get_client_ip(self, request):
        """Récupère l'IP réelle du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _is_blacklisted_ip(self, ip):
        """Vérifie si l'IP est blacklistée"""
        # Liste d'IPs blacklistées (à configurer selon vos besoins)
        blacklisted_ips = getattr(settings, 'PAYMENT_BLACKLISTED_IPS', [])
        return ip in blacklisted_ips 