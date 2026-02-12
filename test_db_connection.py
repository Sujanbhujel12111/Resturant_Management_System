#!/usr/bin/env python
"""
Standalone database connection tester.
Run: python test_db_connection.py
"""

import sys
import os
from decouple import config

print("\n" + "="*60)
print("DATABASE CONNECTION TEST")
print("="*60 + "\n")

# Get environment variables
db_host = config('DB_HOST', default='')
db_port = config('DB_PORT', default='5432', cast=int)
db_name = config('DB_NAME', default='postgres')
db_user = config('DB_USER', default='postgres')
db_password = config('DB_PASSWORD', default='')

print("Configuration:")
print(f"  HOST:     {db_host}")
print(f"  PORT:     {db_port}")
print(f"  DATABASE: {db_name}")
print(f"  USER:     {db_user}")
print(f"  PASSWORD: {'***' if db_password else 'NOT SET'}")

if not db_host:
    print("\n❌ ERROR: DB_HOST is not set!")
    sys.exit(1)

if not db_password:
    print("\n❌ ERROR: DB_PASSWORD is not set!")
    sys.exit(1)

print("\n" + "-"*60)
print("Testing Connection...")
print("-"*60 + "\n")

# Test 1: DNS Resolution
print("1. Testing DNS resolution...")
import socket
try:
    ip = socket.gethostbyname(db_host)
    print(f"   ✓ Resolved {db_host} → {ip}")
except socket.gaierror as e:
    print(f"   ❌ DNS resolution failed: {e}")
    print("\n   Troubleshooting:")
    print("   - Verify DB_HOST is correct in Render environment variables")
    print("   - Check if Supabase database is running")
    print("   - Try the direct endpoint instead of pooler:")
    print("     - Pooler: db.*.pooler.supabase.co")
    print("     - Direct: db.*.supabase.co")
    sys.exit(1)

# Test 2: Port connectivity
print("\n2. Testing port connectivity...")
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)
try:
    result = sock.connect_ex((db_host, db_port))
    if result == 0:
        print(f"   ✓ Port {db_port} is open")
    else:
        print(f"   ❌ Port {db_port} is closed or unreachable")
        sys.exit(1)
finally:
    sock.close()

# Test 3: PostgreSQL connection
print("\n3. Testing PostgreSQL connection...")
try:
    import psycopg2
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password,
        connect_timeout=10,
        sslmode='require' if 'supabase' in db_host else 'disable'
    )
    print("   ✓ PostgreSQL connection successful")
    
    # Get version
    with conn.cursor() as cursor:
        cursor.execute('SELECT version()')
        version = cursor.fetchone()[0]
        print(f"   ✓ Server: {version.split(',')[0]}")
    
    conn.close()
    
except psycopg2.OperationalError as e:
    print(f"   ❌ Connection failed: {e}")
    print("\n   Troubleshooting:")
    if "could not translate host name" in str(e):
        print("   - DNS cannot resolve the hostname")
        print("   - Check if Supabase project is active")
        print("   - Try restarting your Supabase project")
    elif "password authentication failed" in str(e):
        print("   - Invalid password")
        print("   - Verify DB_PASSWORD matches your Supabase password")
    elif "connection refused" in str(e):
        print("   - Cannot connect to the port")
        print("   - Check if Supabase is running")
        print("   - Try using the direct endpoint instead of pooler")
    sys.exit(1)

except Exception as e:
    print(f"   ❌ Unexpected error: {e}")
    sys.exit(1)

# Test 4: Django connection
print("\n4. Testing Django connection...")
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_project.settings')
    import django
    django.setup()
    
    from django.db import connections
    with connections['default'].cursor() as cursor:
        cursor.execute('SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = %s', ['public'])
        table_count = cursor.fetchone()[0]
    
    print(f"   ✓ Django connection successful")
    print(f"   ✓ Database has {table_count} tables")
    
except Exception as e:
    print(f"   ❌ Django connection failed: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("✓ ALL TESTS PASSED")
print("="*60 + "\n")
print("Your database connection is working correctly!")
print("If login still fails on Render, the issue is elsewhere.")
