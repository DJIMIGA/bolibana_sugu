"""
WSGI config for saga project.
"""

import os
import sys

# Ajouter le chemin de l'application au PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.saga.settings')

application = get_wsgi_application() 