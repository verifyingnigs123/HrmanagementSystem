# 🚀 Railway Deployment - QUICK START (10 Minutes)

## Copy & Paste These Commands

### Step 1: Go to Your Project Folder
```powershell
cd "c:\Raph Folders\VS File Code\HrmanagementSystem"
```

### Step 2: Initialize Git
```powershell
git init
git config --global user.name "Your Name"
git config --global user.email "your.email@gmail.com"
git add .
git commit -m "Initial commit"
```

### Step 3: Create GitHub Repo
1. Go to https://github.com/new
2. **Name**: `HrmanagementSystem`
3. Click **Create repository**
4. Copy the URL (looks like: `https://github.com/YOUR_USERNAME/HrmanagementSystem.git`)

### Step 4: Push to GitHub
```powershell
git remote add origin https://github.com/YOUR_USERNAME/HrmanagementSystem.git
git branch -M main
git push -u origin main
```
(Enter your GitHub username and password)

### Step 5: Generate Secret Key
```powershell
cd hrms
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Copy the output (long random string)

### Step 6: Deploy to Railway
1. Go to https://railway.app
2. Sign up with GitHub
3. Click **Dashboard** 
4. Click **New Project**
5. Click **Deploy from GitHub**
6. Select `HrmanagementSystem` repository
7. Click **Create**

**Wait 2-5 minutes for build to complete**

### Step 7: Set Environment Variables
1. In Railway Dashboard, click your project
2. Go to **Variables** tab
3. Add these 3 variables:

| Key | Value |
|-----|-------|
| `DEBUG` | `False` |
| `DJANGO_SECRET_KEY` | Paste the string from Step 5 |
| `ALLOWED_HOSTS` | Will be shown in Railways dashboard (e.g., `your-app-abc123.railway.app`) |

4. Click **Deploy** to restart

### Step 8: Find Your App URL
1. Click **Your Project** → **Deployments**
2. Click the latest deployment
3. Find the **public URL** (e.g., `https://hrmanagement-xyz.railway.app`)
4. Click it to open your app

### Step 9: Test Login
- Username: `admin`
- Password: `admin123`

---

## That's It! 🎉

Your HR Management System is now live online!

**Share your URL**: Copy the Railway URL and share it with others

---

## Later: Update Your App

```powershell
cd "c:\Raph Folders\VS File Code\HrmanagementSystem"
git add .
git commit -m "Your changes"
git push origin main
```

Railway automatically redeploys!

---

## Stuck? Check Logs

```powershell
railway logs -f
```

This shows what's wrong.

---

**Need detailed guide?** See `RAILWAY_DEPLOYMENT_SQLITE.md`
