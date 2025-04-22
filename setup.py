from setuptools import setup, find_packages

setup(
    name="saga",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=5.1.4',
        'gunicorn',
        'whitenoise',
        'dj-database-url',
        'python-dotenv',
        'phonenumber_field',
        'django-htmx',
        'widget-tweaks',
        'djangorestframework',
        'corsheaders',
        'django-filter',
        'djangorestframework-simplejwt',
        'stripe',
        'crispy-forms',
        'crispy-tailwind',
    ],
) 