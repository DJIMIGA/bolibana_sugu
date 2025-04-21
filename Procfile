web: cd /app && PYTHONPATH=/app gunicorn saga.saga.wsgi:application --log-file -
release: cd /app && PYTHONPATH=/app python saga/manage.py migrate 