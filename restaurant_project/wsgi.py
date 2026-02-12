"""
WSGI config for restaurant_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
import logging
import sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_project.settings')

# Configure logging early
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

try:
    application = get_wsgi_application()
    logger.info("Django application initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Django application: {str(e)}", exc_info=True)
    raise

# Health check function for database connectivity
def check_db_health():
    """Check if database is accessible"""
    from django.db import connections
    from django.db.utils import OperationalError
    
    try:
        connection = connections['default']
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        logger.info("Database connection health check: OK")
        return True
    except OperationalError as e:
        logger.error(f"Database connection health check failed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during database health check: {str(e)}", exc_info=True)
        return False
