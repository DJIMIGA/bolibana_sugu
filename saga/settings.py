ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    '.ngrok.io',
    '*',  # Temporairement pour le développement
] 

CSRF_TRUSTED_ORIGINS = [
    'https://*.ngrok.io',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
] 