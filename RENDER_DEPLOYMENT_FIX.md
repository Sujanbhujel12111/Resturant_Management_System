# Render Deployment Fix Guide

## Quick Diagnosis

Your DNS cannot resolve `db.itoixuthobevjbpgbqid.pooler.supabase.co`. This is happening both locally and on Render.

**Possible causes:**
1. Environment variables not correctly set on Render
2. Supabase database is paused or suspended  
3. Pooler endpoint is having issues - try direct endpoint instead
4. DNS/network connectivity issue

## Immediate Actions

### Step 1: Verify Supabase Project Status

1. Go to https://supabase.com/dashboard
2. Sign in to your account
3. Select your project
4. Check the project status in the top-left corner
   - Should show a green indicator
   - If red/paused: Click **Resume** to restart it
5. Click **Settings** → **Database** 
6. Verify under "Connection string" that you can see both:
   - **Pooling endpoint** (contains `pooler`)
   - **Direct endpoint** (no pooler)

### Step 2: Get the Correct Connection Details

In Supabase dashboard under Settings → Database:

**Find the Pooling Connection String:**
```
postgresql://postgres:[PASSWORD]@db.itoixuthobevjbpgbqid.pooler.supabase.co:5432/postgres
```

Extract:
- `DB_HOST`: `db.itoixuthobevjbpgbqid.pooler.supabase.co`
- `DB_PORT`: `5432`
- `DB_NAME`: `postgres`
- `DB_USER`: `postgres`
- `DB_PASSWORD`: Your password

### Step 3: Update Render Environment Variables

**Important:** After changing env vars, Render requires a redeploy to apply them.

1. Go to https://dashboard.render.com
2. Select your service (`resturant-management-system-sf55`)
3. Click **Environment** tab
4. Verify/update these variables:
   ```
   DB_HOST=db.itoixuthobevjbpgbqid.pooler.supabase.co
   DB_PORT=5432
   DB_NAME=postgres
   DB_USER=postgres
   DB_PASSWORD=your_actual_password_here
   ```
5. Click **Save Changes**
6. Click **Manual Deploy** → **Deploy latest commit**
7. Wait 3-5 minutes for deployment to complete
8. Check the logs tab for errors

### Step 4: If Pooler Still Fails - Try Direct Endpoint

If you keep getting DNS resolution errors after redeploy:

1. In Supabase Settings → Database, copy the **Direct PostgreSQL URL** (not pooler)
   - Should look like: `db.itoixuthobevjbpgbqid.supabase.co`
2. In Render environment variables, change:
   ```
   DB_HOST=db.itoixuthobevjbpgbqid.supabase.co  
   (remove "pooler" from the hostname)
   ```
3. Redeploy on Render

### Step 5: Test Locally

Once environment variables are set in your `.env` file, run:

```bash
python test_db_connection.py
```

This will show exactly what's wrong:
- ✓ DNS resolution works
- ✓ Port is reachable
- ✓ PostgreSQL authenticates
- ✓ Django can connect

## Checklist Before Next Redeploy

- [ ] Supabase project is active (green status)
- [ ] All DB_* environment variables are set in Render
- [ ] Password in Render matches Supabase password exactly
- [ ] `DB_HOST` value is correct (double-check copy/paste)
- [ ] Manual Deploy triggered on Render (not just git push)
- [ ] Waited 3-5 minutes for deployment to complete
- [ ] Checked Render logs for errors

## If Still Failing

1. **Check Render logs:**
   - Go to your service on Render dashboard
   - Click **Logs** tab
   - Look for exact error message

2. **Run diagnostics:**
   ```bash
   python manage.py db_health_check --verbose
   ```

3. **Contact support:**
   - Render: https://render.com/docs/troubleshooting-deploys
   - Supabase: https://supabase.com/docs/reference/python/introduction

## Alternative: Use SQLite for Testing

If Supabase is unavailable, temporarily test with SQLite:

Edit `restaurant_project/settings/base.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
```

Then run locally:
```bash
python manage.py migrate
python manage.py runserver
```

Once you verify the app works with SQLite, restore the PostgreSQL config and fix the Supabase connection.

---

**Summary:** The issue is that DNS cannot resolve the Supabase hostname. This is typically fixed by:
1. Ensuring Supabase project is running
2. Redeploying on Render to pick up environment variables  
3. Using the direct endpoint instead of pooler if pooler fails
