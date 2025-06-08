from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from .models import AllowedIP
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

class IPRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Vérifier si l'utilisateur est authentifié et est staff
        if request.user.is_authenticated and request.user.is_staff:
            # Obtenir l'IP du client
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                client_ip = x_forwarded_for.split(',')[0]
            else:
                client_ip = request.META.get('REMOTE_ADDR')

            # Vérifier si l'IP est autorisée
            allowed_ip = AllowedIP.objects.filter(
                ip_address=client_ip,
                is_active=True,
                expires_at__gt=timezone.now()
            ).first()

            if not allowed_ip:
                # Si l'utilisateur n'est pas sur une IP autorisée
                if request.path.startswith('/admin/'):
                    messages.error(
                        request,
                        f'Accès refusé : Votre adresse IP ({client_ip}) n\'est pas autorisée à accéder à l\'administration. '
                        'Veuillez contacter un administrateur pour obtenir l\'accès.'
                    )
                    # Redirection vers la page de login avec un message d'erreur
                    return redirect('admin:login')

        response = self.get_response(request)
        return response

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ne pas réinitialiser l'utilisateur s'il est déjà authentifié
        if not request.user.is_authenticated and not hasattr(request.user, 'email'):
            request.user = AnonymousUser()
            request.user.email = ''
        
        response = self.get_response(request)
        return response 