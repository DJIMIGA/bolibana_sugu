web: python manage.py collectstatic --noinput && gunicorn saga.wsgi:application
worker: python manage.py process_tasks
release: python manage.py migrate
