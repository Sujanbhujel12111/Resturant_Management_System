import os
import sys

# Ensure project root is on sys.path and Django settings are available
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_project.settings')
import django
django.setup()

from django.db import connection
from django.db.migrations.recorder import MigrationRecorder

def mark_applied(app, name):
    rec = MigrationRecorder(connection)
    rec.ensure_schema()
    # record the migration as applied
    rec.record_applied(app, name)

if __name__ == '__main__':
    try:
        mark_applied('accounts', '0001_initial')
        print('Marked accounts.0001_initial as applied')
    except Exception as e:
        print('Error marking migration applied:', e)
        sys.exit(1)
