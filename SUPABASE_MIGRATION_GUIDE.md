# SQLite to Supabase Migration Guide

This guide walks you through migrating your local SQLite database to Supabase (PostgreSQL).

## Prerequisites

- Supabase account (free at https://supabase.com)
- Python 3.8+
- All requirements from `requirements.txt` installed
- Your current SQLite database (`db.sqlite3`) with all data intact

## Step 1: Create a Supabase Project

1. Go to https://supabase.com and sign up/login
2. Create a new project:
   - Click "New project"
   - Enter a project name (e.g., "Restaurant-Management")
   - Set a strong database password
   - Select your organization and region
   - Click "Create new project"
3. Wait for the project to initialize (usually 1-2 minutes)

## Step 2: Get Your Supabase Database Credentials

After your project is created:

1. Go to **Settings** → **Database** in your Supabase console
2. Under "Connection string," find:
   - **Host**: `db.xxxxx.supabase.co`
   - **Port**: `5432` (usually)
   - **Database**: `postgres`
   - **User**: `postgres`
   - **Password**: The password you set during project creation

3. Alternatively, copy the PostgreSQL connection string that looks like:
   ```
   postgresql://postgres:<password>@db.xxxxx.supabase.co:5432/postgres
   ```

## Step 3: Update Your .env File

Create or update your `.env` file with your Supabase credentials:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,localhost,127.0.0.1

# Supabase PostgreSQL Database
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-supabase-password-here
DB_HOST=db.xxxxx.supabase.co
DB_PORT=5432
USE_SUPABASE=True
```

## Step 4: Install PostgreSQL Tools (Windows)

You may need PostgreSQL client tools for the migration:

1. Download PostgreSQL from https://www.postgresql.org/download/
2. Run the installer and **UNCHECK** "Install Server" (you only need client tools)
3. Install pgAdmin 4 (optional but helpful for debugging)

Or use Python-only approach (recommended):

```bash
pip install psycopg2-binary
```

## Step 5: Run the Migration Script

Use the provided migration script to transfer all data:

```bash
python migrate_sqlite_to_supabase.py
```

This script will:
- Dump all data from your local SQLite database
- Connect to Supabase PostgreSQL
- Run Django migrations on Supabase
- Transfer all your data
- Verify the migration was successful

### Migration Script Options

**Full migration (all data):**
```bash
python migrate_sqlite_to_supabase.py
```

**Test connection only (no data transfer):**
```bash
python migrate_sqlite_to_supabase.py --test-only
```

**Backup before migrating (recommended):**
```bash
python migrate_sqlite_to_supabase.py --backup
```

**Force migration even if tables exist:**
```bash
python migrate_sqlite_to_supabase.py --force
```

## Step 6: Verify the Migration

### Check Supabase Database

1. Go to Supabase Dashboard → **SQL Editor**
2. Run this query to see all tables:
   ```sql
   SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
   ```

3. Check row counts for key tables:
   ```sql
   SELECT table_name, (SELECT COUNT(*) FROM information_schema.tables t 
           WHERE t.table_schema='public' AND t.table_name=information_schema.tables.table_name) 
   FROM information_schema.tables WHERE table_schema = 'public';
   ```

### Check via Django

```bash
# Activate your Django environment
python manage.py shell

# Count records
from django.contrib.auth.models import User
from restaurant.models import Order, MenuItem, Table
from accounts.models import Staff

print(f"Users: {User.objects.count()}")
print(f"Orders: {Order.objects.count()}")
print(f"MenuItems: {MenuItem.objects.count()}")
print(f"Tables: {Table.objects.count()}")
print(f"Staff: {Staff.objects.count()}")
```

## Step 7: Switch Your Application to Use Supabase

Your application will automatically use Supabase when:
- `USE_SUPABASE=True` is set in your `.env`
- `DB_HOST` is configured with Supabase credentials

For local development, you can use SQLite:
- Set `USE_SUPABASE=False` or leave `DB_HOST` empty
- Or simply not include these in your `.env`

## Troubleshooting

### Connection Refused
- Check that your Supabase project is running
- Verify your credentials are correct
- Make sure your IP is not blocked by Supabase's IP whitelist (if enabled)

### SSL Certificate Errors
- Update `psycopg2`: `pip install --upgrade psycopg2-binary`
- The settings already handle SSL connection (`sslmode=require`)

### Character Encoding Issues
- Ensure UTF-8 encoding: `DATABASES['default']['OPTIONS']['client_encoding'] = 'UTF8'`

### Data Mismatch
- Run the verification script again: `python migrate_sqlite_to_supabase.py --verify-only`
- Check the migration log file: `supabase_migration.log`

### Performance Issues
- Your first load might be slower due to SSL handshake
- Connection pooling is already configured (`CONN_MAX_AGE=600`)
- Use the pooler endpoint for better performance: `db.xxxxx.pooler.supabase.co`

## Rollback Plan

If something goes wrong:

1. **Restore from backup** (if you ran with `--backup`):
   ```bash
   python migrate_sqlite_to_supabase.py --restore-backup
   ```

2. **Revert to SQLite** by updating `.env`:
   ```env
   USE_SUPABASE=False
   # or comment out DB_HOST
   ```

3. Your SQLite database is untouched, so your local data is safe

## Post-Migration Checklist

- [ ] Environment variables updated in `.env`
- [ ] Migration script ran successfully
- [ ] Row counts verified in Supabase
- [ ] Application tested with Supabase database
- [ ] Static files collected: `python manage.py collectstatic --noinput`
- [ ] All features tested (login, orders, menu, etc.)
- [ ] Backups taken (database + media files)

## Deploying to Production

Once tested locally with Supabase:

1. Add your Supabase credentials to your hosting platform's environment variables
2. For Railway: Add variables in Dashboard → Environment
3. For Render: Add variables in Environment
4. For Heroku: `heroku config:set DB_HOST=...`
5. Redeploy your application

## Support Resources

- Supabase Documentation: https://supabase.com/docs
- PostgreSQL vs SQLite Differences: https://supabase.com/docs/guides/database
- Django PostgreSQL Backend: https://docs.djangoproject.com/en/stable/ref/databases/#postgresql-notes
