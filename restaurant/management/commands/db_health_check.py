"""
Django management command to check database health and connectivity.
Usage: python manage.py db_health_check
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.db.utils import OperationalError
from decouple import config
import sys


class Command(BaseCommand):
    help = 'Check database connectivity and health status'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed connection information',
        )

    def handle(self, *args, **options):
        verbose = options.get('verbose', False)
        
        self.stdout.write(self.style.HTTP_INFO('\n🔍 Running Database Health Check...\n'))
        
        # Check environment variables
        required_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
        missing_vars = [var for var in required_vars if not config(var, default=None)]
        
        if missing_vars:
            self.stdout.write(
                self.style.ERROR(f'❌ Missing environment variables: {", ".join(missing_vars)}')
            )
            raise CommandError('Environment variables not configured properly')
        
        if verbose:
            self.print_config()
        
        self.stdout.write(self.style.SUCCESS('✓ Environment variables are set'))
        
        # Test connection
        try:
            connection = connections['default']
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
            self.stdout.write(self.style.SUCCESS('✓ Database connection successful'))
        except OperationalError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Connection failed: {str(e)}')
            )
            raise CommandError('Database connection failed')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Unexpected error: {str(e)}')
            )
            raise CommandError(f'Unexpected error: {str(e)}')
        
        # Check database tables
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                table_count = cursor.fetchone()[0]
            
            if table_count > 0:
                self.stdout.write(self.style.SUCCESS(f'✓ Database has {table_count} tables'))
            else:
                self.stdout.write(
                    self.style.WARNING('⚠ No tables found - migrations may be needed')
                )
                self.stdout.write(
                    self.style.WARNING('  Run: python manage.py migrate')
                )
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠ Failed to check tables: {str(e)}')
            )
        
        self.stdout.write(self.style.SUCCESS('\n✓ Database health check PASSED\n'))

    def print_config(self):
        """Print database connection configuration (with password masked)"""
        self.stdout.write(self.style.HTTP_INFO('\n=== Database Configuration ==='))
        self.stdout.write(f"HOST: {config('DB_HOST', default='NOT SET')}")
        self.stdout.write(f"PORT: {config('DB_PORT', default='5432')}")
        self.stdout.write(f"NAME: {config('DB_NAME', default='NOT SET')}")
        self.stdout.write(f"USER: {config('DB_USER', default='NOT SET')}")
        self.stdout.write(f"PASSWORD: {'***' if config('DB_PASSWORD', default='') else 'NOT SET'}")
        self.stdout.write(self.style.HTTP_INFO('===============================\n'))
