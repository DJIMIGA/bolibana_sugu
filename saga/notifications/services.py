import logging
import requests
from .models import PushToken, Notification

logger = logging.getLogger('saga.notifications')

EXPO_PUSH_URL = 'https://exp.host/--/api/v2/push/send'


def send_push_notification(user, title, body, data=None):
    """
    Envoie une notification push à tous les appareils actifs d'un utilisateur
    via l'API Expo Push et stocke la notification en base. Ne lève jamais d'exception.
    """
    # Toujours stocker la notification en base (même si push désactivé)
    try:
        Notification.objects.create(user=user, title=title, body=body, data=data or {})
    except Exception:
        logger.warning("Impossible de stocker la notification pour %s", user.email, exc_info=True)

    if not getattr(user, 'notifications_enabled', True):
        return

    tokens = list(
        PushToken.objects.filter(user=user, is_active=True).values_list('token', flat=True)
    )
    if not tokens:
        return

    messages = []
    for token in tokens:
        message = {
            'to': token,
            'sound': 'default',
            'title': title,
            'body': body,
        }
        if data:
            message['data'] = data
        messages.append(message)

    try:
        response = requests.post(
            EXPO_PUSH_URL,
            json=messages,
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            timeout=10,
        )
        result = response.json()

        # Désactiver les tokens invalides
        if 'data' in result:
            for i, ticket in enumerate(result['data']):
                if ticket.get('status') == 'error':
                    error_type = ticket.get('details', {}).get('error')
                    if error_type == 'DeviceNotRegistered':
                        PushToken.objects.filter(token=tokens[i]).update(is_active=False)
                        logger.info("Token push désactivé (DeviceNotRegistered): %s", tokens[i][:20])

        logger.info(
            "Notification push envoyée à %s (%d appareil(s)): %s",
            user.email, len(tokens), title,
        )
    except Exception as e:
        logger.error("Erreur envoi notification push à %s: %s", user.email, str(e))
