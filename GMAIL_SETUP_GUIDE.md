# GMAIL SETUP GUIDE FOR PASSWORD RESET OTP

This guide will help you set up Gmail to send OTP emails for password reset functionality.

## Step 1: Enable 2-Factor Authentication on Gmail

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Look for "How you sign in to Google" section
3. Click on "2-Step Verification"
4. Follow the steps to enable 2-Factor Authentication

## Step 2: Generate App Password

1. Go back to [Google Account Security](https://myaccount.google.com/security)
2. In the left sidebar, click "App passwords" (appears only if 2FA is enabled)
3. Select "Mail" and "Windows Computer" (or your platform)
4. Click "Generate"
5. Google will generate a 16-character password
6. Copy this password

## Step 3: Set Environment Variables

Add these to your system environment variables or .env file:

### On Windows (Command Prompt):
```
set EMAIL_HOST_USER=your-email@gmail.com
set EMAIL_HOST_PASSWORD=your-16-character-app-password
```

### On Windows (PowerShell):
```
$env:EMAIL_HOST_USER="your-email@gmail.com"
$env:EMAIL_HOST_PASSWORD="your-16-character-app-password"
```

### In .env file (if using python-decouple):
```
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-character-app-password
```

## Step 4: Test Email Configuration

Run this command in Django shell:

```
python manage.py shell
```

Then run:

```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    'Test Email from HRMS',
    'This is a test email for password reset OTP functionality.',
    settings.DEFAULT_FROM_EMAIL,
    ['your-email@gmail.com'],
    fail_silently=False,
)
print("Email sent successfully!")
```

## Step 5: Test Password Reset Flow

1. Start Django server: `python manage.py runserver`
2. Go to login page
3. Click "Forgot Password?"
4. Enter your registered email
5. Check your inbox for OTP
6. Enter OTP and set new password

## Security Notes

⚠️ **IMPORTANT SECURITY TIPS:**

- Never commit your EMAIL_HOST_PASSWORD to version control
- Use environment variables for sensitive credentials
- For production, use Django environment (.env) files
- Consider using Gmail's App Password instead of main password
- Rotate app passwords regularly
- Keep your SECRET_KEY secure

## Troubleshooting

### "Authentication failed"
- Ensure 2FA is enabled on Gmail
- Verify the app password is correct (no spaces)
- Check that EMAIL_HOST_USER is correct

### "SMTP Connection Error"
- Verify firewall is not blocking port 587
- Check internet connection
- Ensure Gmail credentials are set correctly

### "Less secure app access"
- Gmail no longer allows "less secure apps"
- Use App Password method (described above) instead

## Settings Configuration

The email settings in `hrms/settings.py` are already configured:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'your-email@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'your-app-password')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

## Features Implemented

✅ Forgot Password Page - Users can request password reset
✅ OTP Generation & Delivery - 6-digit OTP sent to registered email
✅ OTP Verification - Users verify OTP within 15 minutes
✅ Password Reset - Users set new password after OTP verification
✅ Email Templates - Professional email format
✅ Security - Token validation, OTP expiration, one-time use
✅ Password Strength Indicator - Real-time password strength feedback
✅ Success Confirmation - Clear success message and security tips

## OTP Configuration

- **OTP Length:** 6 digits
- **OTP Validity:** 15 minutes
- **OTP Format:** Random 6-digit number

Each OTP is single-use and expires after 15 minutes.
