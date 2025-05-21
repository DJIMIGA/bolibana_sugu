import logging
from django.http import HttpResponseForbidden

class FileRequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('storages')

    def __call__(self, request):
        response = self.get_response(request)
        
        # Vérifier si c'est une requête pour un fichier statique ou média
        if request.path.startswith(('/static/', '/media/')):
            self.logger.info(
                f"File request: {request.path}",
                extra={
                    'path': request.path,
                    'method': request.method,
                    'status': response.status_code,
                }
            )
        
        # Logger les tentatives d'accès à l'interface d'administration
        if request.path.startswith(f'/{request.settings.ADMIN_URL}'):
            self.logger.info(
                f"Admin access attempt: {request.path}",
                extra={
                    'path': request.path,
                    'method': request.method,
                    'status': response.status_code,
                    'user': request.user.username if request.user.is_authenticated else 'anonymous',
                    'ip': request.META.get('REMOTE_ADDR'),
                }
            )
        
        return response

class AdminIPRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('django.security')

    def __call__(self, request):
        if request.path.startswith(f'/{request.settings.ADMIN_URL}'):
            client_ip = request.META.get('REMOTE_ADDR')
            if client_ip not in request.settings.ADMIN_ALLOWED_IPS:
                self.logger.warning(
                    f"Tentative d'accès admin bloquée depuis l'IP: {client_ip}",
                    extra={
                        'ip': client_ip,
                        'path': request.path,
                        'user': request.user.username if request.user.is_authenticated else 'anonymous'
                    }
                )
                return HttpResponseForbidden("Accès non autorisé")
        return self.get_response(request) 