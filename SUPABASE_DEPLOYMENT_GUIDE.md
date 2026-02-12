# Supabase Deployment Guide

## ⚠️ Local DNS Issue

Your local network (ISP in Nepal) is **blocking DNS resolution** for Supabase hostnames (`db.dnpwuprtcnbqxhwtmjvr.supabase.co`). This is a network/firewall issue, **not a code problem**.

**Workaround for local development:**
- Use **SQLite** locally (already working)
- Deploy to **Railway or Render** where DNS will resolve and work correctly

---

## Correct Supabase Credentials

From your Supabase dashboard:

```
Host:     db.dnpwuprtcnbqxhwtmjvr.supabase.co
Port:     5432
Database: postgres
User:     postgres
Password: Sujan@9810195387
```

**Note:** Your project ID is `dnpwuprtcnbqxhwtmjvr`, not `itoixuthobevjbpgbqid` (the one you were using before).

---

## Step 1: Local Development (SQLite)

Keep using SQLite locally since DNS is blocked:

```powershell
$env:USE_SUPABASE="False"
python manage.py runserver
```

---

## Step 2: Deploy to Railway or Render

### Option A: Railway Deployment

**Railway will have working DNS for Supabase.**

1. Connect your GitHub repo to Railway
2. Right-click project → Create → PostgreSQL (optional, or use Supabase)
3. Set environment variables in Railway:
   ```
   USE_SUPABASE=True
   DB_HOST=db.dnpwuprtcnbqxhwtmjvr.supabase.co
   DB_PORT=5432
   DB_NAME=postgres
   DB_USER=postgres
   DB_PASSWORD=Sujan@9810195387
   SECRET_KEY=<your-secret-key>
   DEBUG=False
   ALLOWED_HOSTS=<your-railway-domain>
   ```
4. Deploy → Railway will auto-run migrations

### Option B: Render Deployment

1. Connect GitHub repo to Render
2. Create new Web Service
3. Set environment variables (as above)
4. In build command, add:
   ```
   python manage.py migrate && python manage.py collectstatic --noinput
   ```
5. Deploy

---

## Step 3: Test on Deployed Host

Once deployed, the DNS will resolve and migrations will succeed automatically.

---

## How to Fix Local DNS (Optional)

If you want to test Supabase locally, try:

- **VPN**: Connect to a VPN (NordVPN, ExpressVPN, etc.) → DNS will work
- **Mobile hotspot**: Use your phone's mobile network instead of WiFi
- **Different ISP**: Try from a café or office network

Then run:
```powershell
$env:USE_SUPABASE="True"
$env:DB_HOST="db.dnpwuprtcnbqxhwtmjvr.supabase.co"
$env:DB_PORT="5432"
$env:DB_NAME="postgres"
$env:DB_USER="postgres"
$env:DB_PASSWORD="Sujan@9810195387"
python manage.py migrate
```

---

## Project ID Reference

- **Your Supabase Project ID**: `dnpwuprtcnbqxhwtmjvr`
- **Your Region**: Verify in Supabase dashboard (Settings → Project)
- **Connection Pool**: Disabled (using direct connection; pooler can be enabled in Supabase settings if needed)

---

## Next Steps

1. **Local**: Continue using SQLite for development
2. **Deploy**: Push to Railway/Render with the environment variables above
3. **Verify**: Check logs on deployed host for successful DB connection
