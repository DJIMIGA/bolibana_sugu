#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import logging

# Configuration des logs
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def main():
    """Run administrative tasks."""
    try:
        # Définir le chemin de base
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        logger.debug(f"BASE_DIR: {BASE_DIR}")
        
        # Ajouter le chemin de base au PYTHONPATH
        if BASE_DIR not in sys.path:
            sys.path.insert(0, BASE_DIR)
        logger.debug(f"PYTHONPATH: {sys.path}")

        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saga.settings')
        logger.debug(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")

        try:
            from django.core.management import execute_from_command_line
            logger.debug("Django management import successful")
        except ImportError as exc:
            logger.error(f"Failed to import Django: {exc}")
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            ) from exc

        logger.debug(f"Command line arguments: {sys.argv}")
        execute_from_command_line(sys.argv)
        logger.debug("Command executed successfully")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise


if __name__ == '__main__':
    main()
