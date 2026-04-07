# 📧 Gmail OTP Password Reset Setup Guide

This guide will help you configure Gmail for sending password reset OTP codes in your HR Management System.

---

## Problem Summary

✅ **Fixed Issues:**
- Password reset endpoint now generates OTP codes
- OTP is sent via email (Gmail)
- User can verify OTP and reset password
- OTP expires after 15 minutes
- All email configuration added to Django settings

---

## Step 1: Get Gmail App Password

Gmail no longer allows direct SMTP login with your regular password. You need to create an **App Password** instead.

### Prerequisites:
- Gmail account
- 2-Factor Authentication enabled on your Google account

### Create App Password:

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. In left sidebar, select **App passwords** (below 2-Step Verification)
   - If you don't see "App passwords", you need to enable 2FA first
3. Select **Mail** and **Windows Computer** (or your device)
4. Google will generate a 16-character password
5. **Copy this password** - you'll need it in Step 2

**Example App Password:** `abcd efgh ijkl mnop`

---

## Step 2: Configure Environment Variables

You have two options:

### Option A: Create a `.env` file (Recommended for Development)

Create a file named `.env` in your project root (`c:\Raph Folders\VS File Code\HrmanagementSystem\.env`):

```bash
# Gmail Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

**Important:** Replace:
- `your-email@gmail.com` with your actual Gmail address
- `abcd efgh ijkl mnop` with your 16-character App Password

### Option B: Set Environment Variables (Windows)

Open PowerShell and run these commands:

```powershell
# Set environment variables
$env:EMAIL_HOST = "smtp.gmail.com"
$env:EMAIL_PORT = "587"
$env:EMAIL_USE_TLS = "True"
$env:EMAIL_HOST_USER = "your-email@gmail.com"
$env:EMAIL_HOST_PASSWORD = "abcd efgh ijkl mnop"
$env:DEFAULT_FROM_EMAIL = "your-email@gmail.com"

# Verify they're set
Get-ChildItem env:EMAIL_*
```

### Option C: Use a Package for .env Files

Install python-decouple (already in requirements.txt):

```bash
pip install python-decouple
```

Then update settings.py to use it (already configured!).

---

## Step 3: Test Email Configuration (Optional)

### Option 1: Test via Django Shell

Open a terminal in your project and run:

```bash
# Navigate to project
cd hrms

# Open Django shell
python manage.py shell
```

Then paste this code:

```python
from django.core.mail import send_mail
from django.conf import settings

# Test sending email
try:
    send_mail(
        subject='Test Email from HRMS',
        message='If you see this, your email configuration is working!',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['your-email@gmail.com'],  # Replace with your email
        fail_silently=False,
    )
    print("✅ Email sent successfully!")
except Exception as e:
    print(f"❌ Email failed: {e}")

# Exit shell
exit()
```

### Option 2: Test via Console Backend (Development)

To print emails to console instead of sending (useful for testing):

Edit `hrms/settings.py` and uncomment this line:

```python
if DEBUG:
    # Uncomment next line to print emails to console instead of sending
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Now when you request a password reset, the OTP will be printed in the console instead of being sent.

---

## Step 4: Test Password Reset Flow

### 1. Request Password Reset

Make a POST request to:

```bash
POST http://localhost:8000/api/auth/password/reset-request/
Content-Type: application/json

{
  "email": "john@example.com"
}
```

**Or with username:**

```bash
{
  "username": "john"
}
```

**Response:**
```json
{
  "message": "If an account exists with this email/username, a password reset OTP has been sent to your email address.",
  "status": "success",
  "expired_in_minutes": 15
}
```

✅ **Check your email** - You should receive an email with the OTP code!

### 2. Verify OTP and Reset Password

Once you receive the OTP from email, use it to reset the password:

```bash
POST http://localhost:8000/api/auth/password/verify-reset-otp/
Content-Type: application/json

{
  "email": "john@example.com",
  "otp_code": "123456",
  "new_password": "NewSecure@Pass789",
  "confirm_password": "NewSecure@Pass789"
}
```

**Response:**
```json
{
  "message": "Password has been reset successfully. You can now login with your new password.",
  "status": "success"
}
```

✅ **Success!** You can now login with the new password.

---

## Using cURL to Test

If you prefer command line testing:

### Request OTP:
```bash
curl -X POST http://localhost:8000/api/auth/password/reset-request/ \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com"}'
```

### Verify OTP and Reset Password:
```bash
curl -X POST http://localhost:8000/api/auth/password/verify-reset-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "otp_code": "123456",
    "new_password": "NewSecure@Pass789",
    "confirm_password": "NewSecure@Pass789"
  }'
```

---

## Using Postman to Test

### Step 1: Request OTP

1. Open Postman
2. Create a new POST request:
   - **URL:** `http://localhost:8000/api/auth/password/reset-request/`
   - **Method:** POST
   - **Body (raw JSON):**
     ```json
     {"email": "john@example.com"}
     ```
3. Click **Send**
4. Check your email for the OTP code

### Step 2: Verify OTP

1. Create another POST request:
   - **URL:** `http://localhost:8000/api/auth/password/verify-reset-otp/`
   - **Method:** POST
   - **Body (raw JSON):**
     ```json
     {
       "email": "john@example.com",
       "otp_code": "123456",
       "new_password": "NewSecure@Pass789",
       "confirm_password": "NewSecure@Pass789"
     }
     ```
2. Click **Send**
3. You should get a success response

---

## Password Requirements

When resetting your password, ensure it meets these requirements:

✅ **Must have:**
- Minimum 12 characters
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one number (0-9)
- At least one special character (!@#$%^&*)

❌ **Cannot have:**
- Common patterns (123456, password, qwerty)
- User's name or username
- Sequences (abcdef, 12345678)

**Good Examples:**
- `MyPass@123`
- `Secure#2024$`
- `HR.System@456`

**Bad Examples:**
- `password123` (too common)
- `12345678` (only numbers)
- `MyName@123` (contains username)

---

## Troubleshooting

### ❌ Email not being sent?

**Check 1: Email Configuration**
```python
# In Django shell:
from django.conf import settings
print(f"Host: {settings.EMAIL_HOST}")
print(f"Port: {settings.EMAIL_PORT}")
print(f"User: {settings.EMAIL_HOST_USER}")
print(f"Use TLS: {settings.EMAIL_USE_TLS}")
```

**Check 2: Gmail Account**
- Verify you're using an App Password, not your regular Gmail password
- Check if [Less secure app access](https://myaccount.google.com/lesssecureapps) is enabled (for older accounts)
- Verify 2FA is enabled on your Google account
- Check if your account is locked for security reasons

**Check 3: Firewall/Network**
- Ensure outbound SMTP (port 587) is not blocked
- Try a different network if possible

### ❌ "Email service error" response?

1. Check Django logs in the terminal for detailed error
2. Verify `EMAIL_HOST_PASSWORD` doesn't have typos
3. Ensure no spaces at the beginning/end of passwords in .env file
4. Restart Django server after changing .env file

### ❌ OTP expires too quickly?

OTP is valid for **15 minutes** by default. To change this:

Edit `employees/auth_views.py` and change this line:

```python
# Change 15 to your desired minutes
otp_event = SecurityEventLog.objects.filter(
    user=user,
    event_type='password_reset_otp',
    created_at__gte=timezone.now() - timedelta(minutes=15)  # ← Change this
)
```

### ❌ "Invalid OTP code" error?

1. Make sure you're entering the exact OTP from the email
2. OTP is case-sensitive (6 digits only, no letters)
3. Check if OTP has expired (valid for 15 minutes)
4. Request a new OTP instead of reusing old ones

### ❌ "Password reset OTP has expired"?

The OTP is valid for 15 minutes. Request a new password reset to get a new OTP:

```bash
curl -X POST http://localhost:8000/api/auth/password/reset-request/ \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com"}'
```

---

## Email Content

When users request a password reset, they receive an email like this:

```
Subject: Password Reset Request - OTP

Dear John,

You requested a password reset. Your One-Time Password (OTP) is:

    123456

This OTP is valid for 15 minutes. Do not share this code with anyone.

If you did not request a password reset, please ignore this email.

---
HR Management System
```

---

## For Production Deployment

### On Railway or similar platforms:

1. Add environment variables in your deployment dashboard:
   - `EMAIL_HOST` = `smtp.gmail.com`
   - `EMAIL_PORT` = `587`
   - `EMAIL_USE_TLS` = `True`
   - `EMAIL_HOST_USER` = your Gmail address
   - `EMAIL_HOST_PASSWORD` = your App Password
   - `DEFAULT_FROM_EMAIL` = your Gmail address

2. Update `requirements.txt` to ensure `python-decouple` is included (already done!)

3. Never commit your `.env` file to git:
   - Add `.env` to `.gitignore`

---

## API Endpoints Summary

| Endpoint | Method | Purpose | Auth Required |
|----------|--------|---------|---|
| `/api/auth/password/reset-request/` | POST | Request password reset OTP | ❌ No |
| `/api/auth/password/verify-reset-otp/` | POST | Verify OTP and reset password | ❌ No |
| `/api/auth/password/change/` | POST | Change password (for logged-in users) | ✅ Yes |

---

## Request/Response Examples

### Request OTP

**Request:**
```json
POST /api/auth/password/reset-request/
{
  "email": "john@example.com"
}
```

**Success Response (200):**
```json
{
  "message": "If an account exists with this email/username, a password reset OTP has been sent to your email address.",
  "status": "success",
  "expired_in_minutes": 15
}
```

**Error Response (500):**
```json
{
  "message": "Failed to send reset email. Please check your email settings and try again.",
  "status": "error",
  "error_detail": "Email service error"
}
```

### Verify OTP and Reset Password

**Request:**
```json
POST /api/auth/password/verify-reset-otp/
{
  "email": "john@example.com",
  "otp_code": "123456",
  "new_password": "NewSecure@Pass789",
  "confirm_password": "NewSecure@Pass789"
}
```

**Success Response (200):**
```json
{
  "message": "Password has been reset successfully. You can now login with your new password.",
  "status": "success"
}
```

**Error Responses:**
```json
// Missing fields
{
  "error": "otp_code, new_password, and confirm_password are required"
}

// Passwords don't match
{
  "error": "New passwords do not match"
}

// Weak password
{
  "error": "Password must be at least 12 characters long..."
}

// Invalid OTP
{
  "error": "Invalid OTP code"
}

// Expired OTP
{
  "error": "OTP has expired or is invalid. Please request a new password reset OTP."
}
```

---

## Security Features Implemented

✅ **OTP Security:**
- 6-digit code (1 million combinations)
- Expires after 15 minutes
- One-time use only
- Rate limited (prevent brute force)

✅ **Password Reset Security:**
- Email verification required
- OTP verification required
- Password strength validation
- 12+ character minimum
- Special characters required
- Can't reuse recent passwords
- Logged in security event log

✅ **Privacy:**
- Doesn't reveal if email exists
- Generic response for security
- No sensitive data in logs

---

## Frequently Asked Questions

**Q: Why do I need an App Password instead of my Gmail password?**
A: Google disabled "Less Secure App Access" for security. App Passwords are more secure and device-specific.

**Q: Can I use a different email provider?**
A: Yes! SMTP works with most email providers. Change `EMAIL_HOST` in settings.py:
- Outlook: `smtp.outlook.com`
- Yahoo: `smtp.mail.yahoo.com`
- SendGrid: `smtp.sendgrid.net`

**Q: Can I customize the OTP email message?**
A: Yes! Edit the email template in `employees/auth_views.py`, look for the `message = f"""` section.

**Q: How do I increase the OTP validity period?**
A: Change the `timedelta(minutes=15)` in `employees/auth_views.py` to your desired duration.

**Q: Can users request multiple OTPs?**
A: Yes, each request generates a new OTP. Only the latest one is valid.

---

## Success Checklist

After setup, you should be able to:

- [ ] Request password reset OTP without errors
- [ ] Receive email with 6-digit OTP code
- [ ] Enter OTP code to verify
- [ ] Reset password with new strong password
- [ ] Login with new password

---

**Last Updated:** April 5, 2026  
**Status:** ✅ READY FOR USE  
**Support:** Check terminal logs if emails don't send

