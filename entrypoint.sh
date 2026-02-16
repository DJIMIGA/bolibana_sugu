#!/bin/bash
# Entrypoint SagaKore - Elestio
# Pas de "set -e" : si une étape échoue, le serveur doit quand même démarrer

echo "=== SagaKore - Démarrage ==="

# Attendre que PostgreSQL soit prêt
echo "[0/3] Attente de PostgreSQL..."
MAX_RETRIES=30
RETRY=0
until python -c "
import os, psycopg2
psycopg2.connect(
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT')
)
print('PostgreSQL OK')
" 2>/dev/null; do
    RETRY=$((RETRY+1))
    if [ $RETRY -ge $MAX_RETRIES ]; then
        echo "[WARN] PostgreSQL non disponible après ${MAX_RETRIES} tentatives, on continue..."
        break
    fi
    echo "  Tentative $RETRY/$MAX_RETRIES..."
    sleep 2
done

# Migrations (non bloquant)
echo "[1/3] Migrations de la base de données..."
python manage.py migrate --noinput 2>&1 || echo "[WARN] Migrations échouées, le serveur démarre quand même"

# Collectstatic (non bloquant)
echo "[2/3] Collecte des fichiers statiques..."
python manage.py collectstatic --noinput 2>&1 || echo "[WARN] Collectstatic échoué"

# Démarrage de Gunicorn
echo "[3/3] Démarrage de Gunicorn sur le port 8080..."
exec gunicorn saga.wsgi:application \
    --bind 0.0.0.0:8080 \
    --workers 3 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
