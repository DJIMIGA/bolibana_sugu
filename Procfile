web: cd /app && PYTHONPATH=/app gunicorn wsgi:application --log-file - --log-level debug
release: cd /app && PYTHONPATH=/app python manage.py migrate --verbosity 2 