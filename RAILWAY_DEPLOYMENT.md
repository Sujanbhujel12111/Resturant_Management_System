# Railway Deployment Setup

Your app is now deployed on Railway.app instead of Render. Follow these steps to fix the DisallowedHost error and get your app running.

## Step 1: Fix ALLOWED_HOSTS for Railway

Railway automatically sets the `RAILWAY_PUBLIC_DOMAIN` environment variable. The app now automatically adds this to ALLOWED_HOSTS.

Go to your Railway project and verify the environment variable is being used:

1. Go to https://railway.app/dashboard
2. Select your project
3. Go to **Variables** and check that your domain appears
4. Railway should display your public URL like: `web-production-2e74e.up.railway.app`

## Step 2: Environment Variables for Railway

Set these environment variables in Railway dashboard (**Variables** tab):

```
# Django Settings
DEBUG=False
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,web-production-2e74e.up.railway.app

# Database (Supabase PostgreSQL)
DB_HOST=db.itoixuthobevjbpgbqid.pooler.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_supabase_password_here
```

**Note:** Replace:
- `web-production-2e74e.up.railway.app` with your actual Railway domain
- `your_supabase_password_here` with your actual Supabase password
- `your-super-secret-key-here` with a strong random string

## Step 3: Deploy to Railway

1. Push your code to GitHub:
```bash
git add .
git commit -m "Remove Render-specific code, add Railway support"
git push
```

2. Railway auto-deploys from GitHub, OR manually trigger:
   - Go to Railway dashboard
   - Select your service
   - Click **Deploy** tab
   - Click **Deploy** button

3. Check the build logs to ensure no errors

## Step 4: Test Your App

After deployment completes (2-3 minutes):

```bash
# Test via curl (replace with your Railway domain)
curl https://web-production-2e74e.up.railway.app/

# Or visit in browser
https://web-production-2e74e.up.railway.app/
```

## Environment Variables Reference

| Variable | Required | Example |
|----------|----------|---------|
| `DEBUG` | No | `False` (production) |
| `SECRET_KEY` | Yes | Any random 50+ char string |
| `ALLOWED_HOSTS` | No | Auto-detected, can override |
| `DB_HOST` | Yes | `db.*.pooler.supabase.co` |
| `DB_PORT` | No | `5432` (default) |
| `DB_NAME` | No | `postgres` (default) |
| `DB_USER` | No | `postgres` (default) |
| `DB_PASSWORD` | Yes | Your Supabase password |
| `RAILWAY_PUBLIC_DOMAIN` | Auto | Set by Railway automatically |
| `CUSTOM_DOMAIN` | No | Your custom domain (if using) |

## Railway Features Used

- **Free Tier:** $5/month free credits
- **Auto-deploy:** From GitHub on every push
- **Environment variables:** Managed in dashboard
- **Logs:** Available in Railway dashboard

## Troubleshooting

### Still getting DisallowedHost error?
1. Check that `ALLOWED_HOSTS` is set in Railway
2. Check your actual Railway domain (it's shown in the deployment)
3. Add the domain to ALLOWED_HOSTS environment variable

### Database not connecting?
Run the connection test:
```bash
python test_db_connection.py
```

### Missing environment variables?
Railway might not auto-set `RAILWAY_PUBLIC_DOMAIN`. You can:
1. Manually set `ALLOWED_HOSTS` in Railway environment variables
2. Set `CUSTOM_DOMAIN` if using a custom domain

## Next Steps

1. ✅ Set all environment variables in Railway
2. ✅ Push code to GitHub
3. ✅ Railway auto-deploys
4. ✅ Test the app at your Railway URL

Your app should work on Railway without any Render-specific code now!
