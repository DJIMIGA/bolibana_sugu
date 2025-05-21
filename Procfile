web: gunicorn saga.wsgi:application --config gunicorn_config.py
release: python manage.py migrate && python manage.py collectstatic --noinput
worker: python manage.py process_tasks
