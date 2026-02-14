# Supabase Setup and Configuration Guide

This document provides step-by-step instructions to set up Supabase and configure your Django application to use it.

## Complete Setup Process

### Step 1: Create a Supabase Account and Project

1. **Go to Supabase**: https://supabase.com
2. **Click "Sign Up"** and create an account (or login if you have one)
3. **Create a new organization** (if prompted)
4. **Create a new project**:
   - Click "New project"
   - **Project name**: Enter something like "Restaurant-Management" or "Restaurant-DB"
   - **Database password**: Create a STRONG password (15+ characters, mix of upper/lower/numbers/symbols)
     - Example: `P@ssw0rd2026!Secure`
     - Keep this password safe! You'll need it for your `.env` file
   - **Organization**: Select your organization
   - **Region**: Choose the region closest to your users (e.g., USA, Europe, Asia)
   - Click **"Create new project"**

5. **Wait for initialization** (usually takes 1-2 minutes)
   - You'll see a loading screen
   - Once complete, you'll have access to your project dashboard

### Step 2: Get Your Database Credentials

Once your Supabase project is created:

#### Method A: From the Dashboard (Recommended)

1. Go to your project dashboard
2. Click **"Settings"** (bottom left) → **"Database"**
3. Scroll down to **"Connection string"**
4. You'll see different connection strings. Look for **PostgreSQL**:

```
postgresql://postgres:<password>@db.xxxxx.supabase.co:5432/postgres
```

Extract:
- **Host**: `db.xxxxx.supabase.co` (replace xxxxx with your actual project ID)
- **Port**: `5432`
- **Database**: `postgres`
- **User**: `postgres`
- **Password**: The password you set during project creation

#### Method B: From Connection String

If you have the full connection string, it looks like:
```
postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_ID.supabase.co:5432/postgres
```

Breaking it down:
```
postgresql://USERNAME:PASSWORD@HOST:PORT/DATABASE
               ^^^^^^^^  ^^^^^^^^  ^^^^^^^^^^^^  ^^^^  ^^^^^^^^
               postgres  your-pw   db.xxx...       5432  postgres
```

### Step 3: Update Your .env File

1. **Open your `.env` file** in the project root (or create one if it doesn't exist)

2. **Update it with your Supabase credentials**:

```env
# Django Settings
SECRET_KEY=your-existing-secret-key
DEBUG=False
ALLOWED_HOSTS=127.0.0.1,localhost

# Supabase PostgreSQL Database Configuration
DB_HOST=db.xxxxx.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-actual-password-here
USE_SUPABASE=True
```

**Important**: 
- Replace `db.xxxxx.supabase.co` with your actual Supabase host
- Replace `your-actual-password-here` with the password you set during project creation
- Keep this file NEVER commit to Git (it's in .gitignore)

### Step 4: Install Required Python Packages

If you haven't already installed PostgreSQL support for Django:

```bash
pip install psycopg2-binary
```

Or if you use the requirements.txt:
```bash
pip install -r requirements.txt --upgrade
```

### Step 5: Test the Connection (Optional)

Before running the full migration, test your credentials:

```bash
python migrate_sqlite_to_supabase.py --test-only
```

You should see:
```
✓ Testing Supabase connection...
✓ Successfully connected to Supabase!
```

If this fails:
- Double-check your credentials in `.env`
- Verify the host is correct
- Make sure you didn't add extra spaces
- Check that the password doesn't have special characters that need escaping

### Step 6: Create a Backup (Recommended)

Before migrating your data:

```bash
python migrate_sqlite_to_supabase.py --backup
```

This creates a `backups/migration_YYYYMMDD_HHMMSS/` folder with:
- Full copy of your `db.sqlite3`
- JSON export of all your data

### Step 7: Run the Full Migration

```bash
python migrate_sqlite_to_supabase.py
```

This will:
1. ✓ Test Supabase connection
2. ✓ Create all database tables (via Django migrations)
3. ✓ Transfer all your data from SQLite to Supabase
4. ✓ Verify the migration was successful

You should see output like:
```
✓ Successfully connected to Supabase!
✓ Django migrations completed successfully!
✓ Data dumped to migration_dump.json (1.23 MB)
✓ Loading data into Supabase...
✓ Data migration completed successfully!

==================================================
DATA VERIFICATION
==================================================
✓ Django User                   12 records
✓ Staff                          5 records
✓ Category                       8 records
✓ MenuItem                     156 records
✓ Table                         20 records
✓ Order                        234 records
✓ OrderItem                    892 records
✓ Payment                      234 records
✓ OrderHistory                 145 records
✓ OrderHistoryItem             412 records
==================================================
Total records migrated: 1923
==================================================

✓ MIGRATION COMPLETED SUCCESSFULLY!
```

### Step 8: Verify in Supabase Console

1. Go to your Supabase project dashboard
2. Click **"SQL Editor"** (left sidebar)
3. Click **"New query"**
4. Run this to see all tables:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

You should see your restaurant management tables:
```
auth_user
auth_group
restaurant_category
restaurant_menuitem
restaurant_table
restaurant_order
restaurant_orderitem
restaurant_payment
restaurant_orderhistory
restaurant_orderhistoryitem
accounts_user
accounts_staff
accounts_staffpermission
... and more
```

5. Check if data is there:

```sql
SELECT COUNT(*) FROM restaurant_order;
SELECT COUNT(*) FROM restaurant_menuitem;
SELECT COUNT(*) FROM accounts_staff;
```

## Testing Your Application

After migration:

### Local Testing

```bash
# Ensure USE_SUPABASE=True in your .env
python manage.py runserver
```

Test these features:
- [ ] Login to the application
- [ ] Create a new order
- [ ] View existing orders
- [ ] Check menu items
- [ ] Manage tables
- [ ] View order history

### Django Shell Testing

```bash
python manage.py shell

# Check record counts
from django.contrib.auth.models import User
from restaurant.models import Order, MenuItem

User.objects.count()      # Should show your users
Order.objects.count()     # Should show your orders
MenuItem.objects.count()  # Should show your menu items
```

## Switching Between SQLite and Supabase

### Use Supabase (Production)
```env
USE_SUPABASE=True
DB_HOST=db.xxxxx.supabase.co
DB_USER=postgres
DB_PASSWORD=your-password
```

### Use Local SQLite (Development)
```env
USE_SUPABASE=False
# Comment out or remove DB_HOST line
```

Or simply don't set these variables - SQLite is the default.

## Troubleshooting

### "psycopg2" module not found
```bash
pip install psycopg2-binary
```

### Connection refused / timeout
- Verify `DB_HOST` is correct (should be `db.xxxxx.supabase.co`, not `localhost`)
- Check internet connection
- Verify password is correct
- Wait a few minutes if project was just created

### "FATAL: password authentication failed"
- Check password in `.env` file - make sure it's exact match
- Re-check the password from Supabase dashboard
- If lost, you can reset it in Supabase settings

### SSL CERTIFICATE_VERIFY_FAILED
- This is already handled in the Django settings (`sslmode='require'`)
- Update psycopg2: `pip install --upgrade psycopg2-binary`

### Data didn't transfer
- Check the migration log: `cat supabase_migration.log`
- Verify data count: `python migrate_sqlite_to_supabase.py --verify-only`
- Check if `db.sqlite3` exists and has data

### "relation 'table_name' does not exist"
- The migrations didn't run properly
- Run manually: `python manage.py migrate --database=default`
- Or run migration script with `--force`

## Security Recommendations

1. **Secure your password**:
   - Don't share your `.env` file
   - Ensure `.env` is in `.gitignore`
   - Use strong passwords (15+ characters)

2. **Rotate passwords periodically**:
   - Go to Supabase → Settings → Database → Reset password

3. **Use environment variables in production**:
   - Never hardcode credentials
   - Railway, Render, Heroku support environment variables
   - Set them in the dashboard, not in committed files

4. **Enable Supabase Row Level Security (RLS)**:
   - Optional but recommended for multi-tenant apps
   - Supabase dashboard → SQL Editor

5. **Backup regularly**:
   - Supabase provides automated backups (paid plans)
   - Export your database periodically
   - Use the `--backup` flag when migrating

## Next Steps

1. ✓ Deploy to a hosting platform (Railway, Render, Heroku)
2. ✓ Set environment variables on the hosting platform
3. ✓ Test the application on production
4. ✓ Monitor database performance via Supabase dashboard
5. ✓ Set up database backups

## Additional Resources

- **Supabase Docs**: https://supabase.com/docs
- **PostgreSQL vs SQLite**: https://supabase.com/docs/guides/database
- **Connection Pooling**: https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooler
- **Django + PostgreSQL**: https://docs.djangoproject.com/en/stable/ref/databases/#postgresql-notes
