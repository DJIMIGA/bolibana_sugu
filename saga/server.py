from waitress import serve
from django.core.wsgi import get_wsgi_application
import os
import logging

import sys
import os

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
application = get_wsgi_application()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Démarrage du serveur sur le port {port}")
    serve(application, host='0.0.0.0', port=port, threads=4) 