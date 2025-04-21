"""
WSGI config for saga project.
"""

import os
import sys
import logging

# Configuration des logs
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Nettoyer le PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
logger.debug(f"Current directory: {current_dir}")

# Réinitialiser sys.path
sys.path = [p for p in sys.path if not p.endswith('.env') and not p.endswith('module_teste.py')]
sys.path.append(current_dir)
logger.debug(f"PYTHONPATH nettoyé: {sys.path}")

try:
    from django.core.wsgi import get_wsgi_application
    logger.debug("Django import successful")
except ImportError as e:
    logger.error(f"Django import failed: {e}")
    raise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
logger.debug(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")

try:
    application = get_wsgi_application()
    logger.debug("WSGI application created successfully")
except Exception as e:
    logger.error(f"Failed to create WSGI application: {e}")
    raise 