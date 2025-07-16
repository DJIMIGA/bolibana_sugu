"""
Configuration de Gunicorn pour l'application Django.
"""
import multiprocessing
import os

# Nombre de workers optimisé pour Heroku
workers = 1  # Réduit à 1 worker pour éviter les timeouts

# Configuration des workers
worker_class = 'sync'  # Plus simple et plus rapide
threads = 1
worker_connections = 1000

# Timeouts réduits pour éviter H12
timeout = 25  # Réduit de 30 à 25 secondes
keepalive = 2
graceful_timeout = 25

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Performance
max_requests = 1000
max_requests_jitter = 50

# Memory
worker_tmp_dir = '/dev/shm'
max_worker_connections = 1000

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Process naming
proc_name = 'saga'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None

# Configuration du proxy
forwarded_allow_ips = '*'
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}

# Configuration du worker
worker_timeout = 25
worker_abort_on_memory_error = True 