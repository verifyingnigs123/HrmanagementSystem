# Production settings for Railway
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'your-secret-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['*']

# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('RAILWAY_DB_NAME', 'hrms'),
        'USER': os.environ.get('RAILWAY_DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('RAILWAY_DB_PASSWORD', ''),
        'HOST': os.environ.get('RAILWAY_DB_HOST', 'localhost'),
        'PORT': os.environ.get('RAILWAY_DB_PORT', '5432'),
    }
}

# Enable HTTPS/SSL
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
