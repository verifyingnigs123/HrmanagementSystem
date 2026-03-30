# Railway Deployment - Step by Step Guide (SQLite Version)

## Complete Setup for Beginners

This guide will help you deploy your HR Management System to Railway using SQLite.

---

## STEP 1: Prepare Your Local Project

### 1a. Check your project structure
Your project folder should look like:
```
c:\Raph Folders\VS File Code\HrmanagementSystem\
├── hrms/                    (main Django folder)
│   ├── manage.py
│   ├── db.sqlite3           (your database)
│   ├── Procfile             (already created)
│   ├── requirements.txt      (already created)
│   ├── hrms/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── employees/
│   ├── templates/
│   └── static/
├── .gitignore               (already created)
├── .env.example             (already created)
└── RAILWAY_DEPLOYMENT.md
```

### 1b. Create a `.env` file locally (never push to GitHub)
Create a new file: `c:\Raph Folders\VS File Code\HrmanagementSystem\hrms\.env`

Add this content:
```
DEBUG=False
DJANGO_SECRET_KEY=your-secret-key-here-use-any-random-string
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## STEP 2: Update Django Settings for Production

### 2a. Open `c:\Raph Folders\VS File Code\HrmanagementSystem\hrms\hrms\settings.py`

Find this section:
```python
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
```

Replace with:
```python
import os
from pathlib import Path

DEBUG = os.environ.get('DEBUG', 'False') == 'True'
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY') or os.environ.get('SECRET_KEY')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')
```

### 2b. Find the DATABASES section and ensure it uses SQLite:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### 2c. Add Static Files Configuration
Add at the bottom of `settings.py`:
```python
# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Allowed hosts for production
CSRF_TRUSTED_ORIGINS = [
    'https://*.railway.app',
]

# Security settings
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
```

---

## STEP 3: Create GitHub Repository

### 3a. Go to GitHub
1. Open https://github.com/new
2. **Repository name**: `HrmanagementSystem`
3. **Description**: HR Management System with Django
4. Select **Public** (so you can access it free on Railway)
5. Click **Create repository**

### 3b. You'll see commands like:
```
git remote add origin https://github.com/YOUR_USERNAME/HrmanagementSystem.git
```

Copy the URL - you'll need it next.

---

## STEP 4: Initialize Git & Push Code

### 4a. Open PowerShell and navigate to your project:
```powershell
cd "c:\Raph Folders\VS File Code\HrmanagementSystem"
```

### 4b. Initialize Git:
```powershell
git init
```

### 4c. Configure Git (first time only):
```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 4d. Add all files:
```powershell
git add .
```

### 4e. Create first commit:
```powershell
git commit -m "Initial commit - HR Management System with Django"
```

### 4f. Add GitHub as remote (replace YOUR_USERNAME):
```powershell
git remote add origin https://github.com/YOUR_USERNAME/HrmanagementSystem.git
git branch -M main
git push -u origin main
```

**Note**: You'll be asked for your GitHub username and password (or use personal access token)

---

## STEP 5: Deploy to Railway

### 5a. Go to Railway Dashboard
1. Open https://railway.app
2. Sign up with GitHub (one-click login)
3. Click **Dashboard** after login

### 5b. Create New Project
1. Click **New Project**
2. Select **Deploy from GitHub**
3. Click **Authorize Railway** (if asked)
4. Select your `HrmanagementSystem` repository
5. Click **Deploy**

Railway will automatically:
- Detect it's a Django project
- Install dependencies from `requirements.txt`
- Run using `Procfile` configuration

### 5c. Wait for Deployment
- Railway will build your project (takes 2-5 minutes)
- You'll see a green checkmark when done
- Find your URL in the deployment logs

---

## STEP 6: Set Environment Variables

### 6a. Open Railway Dashboard
1. Click on your project
2. Go to **Variables** tab

### 6b. Add these variables:

| Key | Value |
|-----|-------|
| `DEBUG` | `False` |
| `DJANGO_SECRET_KEY` | Copy from `django.core.management.utils.get_random_secret_key()` (see below) |
| `ALLOWED_HOSTS` | Your Railway domain (e.g., `your-app.railway.app`) |

### 6c. Generate Secret Key
Open PowerShell and run:
```powershell
cd "c:\Raph Folders\VS File Code\HrmanagementSystem\hrms"
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and paste in `DJANGO_SECRET_KEY` variable in Railway.

---

## STEP 7: Find Your Deployed App URL

### 7a. In Railway Dashboard:
1. Click your project
2. Look for the **Service** section
3. You'll see a URL like: `https://hrmanagement-prod.railway.app`
4. Click the URL to open your app

### 7b. Test Your App:
- You should see the login page
- Try logging in with:
  - **Username**: `admin`
  - **Password**: `admin123`

---

## STEP 8: Collect Static Files (One-time)

### 8a. Run this command to upload static files:

Option 1 - Using Railway CLI:
```powershell
railway run "python manage.py collectstatic --noinput"
```

Option 2 - Through Railway Dashboard:
1. Go to your project
2. Click **Deployments**
3. Click the latest deployment
4. Look for a terminal/console button
5. Run: `python manage.py collectstatic --noinput`

---

## STEP 9: Verify Everything Works

### Checklist:
- [ ] App opens at your Railway URL
- [ ] Login page loads
- [ ] Can login with `admin / admin123`
- [ ] Dashboard shows (with sidebar)
- [ ] Icons and styling load correctly
- [ ] Can navigate between pages
- [ ] Profile dropdown works
- [ ] Notification bell visible

---

## TROUBLESHOOTING

### Issue: "Application Error" page
**Solution**: Check logs
```powershell
railway logs
```
Look for error messages and fix in `settings.py`

### Issue: 404 Static Files Not Loading
**Solution**: Run collect static
```powershell
railway run "python manage.py collectstatic --noinput"
```

### Issue: Cannot login / 500 error
**Solution**: Check environment variables
1. Verify `DJANGO_SECRET_KEY` is set
2. Verify `DEBUG=False`
3. Restart deployment in Railway

### Issue: "Page not found" on main URL
**Solution**: Check your `hrms/urls.py` has correct routing to home page

---

## UPDATING YOUR APP

After deployment, whenever you make changes:

### 1. Commit changes locally:
```powershell
cd "c:\Raph Folders\VS File Code\HrmanagementSystem"
git add .
git commit -m "Description of changes"
git push origin main
```

### 2. Railway automatically redeploys!
- No manual action needed
- Check deployment status in Railway dashboard
- New version is live when deployment completes

---

## IMPORTANT NOTES

### Database on Railway
- SQLite database (`db.sqlite3`) is stored locally in your Railway app
- Data persists but only within the deployment
- For multi-instance deployments, consider PostgreSQL

### Free Tier Limits
- 5GB storage (includes database + static files)
- $5 free credit per month
- Suitable for testing/development

### Production Tips
1. Change `SECRET_KEY` to a random string
2. Keep `DEBUG = False`
3. Set proper `ALLOWED_HOSTS`
4. Use strong passwords for admin user
5. Regularly check Railway logs

---

## GETTING YOUR RAILWAY DOMAIN

After successful deployment, your app is at:

```
https://your-project-name.railway.app
```

To access admin panel:
```
https://your-project-name.railway.app/admin/
```

---

## QUICK REFERENCE COMMANDS

```powershell
# View logs
railway logs -f

# Get app URL
railway status

# Check variables
railway variables

# Restart app
railway restart

# Open dashboard
railway open

# View deployment info
railway info
```

---

## NEED HELP?

- Railway Docs: https://docs.railway.app
- Check Railway logs: `railway logs -f`
- Restart deployment if stuck

**You're all set! Your HR Management System is now live on Railway! 🚀**
