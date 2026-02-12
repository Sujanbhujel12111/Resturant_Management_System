# Database Connection Troubleshooting Guide

This guide helps diagnose and resolve database connectivity issues in the Restaurant Management System.

## Quick Diagnosis

### 1. Check Environment Variables on Render

Go to your Render service dashboard and verify these variables are set in the **Environment** tab:

```
DB_HOST=db.itoixuthobevjbqid.pooler.supabase.co
DB_NAME=postgres
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password_here
```

**Important:** 
- Use the **pooler endpoint** (contains `pooler.supabase.co`) for connection pooling
- Do NOT use the direct connection endpoint
- Password must match your Supabase database password exactly

### 2. Run Health Check Locally

```bash
# Configure your local .env file first with valid Supabase credentials
python manage.py db_health_check --verbose
```

Expected output:
```
✓ Environment variables are set
✓ Database connection successful
✓ Database has X tables
✓ Database health check PASSED
```

### 3. Check Supabase Status

1. Visit https://status.supabase.com
2. Verify your region's database is operational (green status)
3. Log in to your Supabase project at https://supabase.com/dashboard
4. Check if your project is active and not suspended

## Common Issues and Solutions

### Issue: "could not translate host name" or "Name or service not known"

**Cause:** DNS cannot resolve the database hostname

**Solutions:**
1. **Verify Supabase is running**
   - Check Supabase dashboard for any service alerts
   - Verify your project tier hasn't hit usage limits

2. **Check Render environment variables**
   - Render must have ALL database environment variables set
   - After adding/updating env vars, Render needs a new deploy
   - Trigger a manual redeploy:
     - Go to Render dashboard
     - Select your service
     - Click "Manual Deploy" > "Deploy latest commit"

3. **Try the direct connection (fallback)**
   - If pooler endpoint fails consistently, get the direct connection endpoint from Supabase
   - Direct endpoint format: `db.abc123.supabase.co` (no "pooler")
   - Update `DB_HOST` environment variable and redeploy

### Issue: "Connection refused"

**Cause:** Can reach the host but database isn't accepting connections

**Solutions:**
1. Verify DB_USER and DB_PASSWORD are correct
2. Check if Supabase project hit usage limits (free tier limits)
3. Verify Postgres version compatibility (Supabase uses PostgreSQL 14+)

### Issue: "server closed the connection unexpectedly"

**Cause:** Connection drop/timeout or SSL issues

**Solutions:**
1. Database configuration now includes:
   - Connection timeout: 10 seconds
   - SSL requirement for Supabase connections
   - TCP keepalive settings
   - Statement timeout: 30 seconds

2. Check Supabase logs for connection drops
3. Consider reducing `CONN_MAX_AGE` if connections are idle too long

### Issue: "relation does not exist" errors

**Cause:** Database tables haven't been created/migrated

**Solutions:**
```bash
# On Render, SSH into the service and run:
python manage.py migrate

# Or in Procfile release step - already configured:
# release: python manage.py migrate
```

## Environment Variable Setup Guide

### For Render.com Deployment

1. Create a PostgreSQL database on Supabase (or use existing)
2. In Supabase dashboard:
   - Go to Project Settings > Database
   - Find "Connection string" section
   - Copy the **Pooling** connection string (contains `pooler`)
   - Extract these details:
     ```
     postgresql://user:password@host:port/database
     ```

3. In Render dashboard for your service:
   - Go to **Environment** tab
   - Add these variables:
     - `DB_HOST`: The hostname from connection string
     - `DB_PORT`: The port (usually 5432)
     - `DB_NAME`: Database name (usually "postgres")
     - `DB_USER`: Username
     - `DB_PASSWORD`: Password
   - Do NOT include quotes around values

4. Click "Save Changes"
5. Trigger a new deploy - Render will restart with new variables

### For Local Development

1. Create `.env` file in project root:
```
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=127.0.0.1,localhost

# Database - local or remote Supabase
DB_HOST=db.itoixuthobevjbqid.pooler.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_password

# For local PostgreSQL instead:
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=restaurant_db
# DB_USER=postgres
# DB_PASSWORD=local_password
```

2. Install python-decouple if not already installed:
```bash
pip install python-decouple
```

## Advanced Debugging

### View Detailed Logs

1. **Local development:**
   ```bash
   tail -f logs/django.log
   ```

2. **On Render:**
   - Go to service dashboard
   - Click "Logs" tab to view real-time logs
   - Filter by "psycopg2" or "database" to see connection errors

### Test Connection with psycopg2 Directly

```bash
python -c "
import psycopg2
import sys
try:
    conn = psycopg2.connect(
        host='db.itoixuthobevjbqid.pooler.supabase.co',
        port=5432,
        database='postgres',
        user='postgres',
        password='your_password',
        connect_timeout=10,
        sslmode='require'
    )
    print('✓ Connection successful!')
    with conn.cursor() as cursor:
        cursor.execute('SELECT version()')
        print(cursor.fetchone()[0])
    conn.close()
except Exception as e:
    print(f'✗ Connection failed: {e}')
    sys.exit(1)
"
```

### Django Debug Toolbar for Connection Analysis

Already configured in settings.py - check `logs/django.log` for SQL queries and connection stats.

## Connection Pool Configuration

Current settings optimize for Render's constraints:

```python
DATABASES = {
    'default': {
        'CONN_MAX_AGE': 600,  # Close idle connections after 10 min
        'OPTIONS': {
            'connect_timeout': 10,  # 10 sec timeout
            'sslmode': 'require',   # SSL for Supabase
            'statement_timeout': 30000,  # 30 sec query timeout
            'tcp_keepalives': 1,
            # ... keepalive settings for stability
        }
    }
}
```

**Adjust if needed:**
- Increase `CONN_MAX_AGE` if you have many active users
- Increase `connect_timeout` if network is slow
- Increase `statement_timeout` for long-running queries

## Getting Help

1. **Check logs:**
   - Local: `logs/django.log`
   - Render: Service logs tab

2. **Run diagnostics:**
   ```bash
   python manage.py db_health_check --verbose
   ```

3. **Common next steps:**
   - Redeploy on Render (may pick up new env vars)
   - Restart Supabase project (dashboard > Pause > Resume)
   - Contact Supabase support if database is down

4. **Supabase documentation:**
   - https://supabase.com/docs/guides/database/connecting-with-pooling
   - https://supabase.com/docs/reference/python/introduction

## Related Files

- Database settings: `restaurant_project/settings/base.py`
- Connection health check: `restaurant_project/health_check.py`
- Management command: `restaurant/management/commands/db_health_check.py`
- Error handling middleware: `restaurant/middleware.py` (DatabaseHealthMiddleware)
- WSGI application: `restaurant_project/wsgi.py`
