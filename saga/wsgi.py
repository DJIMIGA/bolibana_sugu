"""
WSGI config for saga project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import logging
import sys
from pathlib import Path

# Configuration des logs
logging.basicConfig(
    level=logging.INFO if os.environ.get('DJANGO_ENV') == 'production' else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('wsgi.log')
    ]
)
logger = logging.getLogger(__name__)

# Ajouter le répertoire parent au PYTHONPATH
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

logger.info("Démarrage de l'application WSGI")
logger.debug("PYTHONPATH: %s", os.environ.get('PYTHONPATH', 'Non défini'))
logger.debug("DJANGO_SETTINGS_MODULE: %s", os.environ.get('DJANGO_SETTINGS_MODULE', 'Non défini'))

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')

logger.info("Chargement de l'application Django")
application = get_wsgi_application()

# Configuration de WhiteNoise pour servir les fichiers statiques
application = WhiteNoise(
    application,
    root=os.path.join(BASE_DIR, 'staticfiles'),
    prefix='/static/',
    max_age=31536000  # 1 an
)

logger.info("Application WSGI chargée avec succès")
