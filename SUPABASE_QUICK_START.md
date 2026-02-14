# Quick Start: Migration from SQLite to Supabase

Follow these 5 steps to move your local database to Supabase.

---

## STEP 1: Create Supabase Project (2 minutes)

Go to: https://supabase.com/dashboard

1. Click **"New project"**
2. Enter project name: `Restaurant-Management`
3. Create a strong password (save it!)
4. Click **"Create new project"**

Wait for initialization...

---

## STEP 2: Get Your Credentials (1 minute)

In Supabase dashboard:

1. Click **"Settings"** (bottom left)
2. Click **"Database"** tab
3. Look for **Connection string** section and find PostgreSQL one

This is your connection string:
```
postgresql://postgres:PASSWORD@db.PROJECT_ID.supabase.co:5432/postgres
```

Extract these values:
- **DB_HOST** = `db.PROJECT_ID.supabase.co`
- **DB_USER** = `postgres`
- **DB_PASSWORD** = The password you created
- **DB_NAME** = `postgres`
- **DB_PORT** = `5432`

---

## STEP 3: Update .env File (1 minute)

Open `.env` in project root and add/update:

```env
DB_HOST=db.[your-project-id].supabase.co
DB_USER=postgres
DB_PASSWORD=[your-password]
DB_NAME=postgres
DB_PORT=5432
USE_SUPABASE=True
```

Save the file.

---

## STEP 4: Test Connection (2 minutes)

In terminal, run:

```bash
python migrate_sqlite_to_supabase.py --test-only
```

**Expected output:**
```
✓ Testing Supabase connection...
✓ Successfully connected to Supabase!
```

If you see an error:
- Check `.env` credentials
- Verify no extra spaces or typos
- Wait 1-2 minutes if project was just created

---

## STEP 5: Migrate Your Data (5 minutes)

**First, backup your data:**
```bash
python migrate_sqlite_to_supabase.py --backup
```

**Then run the migration:**
```bash
python migrate_sqlite_to_supabase.py
```

Watch for:
```
✓ MIGRATION COMPLETED SUCCESSFULLY!
```

---

## Done! ✓

Your database is now on Supabase!

### Verify it worked:

**In terminal:**
```bash
python manage.py shell
from restaurant.models import Order
Order.objects.count()  # Should show your orders
```

**Or in Supabase dashboard:**
1. Go to SQL Editor
2. Run: `SELECT COUNT(*) FROM restaurant_order;`
3. Should show your order count

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Connection refused | Check `.env` credentials, wait 2 min if fresh project |
| Password auth failed | Verify password in `.env` matches Supabase password |
| psycopg2 not found | `pip install psycopg2-binary` |
| No data transferred | Run `python migrate_sqlite_to_supabase.py --verify-only` to check |

---

## Next: Deploy to Production

Once tested locally:

1. Add same `.env` variables to your hosting platform (Railway, Render, Heroku)
2. Deploy your application
3. Your app will automatically use Supabase in production!

---

## Rollback if Needed

If something goes wrong:

```bash
# Use your backup (if you created one with --backup)
python migrate_sqlite_to_supabase.py --restore-backup

# Or just switch back to SQLite in .env:
# Set: USE_SUPABASE=False
```

Your local `db.sqlite3` is never touched!

---

**Need help?** See detailed guides:
- `SUPABASE_SETUP_GUIDE.md` - Detailed setup instructions
- `SUPABASE_MIGRATION_GUIDE.md` - Complete migration guide
