from setuptools import setup, find_packages

setup(
    name="saga",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=5.1.4',
        'waitress>=3.0.2',
        'whitenoise>=6.6.0',
        'dj-database-url>=2.1.0',
        'python-dotenv>=1.0.0',
        'phonenumber_field>=7.2.0',
        'django-htmx>=1.21.0',
        'django-widget-tweaks>=1.5.0',
        'djangorestframework>=3.14.0',
        'django-cors-headers>=4.3.1',
        'django-filter>=23.5',
        'djangorestframework-simplejwt>=5.3.1',
        'stripe>=7.10.0',
        'django-crispy-forms>=2.1',
        'crispy-tailwind>=0.5.0',
    ],
) 