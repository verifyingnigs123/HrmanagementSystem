# Railway Deployment Checklist

## Pre-Deployment ✅

- [ ] Python version: 3.11 or higher
- [ ] All dependencies in `requirements.txt`
- [ ] `Procfile` created in project root
- [ ] `.gitignore` configured
- [ ] Django `settings.py` handles environment variables
- [ ] Database migrations created (`python manage.py migrate`)
- [ ] Static files configured (`STATIC_ROOT`, `STATIC_URL`)
- [ ] Secret key generated and stored safely

## GitHub Setup ✅

- [ ] Git repository initialized (`git init`)
- [ ] All files committed (`git add . && git commit -m "..."`)
- [ ] Remote added (`git remote add origin [URL]`)
- [ ] Code pushed to GitHub (`git push -u origin main`)

## Railway Setup ✅

- [ ] Railway account created (https://railway.app)
- [ ] Project created in Railway
- [ ] GitHub repository connected
- [ ] PostgreSQL database added
- [ ] Environment variables configured:
  - [ ] `DJANGO_SECRET_KEY`
  - [ ] `DEBUG=False`
  - [ ] `ALLOWED_HOSTS`
  - [ ] `DATABASE_URL` (auto from Railway)

## Deployment ✅

- [ ] Deploy triggered (auto or manual)
- [ ] Build logs checked for errors
- [ ] Migrations run successfully
- [ ] Admin user created (if needed)
- [ ] Application accessible at Railway URL
- [ ] Login tested with demo credentials
- [ ] Dashboard loads correctly

## Post-Deployment ✅

- [ ] Demo users created
- [ ] All 4 role dashboards tested
- [ ] Sidebar navigation working
- [ ] Notifications bell visible
- [ ] Profile dropdown functional
- [ ] Logout working
- [ ] Static files loading (CSS, icons)

## Important Notes

- Railway provides automatic SSL/HTTPS
- Database backups are handled by Railway
- Auto-redeploy on GitHub push (if connected)
- Free tier includes: 5GB of storage, $5 credit/month
- Check Railway logs regularly: `railway logs -f`

## Support Links

- Railway Docs: https://docs.railway.app
- Django Deployment Guide: https://docs.djangoproject.com/en/stable/howto/deployment/
- PostgreSQL on Railway: https://docs.railway.app/databases/postgresql
