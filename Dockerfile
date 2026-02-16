FROM python:3.11-slim-bookworm

# Dépendances système (curl pour healthcheck, libpq pour PostgreSQL, libgl pour opencv)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq-dev \
    gcc \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Installer les dépendances Python en premier (meilleur cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le projet
COPY . .

# Collecter les fichiers statiques au build
RUN DJANGO_SETTINGS_MODULE=saga.settings \
    SECRET_KEY=build-placeholder \
    DEBUG=False \
    DB_NAME=placeholder \
    DB_USER=placeholder \
    DB_PASSWORD=placeholder \
    DB_HOST=placeholder \
    DB_PORT=5432 \
    python manage.py collectstatic --noinput 2>/dev/null || true

EXPOSE 8080

# Healthcheck pour éviter les 502 sur Elestio
HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
    CMD curl -f http://localhost:8080/health/ || exit 1

# Script d'entrée
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
