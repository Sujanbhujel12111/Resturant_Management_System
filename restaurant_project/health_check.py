"""
Database health check utility for diagnosing connection issues.
Can be imported and used as: from restaurant_project.health_check import check_database_health
"""

import logging
import sys
from django.db import connections
from django.db.utils import OperationalError, ProgrammingError
from decouple import config

logger = logging.getLogger(__name__)


def check_database_health(verbose=True):
    """
    Comprehensive database health check.
    
    Returns:
        dict: Status information including connection test, migration status, etc.
    """
    
    result = {
        'status': 'unknown',
        'message': '',
        'connection_available': False,
        'migration_status': 'unknown',
        'errors': []
    }
    
    # Check environment variables are set
    required_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing_vars = [var for var in required_vars if not config(var, default=None)]
    
    if missing_vars:
        result['errors'].append(f"Missing environment variables: {', '.join(missing_vars)}")
        result['status'] = 'error'
        if verbose:
            print(f"❌ ERROR: Missing environment variables: {', '.join(missing_vars)}")
        return result
    
    if verbose:
        print("✓ Environment variables are set")
    
    # Test connection
    try:
        connection = connections['default']
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        result['connection_available'] = True
        if verbose:
            print("✓ Database connection successful")
    except OperationalError as e:
        result['errors'].append(f"Connection failed: {str(e)}")
        result['status'] = 'error'
        if verbose:
            print(f"❌ Connection failed: {str(e)}")
        return result
    except Exception as e:
        result['errors'].append(f"Unexpected error: {str(e)}")
        result['status'] = 'error'
        if verbose:
            print(f"❌ Unexpected error: {str(e)}")
        return result
    
    # Check if tables exist
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            table_count = cursor.fetchone()[0]
        
        if table_count > 0:
            result['migration_status'] = 'tables_exist'
            if verbose:
                print(f"✓ Database has {table_count} tables")
        else:
            result['migration_status'] = 'migrations_needed'
            if verbose:
                print("⚠ No tables found - migrations may be needed")
    except Exception as e:
        result['errors'].append(f"Failed to check tables: {str(e)}")
        if verbose:
            print(f"⚠ Failed to check tables: {str(e)}")
    
    if not result['errors']:
        result['status'] = 'healthy'
        if verbose:
            print("\n✓ Database health check PASSED")
    
    return result


def print_connection_info():
    """Print database connection configuration (with password masked)"""
    print("\n=== Database Connection Configuration ===")
    print(f"HOST: {config('DB_HOST', default='NOT SET')}")
    print(f"PORT: {config('DB_PORT', default='5432')}")
    print(f"NAME: {config('DB_NAME', default='NOT SET')}")
    print(f"USER: {config('DB_USER', default='NOT SET')}")
    print(f"PASSWORD: {'***' if config('DB_PASSWORD', default='') else 'NOT SET'}")
    print("=========================================\n")


if __name__ == '__main__':
    import django
    import os
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_project.settings')
    django.setup()
    
    print("\n🔍 Running Database Health Check...\n")
    print_connection_info()
    result = check_database_health(verbose=True)
    
    if result['errors']:
        print("\nErrors found:")
        for error in result['errors']:
            print(f"  - {error}")
    
    sys.exit(0 if result['status'] == 'healthy' else 1)
