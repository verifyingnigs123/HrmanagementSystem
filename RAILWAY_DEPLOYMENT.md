# Railway Deployment Guide for HR Management System

## Prerequisites
- GitHub account (to push code)
- Railway account (https://railway.app)
- Git installed on your computer

## Step 1: Initialize Git Repository

```bash
cd c:\Raph Folders\VS File Code\HrmanagementSystem
git init
git add .
git commit -m "Initial commit - HR Management System"
```

## Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Create a new repository (e.g., `HrmanagementSystem`)
3. Copy the repository URL

## Step 3: Push Code to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/HrmanagementSystem.git
git branch -M main
git push -u origin main
```

## Step 4: Deploy to Railway

### Option A: Using Railway CLI (Recommended)

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway:**
   ```bash
   railway login
   ```

3. **Initialize Railway Project:**
   ```bash
   cd c:\Raph Folders\VS File Code\HrmanagementSystem\hrms
   railway init
   ```

4. **Add Environment Variables:**
   ```bash
   railway variables set DJANGO_SECRET_KEY="your-random-secret-key-here"
   railway variables set DEBUG=False
   railway variables set DATABASE_URL="$DATABASE_URL"
   ```

5. **Deploy:**
   ```bash
   railway up
   ```

### Option B: Using Railway Web Dashboard

1. Go to https://railway.app/dashboard
2. Click **"New Project"**
3. Select **"Deploy from GitHub"**
4. Authorize Railway to access your GitHub account
5. Select your `HrmanagementSystem` repository
6. Railway will auto-detect Django

## Step 5: Configure Environment Variables in Railway Dashboard

1. Go to your Railway project
2. Click **"Variables"** tab
3. Add the following variables:

```
DJANGO_SECRET_KEY=your-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-railway-domain.railway.app
DATABASE_URL=<Railway will auto-populate this>
```

**Generate a Secret Key:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Step 6: Add PostgreSQL Database

1. In Railway Dashboard, click **"+ New"**
2. Select **"PostgreSQL"**
3. Railway will auto-configure the `DATABASE_URL` environment variable
4. Click the database plugin to get connection details

## Step 7: Run Database Migrations

After deployment, run migrations manually:

1. Find your deployed app URL (e.g., `your-app.railway.app`)
2. Run migrations:
   ```bash
   railway run "python manage.py migrate"
   ```

Or create a superuser:
   ```bash
   railway run "python manage.py createsuperuser"
   ```

## Step 8: Update Django Settings

Your `settings.py` needs to handle Railway environment variables:

```python
import os
from pathlib import Path

# ... existing settings ...

# Database
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}

# Security settings for production
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Trusted hosts
CSRF_TRUSTED_ORIGINS = [
    f"https://{host}" for host in ALLOWED_HOSTS if host != 'localhost'
]
```

## Step 9: Access Your Application

Your application will be available at:
```
https://your-railroad-app-name.railway.app
```

Login with your demo credentials:
- Username: `admin`
- Password: `admin123`

## Troubleshooting

### 1. **500 Error on First Load**
- Check Railway logs: `railway logs`
- Run migrations: `railway run "python manage.py migrate"`

### 2. **Static Files Not Loading**
```bash
railway run "python manage.py collectstatic --noinput"
```

### 3. **Database Connection Error**
- Verify PostgreSQL is added to your Railway project
- Check environment variables are correctly set
- Restart the deployment

### 4. **ALLOWED_HOSTS Error**
Update the environment variable:
```
ALLOWED_HOSTS=your-app.railway.app
```

### 5. **View Logs**
```bash
railway logs -f
```

## Updating Your Application

1. Make changes locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Your message"
   git push origin main
   ```
3. Railway automatically redeploys on push

## Useful Railway Commands

```bash
# View logs
railway logs -f

# Set environment variables
railway variables set KEY=value

# View variables
railway variables

# Run Django management commands
railway run "python manage.py migrate"
railway run "python manage.py createsuperuser"

# Open Railway dashboard
railway open

# View deployed URL
railway status
```

## File Structure Required

```
HrmanagementSystem/
├── hrms/                    # Django project folder
│   ├── manage.py
│   ├── Procfile            # ← Railway will look for this
│   ├── requirements.txt     # ← Must include gunicorn
│   ├── hrms/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── employees/
│   ├── templates/
│   └── static/
├── .git/
├── .gitignore
└── README.md
```

## Next Steps After Deployment

1. Create a superuser for admin access
2. Populate demo data
3. Set up email configuration
4. Configure custom domain (optional)
5. Set up backup strategies

Good luck! 🚀
