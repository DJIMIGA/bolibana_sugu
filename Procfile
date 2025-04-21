web: gunicorn wsgi:application --log-file - --log-level debug
release: python manage.py migrate --verbosity 2 