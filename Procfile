web: cd saga && gunicorn saga.wsgi:application --log-file - --log-level debug
release: cd saga && python manage.py migrate --verbosity 2 