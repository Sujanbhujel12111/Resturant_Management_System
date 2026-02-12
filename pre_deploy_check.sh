#!/bin/bash
# Pre-deployment database check script
# This helps diagnose connectivity issues before the app starts

echo "==================================="
echo "Pre-Deployment Database Check"
echo "==================================="

# Check environment variables are set
if [ -z "$DB_HOST" ]; then
    echo "❌ ERROR: DB_HOST is not set!"
    exit 1
fi

if [ -z "$DB_PASSWORD" ]; then
    echo "❌ ERROR: DB_PASSWORD is not set!"
    exit 1
fi

echo "✓ Environment variables are set"
echo "  - DB_HOST: $DB_HOST"
echo "  - DB_PORT: ${DB_PORT:-5432}"
echo "  - DB_NAME: ${DB_NAME:-postgres}"
echo "  - DB_USER: ${DB_USER:-postgres}"

# Try to connect using psycopg2
python << 'EOF'
import sys
import os
import psycopg2
from decouple import config

try:
    conn = psycopg2.connect(
        host=config('DB_HOST'),
        port=config('DB_PORT', default=5432, cast=int),
        database=config('DB_NAME', default='postgres'),
        user=config('DB_USER', default='postgres'),
        password=config('DB_PASSWORD'),
        connect_timeout=10,
        sslmode='require'
    )
    with conn.cursor() as cursor:
        cursor.execute('SELECT 1')
    conn.close()
    print("✓ Database connection successful")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo "❌ Database connectivity check failed"
    echo "Proceeding anyway (migrations may help)..."
fi

echo ""
echo "Running migrations..."
python manage.py migrate --noinput

if [ $? -ne 0 ]; then
    echo "⚠️  Migrations had issues, but continuing..."
fi

echo "✓ Pre-deployment check complete"
