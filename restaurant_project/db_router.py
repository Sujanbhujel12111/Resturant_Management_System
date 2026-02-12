"""
Database router for handling Supabase pooler fallback.
Automatically switches to direct endpoint if pooler fails.
"""

import logging
from django.db import connections
from django.db.utils import OperationalError, DatabaseError
import threading

logger = logging.getLogger(__name__)

# Thread-local storage for fallback state
_thread_local = threading.local()


class PoolerFallbackRouter:
    """
    Database router that monitors pooler connection health.
    If pooler fails, routes future queries through direct endpoint.
    """
    
    def __init__(self):
        self._pooler_failed = False
        self._fallback_used = False
    
    def db_for_read(self, model, **hints):
        """Route read operations to appropriate database."""
        if self._should_use_fallback():
            return 'fallback'
        return 'default'
    
    def db_for_write(self, model, **hints):
        """Route write operations to appropriate database."""
        if self._should_use_fallback():
            return 'fallback'
        return 'default'
    
    def _should_use_fallback(self):
        """Check if we should use fallback database."""
        # If we've already switched, stay on fallback
        if getattr(_thread_local, 'using_fallback', False):
            return True
        return False
    
    @staticmethod
    def test_connection(db_alias='default'):
        """Test if a database connection is available."""
        try:
            with connections[db_alias].cursor() as cursor:
                cursor.execute('SELECT 1')
            return True
        except (OperationalError, DatabaseError) as e:
            error_msg = str(e).lower()
            # Check for DNS/connectivity errors that indicate unreachable endpoint
            if any(keyword in error_msg for keyword in [
                'could not translate host name',
                'name or service not known',
                'connection refused',
                'connection timeout',
                'network is unreachable',
                'no route to host',
            ]):
                return False
            # Re-raise other database errors
            raise
        except Exception:
            return False


def check_pooler_health_on_startup():
    """
    Check pooler health at startup.
    If pooler fails, mark fallback for use.
    Only use fallback if pooler is completely unreachable.
    """
    from django.conf import settings
    
    # Only do this if we have a fallback database configured
    if 'fallback' not in settings.DATABASES:
        logger.info("✓ No fallback database configured")
        return
    
    logger.info("Checking Supabase pooler connection...")
    router = PoolerFallbackRouter()
    
    # Always start with pooler - it's more reliable and scalable
    logger.info("Using pooler endpoint (primary)")
    
    # Test pooler connection in background, decide on fallback only if it truly fails
    try:
        if router.test_connection('default'):
            logger.info("✓ Pooler endpoint is healthy")
            return
        else:
            logger.warning("⚠ Pooler endpoint is unreachable")
            
            # Test if fallback is available
            try:
                if router.test_connection('fallback'):
                    logger.warning("🔄 Switching to direct endpoint as fallback")
                    _thread_local.using_fallback = True
                else:
                    logger.error("❌ Both pooler and direct endpoints are unreachable")
                    logger.warning("⚠ Attempting to continue with pooler (may fail at runtime)")
            except Exception as e:
                logger.warning(f"⚠ Could not test fallback: {e}")
                
    except Exception as e:
        logger.error(f"Error checking pooler health: {e}")
        logger.warning("Proceeding with pooler as primary database")


def get_active_db_alias():
    """Get the currently active database alias."""
    if getattr(_thread_local, 'using_fallback', False):
        return 'fallback'
    return 'default'


def get_active_db_host():
    """Get the currently active database host for logging."""
    from django.conf import settings
    alias = get_active_db_alias()
    return settings.DATABASES.get(alias, {}).get('HOST', 'unknown')
