import logging
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from django.contrib.auth.signals import user_login_failed, user_logged_in
from django.dispatch import receiver


logger = logging.getLogger('security')


def _get_client_ip(request):
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _increment_login_failures(cache_key, window_seconds):
    data = cache.get(cache_key)
    if not data:
        data = {
            'count': 0,
            'first_seen': timezone.now().isoformat(),
        }
    data['count'] += 1
    cache.set(cache_key, data, timeout=window_seconds)
    return data['count'], data['first_seen']


@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    window_seconds = getattr(settings, 'LOGIN_FAILURE_WINDOW_SECONDS', 900)
    threshold = getattr(settings, 'LOGIN_FAILURE_ALERT_THRESHOLD', 5)
    client_ip = _get_client_ip(request) or 'unknown'
    username = credentials.get('username') or credentials.get('email') or 'unknown'
    cache_key = f"login_failed:{client_ip}"
    count, first_seen = _increment_login_failures(cache_key, window_seconds)

    if count == threshold or count % threshold == 0:
        logger.warning(
            "Alerte tentative de connexion anormale: ip=%s username=%s count=%s first_seen=%s window=%ss",
            client_ip,
            username,
            count,
            first_seen,
            window_seconds,
        )


@receiver(user_logged_in)
def reset_failed_login_counter(sender, request, user, **kwargs):
    client_ip = _get_client_ip(request)
    if client_ip:
        cache.delete(f"login_failed:{client_ip}")
