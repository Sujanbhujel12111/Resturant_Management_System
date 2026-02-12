# Deploy to Railway + Supabase (5 Minutes)

## ⚠️ Local Limitation
Your ISP blocks DNS to Supabase, so you **cannot test locally**. But Railway can connect fine — deploy and it will work.

---

## Step 1: Push Code to GitHub

```powershell
cd C:\Users\ACER\Desktop\Resturant-Management-System-main

# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Restaurant Management System - Ready for deployment"

# Create a GitHub repo at https://github.com/new, then:
git remote add origin https://github.com/YOUR_USERNAME/Resturant-Management-System.git
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy to Railway

### A. Sign up for Railway
1. Go to **https://railway.app**
2. Click **Sign up** → Login with GitHub
3. Authorize Railway to access your repos

### B. Create New Project
1. Click **New Project**
2. Select **Deploy from GitHub**
3. Find and select your **Resturant-Management-System** repo
4. Click **Deploy**

### C. Configure Environment Variables
Railway will auto-detect Python. Now add Supabase variables:

1. In Railway dashboard, go to your project → **Variables** tab
2. Add these variables:

```
USE_SUPABASE=True
DB_HOST=db.dnpwuprtcnbqxhwtmjvr.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=Sujan@9810195387
SECRET_KEY=your-very-secret-random-key-here-use-at-least-50chars
DEBUG=False
ALLOWED_HOSTS=*.railway.app
```

**⚠️ Important:** Generate a new `SECRET_KEY`:
```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Copy the output and paste as `SECRET_KEY` value.

### D. Set Build & Start Commands
1. Go to **Settings** tab in Railway
2. Under **Build Command**, enter:
```
pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
```

3. Under **Start Command**, enter:
```
gunicorn restaurant_project.wsgi:application --bind 0.0.0.0:$PORT
```

### E. Deploy
1. Click **Deploy** button
2. Wait for build to complete (~2-3 minutes)
3. Once done, you'll get a URL like: `https://resturant-xyz.railway.app`

---

## Step 3: Verify Deployment

Once Railway shows "Deployment successful":

1. **Check logs:**
   - In Railway → **Logs** tab
   - Look for: ✅ `System check identified no issues`
   - Look for: ✅ `Migrations applied successfully`

2. **Test the app:**
   - Visit: `https://your-railway-url/` (from Railway dashboard)
   - You should see your Restaurant app homepage

3. **Test admin panel:**
   - Visit: `https://your-railway-url/admin`
   - Create a superuser first:
     - Railway → Logs → scroll up to deployment output
     - OR run locally: `python manage.py createsuperuser` then push to GitHub and redeploy

---

## Step 4: Create Admin User (One-Time)

If you want to test admin panel, create a superuser:

### Option A: Create locally then deploy
```powershell
$env:USE_SUPABASE="False"
python manage.py createsuperuser
# Enter: username, email, password

git add .
git commit -m "Admin user created"
git push
```

Then redeploy on Railway.

### Option B: Create via Railway terminal (if available)
In Railway dashboard, click **Terminal** and run:
```bash
python manage.py createsuperuser
```

---

## Troubleshooting

### "Deployment failed"
- Check **Logs** tab in Railway for error messages
- Common issues:
  - Missing `requirements.txt` → verify in root directory
  - Invalid `SECRET_KEY` → must be at least 50 characters
  - Wrong Supabase credentials → verify `DB_HOST`, `DB_USER`, `DB_PASSWORD`

### "Bad Request (400) - Disallowed Host"
- This means `ALLOWED_HOSTS` is wrong
- In Railway Variables, set:
```
ALLOWED_HOSTS=your-railway-domain.railway.app,.railway.app
```

### "Database connection failed"
- This is expected locally (DNS blocked)
- But should work on Railway (DNS is open)
- Check Railway Logs for the actual error

---

## Your Supabase Connection Details

```
Host:     db.dnpwuprtcnbqxhwtmjvr.supabase.co
Port:     5432
Database: postgres
User:     postgres
Password: Sujan@9810195387
```

---

## Next Steps After Deployment

1. ✅ Verify app loads at Railway URL
2. ✅ Test admin panel (create superuser if needed)
3. ✅ Add restaurant data through admin panel
4. ✅ Test order functionality
5. (Optional) Add custom domain in Railway → Domain settings

---

## Project Ready? 

Your code is configured and ready. Just:
1. Push to GitHub
2. Connect Railway
3. Deploy

**That's it!** 🚀
