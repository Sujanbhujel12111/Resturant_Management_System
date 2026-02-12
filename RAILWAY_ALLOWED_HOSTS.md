# Railway Deployment - ALLOWED_HOSTS Fix

Your app is running on Railway but failing with `DisallowedHost` error because the domain isn't in `ALLOWED_HOSTS`.

## Quick Fix

1. **Get your Railway domain:**
   - Check the logs or Railway dashboard
   - Your domain is: `web-production-2e74e.up.railway.app` (from the error message)

2. **Add it to ALLOWED_HOSTS in Railway:**
   - Go to https://railway.app/dashboard
   - Select your project
   - Go to **Variables** tab
   - Find or create the variable: `ALLOWED_HOSTS`
   - Set its value to:
     ```
     localhost,127.0.0.1,web-production-2e74e.up.railway.app
     ```
   - (Replace `web-production-2e74e.up.railway.app` with YOUR actual domain from logs)

3. **Deploy:**
   - Click **Deploy** button in Railway
   - Wait 2-3 minutes
   - Try accessing your app again

## Why This Happens

Django's `ALLOWED_HOSTS` setting is a security feature that prevents Host header attacks. Every domain accessing your app must be explicitly listed.

Railway assigns domains dynamically like `web-production-XXXX.up.railway.app` where XXXX changes. The app now auto-detects Railway domains, but you may still need to explicitly set it.

## Environment Variables to Set in Railway

| Variable | Value | Example |
|----------|-------|---------|
| `DEBUG` | `False` | (production mode) |
| `SECRET_KEY` | Your secret key | `django-insecure-...` |
| `ALLOWED_HOSTS` | Your domains | `localhost,127.0.0.1,web-production-2e74e.up.railway.app` |
| `DB_HOST` | Supabase host | `db.*.pooler.supabase.co` |
| `DB_PORT` | `5432` | (default) |
| `DB_NAME` | `postgres` | (default) |
| `DB_USER` | `postgres` | (default) |
| `DB_PASSWORD` | Your password | Your Supabase password |

## Auto-Detection (What the App Does)

The updated settings now:
- ✅ Auto-detects Railway environment
- ✅ Adds system hostname to ALLOWED_HOSTS 
- ✅ Supports RAILWAY_PUBLIC_DOMAIN environment variable
- ✅ Supports custom domains via CUSTOM_DOMAIN variable

But if Railway doesn't set these automatically, you need to explicitly set `ALLOWED_HOSTS`.

## Testing Locally

```bash
# Simulating Railway environment
export RAILWAY=true
export ALLOWED_HOSTS="localhost,127.0.0.1"
python manage.py runserver
```

## Next Steps

1. **In Railway Dashboard:**
   - Set `ALLOWED_HOSTS` variable with your domain
   - Click Deploy

2. **After deployment:**
   ```bash
   # Test your domain
   curl -H "Host: web-production-2e74e.up.railway.app" http://localhost:8080/
   # Or visit in browser
   https://web-production-2e74e.up.railway.app/
   ```

3. **If still getting errors:**
   - Check Railway logs for the actual domain
   - Verify ALLOWED_HOSTS in Railway includes that domain
   - Check that changes were deployed (sometimes need manual redeploy)

## Custom Domain

If using a custom domain:
1. Set in Railway: `CUSTOM_DOMAIN=yourdomain.com`
2. Or set `ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com`

The app will automatically add custom domains to ALLOWED_HOSTS.
