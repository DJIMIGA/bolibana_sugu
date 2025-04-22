"""
WSGI config for saga project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import logging
import sys
from waitress import serve

# Configuration des logs
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('wsgi.log')
    ]
)
logger = logging.getLogger(__name__)

logger.info("Démarrage de l'application WSGI")
logger.debug("PYTHONPATH: %s", os.environ.get('PYTHONPATH', 'Non défini'))
logger.debug("DJANGO_SETTINGS_MODULE: %s", os.environ.get('DJANGO_SETTINGS_MODULE', 'Non défini'))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')

logger.info("Chargement de l'application Django")
application = get_wsgi_application()
logger.info("Application WSGI chargée avec succès")

if __name__ == '__main__':
    logger.info("Démarrage du serveur Waitress")
    serve(application, host='0.0.0.0', port=8000)
