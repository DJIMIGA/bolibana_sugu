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

logger = logging.getLogger(__name__)

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
            client_ip = request.META.get('REMOTE_ADDR')
            if client_ip not in settings.ADMIN_ALLOWED_IPS:
                self.logger.warning(f"Tentative d'accès admin depuis IP non autorisée: {client_ip}")
                return redirect('home')
        return self.get_response(request) 