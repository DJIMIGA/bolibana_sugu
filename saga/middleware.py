from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.conf import settings
import time

class AdminLoginAttemptMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_attempts = 5  # Nombre maximum de tentatives
        self.lockout_time = 300  # Temps de blocage en secondes (5 minutes)

    def __call__(self, request):
        if request.path.startswith(f'/{settings.ADMIN_URL}') and request.method == 'POST':
            ip = self.get_client_ip(request)
            cache_key = f'admin_login_attempts_{ip}'
            
            # Vérifier si l'IP est bloquée
            if cache.get(f'admin_blocked_{ip}'):
                return HttpResponseForbidden('Trop de tentatives de connexion. Veuillez réessayer plus tard.')
            
            # Incrémenter le compteur de tentatives
            attempts = cache.get(cache_key, 0) + 1
            cache.set(cache_key, attempts, self.lockout_time)
            
            # Bloquer l'IP si trop de tentatives
            if attempts >= self.max_attempts:
                cache.set(f'admin_blocked_{ip}', True, self.lockout_time)
                return HttpResponseForbidden('Trop de tentatives de connexion. Veuillez réessayer plus tard.')
        
        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 