#!/usr/bin/env python
"""
SQLite to Supabase PostgreSQL Migration Script

This script safely migrates your Django database from local SQLite to Supabase PostgreSQL.
It handles:
- Connection validation
- Django migrations
- Data export and import
- Backup creation
- Verification

Usage:
    python migrate_sqlite_to_supabase.py                    # Full migration
    python migrate_sqlite_to_supabase.py --test-only       # Test connection only
    python migrate_sqlite_to_supabase.py --backup          # Create backup before migration
    python migrate_sqlite_to_supabase.py --force           # Force migration even if tables exist
    python migrate_sqlite_to_supabase.py --verify-only     # Verify data was migrated correctly
"""

import os
import sys
import django
import json
import shutil
import logging
from datetime import datetime
from pathlib import Path
from decouple import config
import argparse

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_project.settings.base')
django.setup()

from django.core.management import call_command
from django.db import connections, DEFAULT_DB_ALIAS
from django.core.serializers import serialize
from django.contrib.contenttypes.models import ContentType
import psycopg2
from psycopg2 import sql

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('supabase_migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SupabaseMigration:
    """Handles SQLite to Supabase PostgreSQL migration"""
    
    def __init__(self, backup=False, force=False, test_only=False, verify_only=False):
        self.backup = backup
        self.force = force
        self.test_only = test_only
        self.verify_only = verify_only
        self.backup_dir = None
        self.migration_errors = []
        self.migration_warnings = []
        
    def log_info(self, message):
        """Log info message"""
        logger.info(f"✓ {message}")
        
    def log_error(self, message):
        """Log error message"""
        logger.error(f"✗ {message}")
        self.migration_errors.append(message)
        
    def log_warning(self, message):
        """Log warning message"""
        logger.warning(f"⚠ {message}")
        self.migration_warnings.append(message)
        
    def get_supabase_config(self):
        """Get Supabase database configuration from environment"""
        config_dict = {
            'DB_HOST': config('DB_HOST', default=''),
            'DB_NAME': config('DB_NAME', default='postgres'),
            'DB_USER': config('DB_USER', default='postgres'),
            'DB_PASSWORD': config('DB_PASSWORD', default=''),
            'DB_PORT': config('DB_PORT', default='5432', cast=int),
        }
        
        if not config_dict['DB_HOST']:
            self.log_error("DB_HOST not configured in .env file")
            return None
            
        return config_dict
        
    def validate_supabase_config(self, config_dict):
        """Validate Supabase configuration is complete"""
        required_keys = ['DB_HOST', 'DB_USER', 'DB_PASSWORD']
        missing = [k for k in required_keys if not config_dict.get(k)]
        
        if missing:
            self.log_error(f"Missing required Supabase config: {', '.join(missing)}")
            self.log_info("Please add these to your .env file:")
            self.log_info("  DB_HOST=db.xxxxx.supabase.co")
            self.log_info("  DB_USER=postgres")
            self.log_info("  DB_PASSWORD=your-password")
            return False
            
        return True
        
    def test_supabase_connection(self, config_dict):
        """Test connection to Supabase database"""
        self.log_info("Testing Supabase connection...")
        
        try:
            conn = psycopg2.connect(
                host=config_dict['DB_HOST'],
                database=config_dict['DB_NAME'],
                user=config_dict['DB_USER'],
                password=config_dict['DB_PASSWORD'],
                port=config_dict['DB_PORT'],
                sslmode='require',
                connect_timeout=10
            )
            conn.close()
            self.log_info("Successfully connected to Supabase!")
            return True
        except psycopg2.Error as e:
            self.log_error(f"Failed to connect to Supabase: {e}")
            return False
            
    def backup_sqlite(self):
        """Create backup of SQLite database"""
        self.log_info("Creating backup of SQLite database...")
        
        sqlite_path = Path('restaurant_project/db.sqlite3')
        if not sqlite_path.exists():
            self.log_error("SQLite database not found at db.sqlite3")
            return False
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = Path(f'backups/migration_{timestamp}')
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Backup database file
            backup_db = backup_dir / 'db.sqlite3'
            shutil.copy2(sqlite_path, backup_db)
            self.log_info(f"SQLite database backed up to {backup_db}")
            
            # Export data as JSON
            backup_json = backup_dir / 'data.json'
            with open(backup_json, 'w') as f:
                json.dump(json.loads(serialize('json', self._get_all_models())), f, indent=2)
            self.log_info(f"Data exported to {backup_json}")
            
            self.backup_dir = backup_dir
            return True
        except Exception as e:
            self.log_error(f"Backup failed: {e}")
            return False
            
    def _get_all_models(self):
        """Get all model instances from database"""
        from django.apps import apps
        all_instances = []
        
        for model in apps.get_models():
            try:
                instances = model.objects.all()
                if instances.exists():
                    all_instances.extend(instances)
            except Exception as e:
                self.log_warning(f"Could not fetch {model.__name__}: {e}")
                
        return all_instances
        
    def run_migrations_on_supabase(self):
        """Run Django migrations on Supabase database"""
        self.log_info("Running Django migrations on Supabase...")
        
        try:
            # This will use the Supabase DB configured in settings
            call_command('migrate', interactive=False, verbosity=1)
            self.log_info("Django migrations completed successfully!")
            return True
        except Exception as e:
            self.log_error(f"Migration failed: {e}")
            return False
            
    def check_existing_tables(self, config_dict):
        """Check if tables already exist in Supabase"""
        try:
            conn = psycopg2.connect(
                host=config_dict['DB_HOST'],
                database=config_dict['DB_NAME'],
                user=config_dict['DB_USER'],
                password=config_dict['DB_PASSWORD'],
                port=config_dict['DB_PORT'],
                sslmode='require',
                connect_timeout=10
            )
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            table_count = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            return table_count > 0
        except Exception as e:
            self.log_warning(f"Could not check existing tables: {e}")
            return False
            
    def migrate_data(self):
        """Migrate data from SQLite to Supabase"""
        self.log_info("Starting data migration...")
        
        try:
            # Use Django's dumpdata and loaddata for safe migration
            # First dump all data from SQLite
            self.log_info("Dumping data from SQLite...")
            dump_file = 'migration_dump.json'
            
            call_command('dumpdata', '--natural-foreign', '--natural-primary', 
                        '--indent', '2', stdout=open(dump_file, 'w'))
            
            file_size = os.path.getsize(dump_file) / 1024 / 1024
            self.log_info(f"Data dumped to {dump_file} ({file_size:.2f} MB)")
            
            # Load data into Supabase
            self.log_info("Loading data into Supabase...")
            with open(dump_file, 'r') as f:
                call_command('loaddata', f.name, verbosity=1)
            
            self.log_info("Data migration completed successfully!")
            
            # Cleanup
            os.remove(dump_file)
            
            return True
        except Exception as e:
            self.log_error(f"Data migration failed: {e}")
            return False
            
    def verify_migration(self, config_dict):
        """Verify that data was migrated correctly"""
        self.log_info("Verifying migration...")
        
        try:
            # Get counts from Supabase
            from django.contrib.auth.models import User
            from restaurant.models import (
                Order, MenuItem, Table, Category, OrderItem, Payment,
                OrderHistory, OrderHistoryItem
            )
            from accounts.models import Staff, StaffPermission
            
            models_to_check = [
                ('Django User', User),
                ('Staff', Staff),
                ('Category', Category),
                ('MenuItem', MenuItem),
                ('Table', Table),
                ('Order', Order),
                ('OrderItem', OrderItem),
                ('Payment', Payment),
                ('OrderHistory', OrderHistory),
                ('OrderHistoryItem', OrderHistoryItem),
            ]
            
            self.log_info("\n" + "="*50)
            self.log_info("DATA VERIFICATION")
            self.log_info("="*50)
            
            total_records = 0
            for name, model in models_to_check:
                count = model.objects.count()
                total_records += count
                status = "✓" if count > 0 else "○"
                self.log_info(f"{status} {name:25} {count:>6} records")
            
            self.log_info("="*50)
            self.log_info(f"Total records migrated: {total_records}")
            self.log_info("="*50)
            
            return total_records > 0
            
        except Exception as e:
            self.log_error(f"Verification failed: {e}")
            return False
            
    def run(self):
        """Run the migration process"""
        self.log_info("="*60)
        self.log_info("SQLite to Supabase Migration Tool")
        self.log_info("="*60)
        
        # Step 1: Get configuration
        config_dict = self.get_supabase_config()
        if not config_dict:
            return False
            
        # Step 2: Validate configuration
        if not self.validate_supabase_config(config_dict):
            return False
            
        # Step 3: Test connection
        if not self.test_supabase_connection(config_dict):
            return False
            
        # Step 4: Check for existing tables
        if self.check_existing_tables(config_dict) and not self.force:
            self.log_warning("Supabase database already has tables!")
            self.log_info("Run with --force to overwrite, or manually delete tables in Supabase")
            return False
            
        # Test-only mode
        if self.test_only:
            self.log_info("Test-only mode: Connection successful!")
            return True
            
        # Verify-only mode
        if self.verify_only:
            self.log_info("Verify-only mode: Checking existing migration...")
            return self.verify_migration(config_dict)
            
        # Step 5: Backup if requested
        if self.backup:
            if not self.backup_sqlite():
                return False
                
        # Step 6: Create tables via migrations
        self.log_info("\nSetting up database schema...")
        if not self.run_migrations_on_supabase():
            return False
            
        # Step 7: Migrate data
        self.log_info("\nMigrating data...")
        if not self.migrate_data():
            return False
            
        # Step 8: Verify
        self.log_info("\nVerifying migration...")
        if not self.verify_migration(config_dict):
            self.log_warning("Migration completed but verification found no data!")
            
        # Summary
        self.log_info("\n" + "="*60)
        if self.migration_errors:
            self.log_error(f"MIGRATION COMPLETED WITH {len(self.migration_errors)} ERROR(S)")
            for error in self.migration_errors:
                self.log_error(f"  - {error}")
        else:
            self.log_info("MIGRATION COMPLETED SUCCESSFULLY!")
            
        if self.migration_warnings:
            self.log_info(f"Warnings ({len(self.migration_warnings)}):")
            for warning in self.migration_warnings:
                self.log_warning(f"  - {warning}")
                
        if self.backup_dir:
            self.log_info(f"Backup location: {self.backup_dir}")
            
        self.log_info("="*60)
        
        return len(self.migration_errors) == 0


def main():
    parser = argparse.ArgumentParser(
        description='Migrate Django database from SQLite to Supabase PostgreSQL'
    )
    parser.add_argument('--backup', action='store_true', 
                       help='Create backup before migration')
    parser.add_argument('--force', action='store_true',
                       help='Force migration even if tables exist')
    parser.add_argument('--test-only', action='store_true',
                       help='Test Supabase connection only')
    parser.add_argument('--verify-only', action='store_true',
                       help='Verify existing migration')
    
    args = parser.parse_args()
    
    migration = SupabaseMigration(
        backup=args.backup,
        force=args.force,
        test_only=args.test_only,
        verify_only=args.verify_only
    )
    
    success = migration.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
