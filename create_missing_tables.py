import os
import sys
import sqlite3

# Try to locate sqlite DB via DJANGO_SETTINGS_MODULE if set, otherwise fallback to db.sqlite3
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.sqlite3')
if 'DJANGO_SETTINGS_MODULE' in os.environ:
    try:
        import django
        django.setup()
        from django.conf import settings
        cfg = settings.DATABASES.get('default', {})
        if cfg.get('ENGINE', '').endswith('sqlite3') and cfg.get('NAME'):
            db_path = cfg['NAME']
    except Exception:
        pass

print(f"Using sqlite DB at: {db_path}")
if not os.path.exists(db_path):
    print("Database file not found; nothing to do.")
    sys.exit(0)

conn = sqlite3.connect(db_path)
c = conn.cursor()

tables = {
    'restaurant_orderstatuslog': """
        CREATE TABLE IF NOT EXISTS restaurant_orderstatuslog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            previous_status TEXT,
            new_status TEXT,
            changed_by_id INTEGER,
            timestamp DATETIME
        );
    """,
    'restaurant_orderhistorystatus': """
        CREATE TABLE IF NOT EXISTS restaurant_orderhistorystatus (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_history_id INTEGER,
            previous_status TEXT,
            new_status TEXT,
            changed_by_id INTEGER,
            timestamp DATETIME
        );
    """
}

for name, ddl in tables.items():
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (name,))
    if c.fetchone():
        print(f"Table {name} already exists.")
    else:
        print(f"Creating placeholder table: {name}")
        c.executescript(ddl)
        print(f"Created {name}.")

conn.commit()
conn.close()
print("Done. Now run: python manage.py migrate")
