"""
WSGI config for saga project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys
import logging

# Configuration des logs
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Ajouter le chemin de l'application au PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
logger.debug(f"Current directory: {current_dir}")
sys.path.append(current_dir)

logger.debug(f"PYTHONPATH: {sys.path}")

try:
    from django.core.wsgi import get_wsgi_application
    logger.debug("Django import successful")
except ImportError as e:
    logger.error(f"Django import failed: {e}")
    raise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.saga.settings')
logger.debug(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")

try:
    application = get_wsgi_application()
    logger.debug("WSGI application created successfully")
except Exception as e:
    logger.error(f"Failed to create WSGI application: {e}")
    raise
