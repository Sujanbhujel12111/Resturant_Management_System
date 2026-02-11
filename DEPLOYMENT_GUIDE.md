# Deployment Guide - Render.com with Supabase

This guide will help you deploy your Django Restaurant Management System to Render.com with your domain `sujanbhujel01.com.np`.

## Prerequisites

- GitHub account with your code pushed
- Supabase account with PostgreSQL database configured
- Render.com account
- Domain registered at your registrar

## Step 1: Push Code to GitHub

If not already done:

```bash
git add .
git commit -m "Setup for production deployment"
git push origin master
```

## Step 2: Create Render App

1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select the repository
5. Fill in the details:
   - **Name**: `restaurant-management`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Start Command**: `gunicorn restaurant_project.wsgi:application`

## Step 3: Set Environment Variables

In Render dashboard, go to **Environment** → Add these variables:

```
DEBUG=False
SECRET_KEY=your-random-secret-key-here
ALLOWED_HOSTS=sujanbhujel01.com.np,www.sujanbhujel01.com.np,your-render-url.onrender.com
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-supabase-password
DB_HOST=your-supabase-project.supabase.co
DB_PORT=5432
```

**Important**: Get your Supabase credentials from Supabase Dashboard → Settings → Database

## Step 4: Connect Your Domain

1. In Render dashboard, go to **Settings** → **Custom Domains**
2. Add your domain: `sujanbhujel01.com.np`
3. Render will give you DNS records to add

## Step 5: Update Domain DNS Records

1. Go to your domain registrar (where you registered sujanbhujel01.com.np)
2. Find **DNS Settings** or **Nameservers**
3. Add the DNS records Render provided
4. Wait 24-48 hours for DNS propagation

## Step 6: Test Deployment

Once deployed, access:
- `https://sujanbhujel01.com.np`
- Check Render logs for any errors

## Troubleshooting

### Error: "command not found"
- Make sure Procfile and build.sh exist
- Check requirement.txt is properly formatted

### Database connection error
- Verify all DB_* environment variables are correct
- Test Supabase connection locally: `python test_connection.py`

### Static files not loading
- WhiteNoise middleware handles this automatically
- Check `collectstatic` runs without errors

### Domain not resolving
- DNS changes take 24-48 hours
- Wait or contact your registrar

## Further Help

- Render docs: https://render.com/docs
- Django deployment: https://docs.djangoproject.com/en/4.0/howto/deployment/
- Contact support if needed

