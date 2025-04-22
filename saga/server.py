from waitress import serve
from django.core.wsgi import get_wsgi_application
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
application = get_wsgi_application()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    serve(application, host='0.0.0.0', port=port) 