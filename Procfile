web: gunicorn saga.wsgi:application --config gunicorn_config.py --max-requests 1000 --max-requests-jitter 50
release: python manage.py migrate && python manage.py collectstatic --noinput
worker: python manage.py process_tasks
