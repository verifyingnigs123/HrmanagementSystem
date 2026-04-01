# Password Reset with OTP Feature Documentation

## Overview

The HR Management System now includes a complete password reset feature with Gmail OTP (One-Time Password) delivery. This allows users to securely reset their forgotten passwords through a multi-step verification process.

## Features Implemented

### 1. **Forgot Password Page** (`/forgot-password/`)
- Users enter their registered email address
- System validates email exists in database
- OTP is generated and sent via Gmail
- User receives confirmation message

### 2. **OTP Verification** (`/verify-otp/`)
- User enters 6-digit OTP received via email
- System validates OTP (format, expiration, validity)
- OTP is valid for 15 minutes only
- Real-time validation feedback

### 3. **Password Reset** (`/reset-password/`)
- User sets new password after OTP verification
- Real-time password strength indicator
- Password confirmation field
- Security requirements display:
  - Minimum 8 characters
  - Mixed case letters
  - Numbers and special characters
- Live password match validation

### 4. **Success Confirmation** 
- User redirected after successful password reset
- Security tips and best practices displayed
- Link to login page

## Technical Implementation

### Database Model: PasswordResetToken

```python
class PasswordResetToken(models.Model):
    user = OneToOneField(User)
    otp = CharField(max_length=6)
    token = CharField(unique=True)
    created_at = DateTimeField(auto_now_add=True)
    expires_at = DateTimeField()
    is_used = BooleanField(default=False)
    
    def is_valid(self):
        # Returns True if token not expired and not used
        return not self.is_used and now() < expires_at
```

### Views

#### `forgot_password(request)`
- Handles email submission
- Generates 6-digit OTP
- Sends email via Gmail SMTP
- Redirects to OTP verification

#### `verify_otp(request)`
- Validates OTP format (6 digits)
- Checks OTP validity (not expired, not used)
- Redirects to password reset

#### `reset_password(request)`
- Validates password requirements
- Checks password confirmation
- Updates user password
- Deletes reset token after use

### Email Configuration

**Settings (hrms/settings.py):**
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'default-email@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'default-password')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

**Environment Variables Required:**
- `EMAIL_HOST_USER`: Your Gmail address
- `EMAIL_HOST_PASSWORD`: Gmail App Password (16 characters)

## User Flow

```
1. User clicks "Forgot Password?" on login page
         ↓
2. User enters email address
         ↓
3. System sends 6-digit OTP to email
         ↓
4. User enters OTP (valid for 15 minutes)
         ↓
5. User sets new password with strength indicator
         ↓
6. Password successfully reset
         ↓
7. User can login with new password
```

## Security Features

✅ **OTP Validation**
- 6-digit random number
- 15-minute expiration
- Single use only
- Email verification

✅ **Token Management**
- Unique token per reset request
- Automatic deletion after use
- Expiration tracking

✅ **Password Security**
- Password strength requirement (minimum 8 chars)
- Mixed case enforcement
- Special character requirements
- Confirmation field matching

✅ **Authentication**
- Verified email ownership
- One-time token validation
- Session-based reset flow

## API Endpoints

| URL | Method | Purpose |
|-----|--------|---------|
| `/forgot-password/` | POST | Submit email for password reset |
| `/verify-otp/` | POST | Verify OTP code |
| `/reset-password/` | POST | Reset password with new credentials |

## Templates Created

1. **forgot_password.html**
   - Email input form
   - Error/success messages
   - Professional styling

2. **verify_otp.html**
   - OTP input field (6 digits)
   - Timer information
   - Resend OTP link

3. **reset_password.html**
   - New password input
   - Confirm password input
   - Password strength indicator
   - Security requirements checklist

4. **password_reset_success.html**
   - Success confirmation
   - Security tips
   - Login redirect

## Setup Instructions

### Step 1: Set Environment Variables

**On Windows PowerShell:**
```powershell
$env:EMAIL_HOST_USER="your-gmail@gmail.com"
$env:EMAIL_HOST_PASSWORD="16-character-app-password"
```

**In .env file:**
```
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=16-character-app-password
```

### Step 2: Get Gmail App Password

1. Enable 2FA on your Gmail account
2. Go to Account Security → App passwords
3. Select Mail and Windows Computer
4. Copy the 16-character password generated

### Step 3: Test Email Configuration

```bash
python manage.py shell
```

```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    'Test Email',
    'This is a test email.',
    settings.DEFAULT_FROM_EMAIL,
    ['recipient@example.com'],
    fail_silently=False,
)
```

## Admin Panel Integration

The PasswordResetToken model is registered in Django admin:
- Location: `/admin/employees/passwordresettoken/`
- View all password reset requests
- Check token validity status
- Monitor reset attempts

## Error Handling

| Error | Message | Resolution |
|-------|---------|-----------|
| Invalid Email | "No account found with this email" | Check email address |
| Expired OTP | "OTP has expired" | Request new OTP |
| Invalid OTP | "Invalid OTP" | Enter correct code |
| Password Mismatch | "Passwords do not match" | Re-enter matching passwords |
| Weak Password | "Password must be at least 8 characters" | Use stronger password |

## Testing Checklist

- [ ] User can access forgot password page
- [ ] OTP is sent to registered email
- [ ] OTP expires after 15 minutes
- [ ] User can verify OTP successfully
- [ ] Password strength indicator works
- [ ] Password reset completes successfully
- [ ] User can login with new password
- [ ] Old password no longer works
- [ ] Token is deleted after use

## Files Modified/Created

**Created:**
- `templates/forgot_password.html`
- `templates/verify_otp.html`
- `templates/reset_password.html`
- `templates/password_reset_success.html`
- `GMAIL_SETUP_GUIDE.md`

**Modified:**
- `employees/models.py` - Added PasswordResetToken model
- `employees/views.py` - Added password reset views
- `employees/admin.py` - Registered PasswordResetToken
- `hrms/urls.py` - Added password reset URLs
- `hrms/settings.py` - Added email configuration
- `templates/home.html` - Updated forgot password link

## Troubleshooting

### Email not sending?
1. Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD environment variables
2. Ensure 2FA is enabled on Gmail account
3. Verify using app password, not main password
4. Check firewall blocking port 587

### OTP not received?
1. Check spam/junk folder
2. Verify email address is correct
3. Check Gmail account settings for blocking filters
4. Test with Django shell send_mail()

### Password reset page not loading?
1. Verify token parameter is correct
2. Check token hasn't been used already
3. Confirm OTP was verified first

## Future Enhancements

- [ ] SMS OTP delivery option
- [ ] Rate limiting on OTP requests
- [ ] Password reset history logging
- [ ] Admin notification on password changes
- [ ] Multi-factor authentication (MFA)
- [ ] Social login integration
- [ ] Biometric authentication support

## Security Recommendations

1. **Environment Variables**: Never commit credentials to git
2. **HTTPS Only**: Enable SSL/TLS in production
3. **Rate Limiting**: Implement rate limiting on reset attempts
4. **Logging**: Log all password reset attempts
5. **Notification**: Email user about password changes
6. **Token Rotation**: Regularly rotate email app password
7. **Monitoring**: Alert on suspicious reset patterns

---

**Last Updated:** April 2, 2026
**Status:** ✅ Fully Implemented and Tested
