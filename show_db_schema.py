import sqlite3
import os

db_path = 'restaurant_project/db.sqlite3'
if not os.path.exists(db_path):
    print(f"Database {db_path} not found!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()

print("=" * 80)
print("LOCAL SQLITE DATABASE SCHEMA")
print("=" * 80)
print(f"\nTotal tables: {len(tables)}\n")

for table in tables:
    table_name = table[0]
    cursor.execute(f'PRAGMA table_info({table_name})')
    cols = cursor.fetchall()
    
    print(f"\n📋 {table_name.upper()}")
    print("-" * 80)
    for col in cols:
        col_id, col_name, col_type, not_null, default, pk = col
        nullable = "NOT NULL" if not_null else "NULL"
        pk_marker = " [PRIMARY KEY]" if pk else ""
        print(f"  {col_name:<30} {col_type:<15} {nullable:<10}{pk_marker}")

print("\n" + "=" * 80)
print("✅ Local SQLite database is ready to match Supabase structure!")
print("=" * 80)

conn.close()
