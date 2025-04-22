"""
WSGI config for saga project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.saga.settings')

application = get_wsgi_application() 