# Migrate Your Restaurant Database to Supabase ☁️

This guide helps you move your local SQLite database to Supabase PostgreSQL in **just 5 minutes**.

## What is Supabase?

Supabase is a PostgreSQL database hosting service. Benefits:
- ✓ Your database is secure and always accessible
- ✓ No need to host on your own computer
- ✓ Easy deployment to Railway, Render, Heroku, etc.
- ✓ Free tier available (perfect for testing)

---

## 🚀 Quick Start (5 minutes)

### 1️⃣ Create Supabase Project

1. Go to https://supabase.com
2. Sign up or login
3. Click "New project"
4. Enter name: `Restaurant-Management`
5. Create a **strong password** (save it!)
6. Click "Create new project"
7. ⏳ Wait for it to initialize (1-2 minutes)

### 2️⃣ Get Your Credentials

In Supabase dashboard:
1. Click **Settings** (left menu, bottom)
2. Click **Database** tab
3. Find **Connection string** and copy the PostgreSQL one

It looks like:
```
postgresql://postgres:PASSWORD@db.PROJECT_ID.supabase.co:5432/postgres
```

Write down:
```
Host: db.PROJECT_ID.supabase.co
User: postgres
Password: [your-password]
Database: postgres
Port: 5432
```

### 3️⃣ Set Up Configuration

Run this interactive setup:
```bash
python setup_supabase.py
```

This will ask you for your credentials and save them to `.env`. Much easier than typing!

**Or manually edit `.env`:**
```env
DB_HOST=db.xxxxx.supabase.co
DB_USER=postgres
DB_PASSWORD=your-password
DB_NAME=postgres
DB_PORT=5432
USE_SUPABASE=True
```

### 4️⃣ Test Connection

```bash
python migrate_sqlite_to_supabase.py --test-only
```

Should show:
```
✓ Testing Supabase connection...
✓ Successfully connected to Supabase!
```

### 5️⃣ Migrate Your Data

**First backup** (recommended):
```bash
python migrate_sqlite_to_supabase.py --backup
```

**Then migrate:**
```bash
python migrate_sqlite_to_supabase.py
```

Watch for success message:
```
✓ MIGRATION COMPLETED SUCCESSFULLY!
```

## ✅ Done! Your data is now in Supabase

---

## Verify It Worked

### Option A: Check in Supabase Dashboard
1. Go to Supabase → your project
2. Click **SQL Editor**
3. Run: `SELECT COUNT(*) FROM restaurant_order;`
4. Should show your order count

### Option B: Check in Django
```bash
python manage.py shell
from restaurant.models import Order
Order.objects.count()  # Shows your orders
```

---

## What Gets Migrated?

All your data is transferred:
- ✓ Users and Staff
- ✓ Menu Items and Categories  
- ✓ Orders and Order History
- ✓ Payments
- ✓ Tables
- ✓ Settings and Permissions

No data is lost!

---

## Troubleshooting

### ❌ Connection fails

**Check your credentials:**
```bash
python setup_supabase.py --show
```

Make sure:
- Host is exactly: `db.xxxxx.supabase.co`
- No extra spaces
- Password is exactly right

**Wait for Supabase:**
- If project was just created, wait 1-2 minutes

**Reset password:**
- Go to Supabase → Settings → Database → "Reset database password"

### ❌ "psycopg2 not found"

```bash
pip install psycopg2-binary
```

### ❌ Migration says "tables already exist"

Either:
- Delete tables in Supabase first, or
- Use `--force` flag: `python migrate_sqlite_to_supabase.py --force`

### ❌ Data didn't transfer

Check migration log:
```bash
python migrate_sqlite_to_supabase.py --verify-only
```

Should show all your records.

---

## Common Questions

### Q: Is my data safe?
**A:** Yes! Your original SQLite file is never touched. You can always rollback.

### Q: Will my app work with Supabase?
**A:** Yes, completely. It's just PostgreSQL instead of SQLite.

### Q: How much does it cost?
**A:** Supabase free tier is generous (500MB database). Upgrade anytime.

### Q: Can I still use SQLite locally?
**A:** Yes! Set `USE_SUPABASE=False` to use SQLite for development.

### Q: How do I switch back to SQLite?
**A:** Edit `.env` and set `USE_SUPABASE=False`. That's it.

---

## For Deployment

After testing locally:

### Railway
1. Connect your GitHub repo
2. Add environment variables in Railway dashboard:
   ```
   DB_HOST=db.xxxxx.supabase.co
   DB_USER=postgres
   DB_PASSWORD=your-password
   DB_NAME=postgres
   DB_PORT=5432
   USE_SUPABASE=True
   ```
3. Deploy!

### Render
1. Create new service from repository
2. Add same environment variables
3. Deploy!

### Heroku
```bash
heroku config:set DB_HOST=db.xxxxx.supabase.co
heroku config:set DB_USER=postgres
heroku config:set DB_PASSWORD=your-password
heroku config:set DB_NAME=postgres
heroku config:set DB_PORT=5432
heroku config:set USE_SUPABASE=True
```

---

## Scripts Provided

| Script | Purpose |
|--------|---------|
| `setup_supabase.py` | Interactive setup helper |
| `migrate_sqlite_to_supabase.py` | Main migration tool |
| `SUPABASE_QUICK_START.md` | 5-step quick guide |
| `SUPABASE_SETUP_GUIDE.md` | Detailed setup instructions |
| `SUPABASE_MIGRATION_GUIDE.md` | Complete migration reference |

---

## Need Help?

1. **Setup issues:** Run `python setup_supabase.py --show` to diagnose
2. **Connection issues:** Check `.env` file and Supabase credentials
3. **Migration issues:** Check the log file: `supabase_migration.log`
4. **Still stuck:** Check `SUPABASE_MIGRATION_GUIDE.md` for detailed troubleshooting

---

## One Last Thing

After migration, your `.env` file should look like:

```env
SECRET_KEY=your-key-here
DEBUG=False
ALLOWED_HOSTS=127.0.0.1,localhost

DB_HOST=db.xxxxx.supabase.co
DB_USER=postgres
DB_PASSWORD=Your_Secure_Password_123
DB_NAME=postgres
DB_PORT=5432
USE_SUPABASE=True
```

**NEVER share this file!** Keep it in `.gitignore` (already configured).

---

## Ready? Start Here:

```bash
# Step 1: Interactive setup
python setup_supabase.py

# Step 2: Test connection
python migrate_sqlite_to_supabase.py --test-only

# Step 3: Backup and migrate
python migrate_sqlite_to_supabase.py --backup
python migrate_sqlite_to_supabase.py

# Done! ✓
```

**Questions?** Refer to the detailed guides in the repo.
