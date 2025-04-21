web: cd /app && PYTHONPATH=/app gunicorn saga.wsgi:application --log-file - --log-level debug
release: cd /app && PYTHONPATH=/app python saga/manage.py migrate --verbosity 2 