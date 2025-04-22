web: gunicorn saga.wsgi:application --log-file - --log-level debug
release: python saga/manage.py migrate --verbosity 2 