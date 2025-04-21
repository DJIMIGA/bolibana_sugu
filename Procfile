web: PYTHONPATH=/app gunicorn saga.saga.wsgi:application --log-file -
release: PYTHONPATH=/app python saga/manage.py migrate 