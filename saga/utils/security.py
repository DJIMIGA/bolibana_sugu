"""
Utilitaires de sécurité pour SagaKore
"""
import logging
from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger('security')

def require_2fa(view_func):
    """
    Décorateur pour exiger la 2FA sur une vue
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return login_required(view_func)(request, *args, **kwargs)
        
        if not hasattr(request.user, 'is_verified') or not request.user.is_verified():
            from django.contrib import messages
            from django.shortcuts import redirect
            from django.urls import reverse
            
            messages.warning(
                request, 
                "Cette action nécessite une vérification 2FA. "
                "Veuillez vous connecter avec votre code 2FA."
            )
            return redirect('accounts:verify_2fa')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view

def rate_limit_by_user(key_func=None, rate='5/m', method=['POST']):
    """
    Décorateur de rate limiting basé sur l'utilisateur
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.method not in method:
                return view_func(request, *args, **kwargs)
            
            # Générer la clé de cache
            if key_func:
                cache_key = key_func(request)
            else:
                cache_key = f"rate_limit_{request.user.id if request.user.is_authenticated else 'anonymous'}_{request.path}"
            
            # Vérifier le rate limit
            current_count = cache.get(cache_key, 0)
            if current_count >= int(rate.split('/')[0]):
                logger.warning(f"Rate limit dépassé pour {cache_key}")
                return HttpResponseForbidden("Trop de requêtes. Veuillez réessayer plus tard.")
            
            # Incrémenter le compteur
            cache.set(cache_key, current_count + 1, 60)  # Expire en 1 minute
            
            return view_func(request, *args, **kwargs)
        
        return _wrapped_view
    return decorator

def log_sensitive_action(action_name):
    """
    Décorateur pour journaliser les actions sensibles
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Journaliser avant l'action
            logger.info(
                f"Action sensible '{action_name}' initiée par "
                f"{request.user.email if request.user.is_authenticated else 'Anonymous'} "
                f"depuis {request.META.get('REMOTE_ADDR', 'Unknown IP')}"
            )
            
            try:
                result = view_func(request, *args, **kwargs)
                # Journaliser le succès
                logger.info(f"Action '{action_name}' réussie")
                return result
            except Exception as e:
                # Journaliser l'erreur
                logger.error(f"Action '{action_name}' échouée: {str(e)}")
                raise
        
        return _wrapped_view
    return decorator

def require_recent_activity(minutes=30):
    """
    Décorateur pour exiger une activité récente
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return login_required(view_func)(request, *args, **kwargs)
            
            # Vérifier la dernière activité
            last_activity = getattr(request.user, 'last_activity', None)
            if last_activity and timezone.now() - last_activity > timedelta(minutes=minutes):
                from django.contrib import messages
                from django.shortcuts import redirect
                
                messages.warning(
                    request,
                    f"Votre session a expiré. Veuillez vous reconnecter."
                )
                return redirect('accounts:login')
            
            # Mettre à jour la dernière activité
            request.user.last_activity = timezone.now()
            request.user.save(update_fields=['last_activity'])
            
            return view_func(request, *args, **kwargs)
        
        return _wrapped_view
    return decorator

def validate_user_permission(permission_check):
    """
    Décorateur pour valider les permissions utilisateur
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return login_required(view_func)(request, *args, **kwargs)
            
            if not permission_check(request.user):
                logger.warning(
                    f"Tentative d'accès non autorisé à {request.path} "
                    f"par {request.user.email}"
                )
                return HttpResponseForbidden("Accès non autorisé")
            
            return view_func(request, *args, **kwargs)
        
        return _wrapped_view
    return decorator 