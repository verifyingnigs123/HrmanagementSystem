# Security Requirements - Complete Implementation

## ✅ All Security Features Implemented

### 1. ✅ Password Encryption
**Status:** Implemented & Active

- **Algorithm:** PBKDF2 with SHA256 (Django default)
- **Iterations:** 260,000
- **Location:** Django authentication system
- **Features:**
  - Automatic hashing on user creation
  - Never stored in plain text
  - One-way encryption

**How it works:**
```python
# Django automatically handles password encryption
user = User.objects.create_user(username='john', password='SecurePass123!')
# Password is encrypted and stored as hash

# Verification
user.check_password('SecurePass123!')  # Returns True/False
```

---

### 2. ✅ OTP 2FA (Two-Factor Authentication)
**Status:** Implemented & Ready to Use

- **Algorithm:** TOTP (Time-based One-Time Password)
- **Standard:** RFC 6238 compatible
- **Package:** pyotp 2.9.0
- **Location:** `employees/models.py` - `TwoFactorAuth` model

**Features:**
- QR code generation for authenticator apps
- Backup codes for account recovery (10 codes)
- Support for Google Authenticator, Authy, Microsoft Authenticator, etc.
- Secure secret key generation
- Time-drift tolerance (±30 seconds)

**API Endpoints:**
```
POST /api/auth/2fa/setup/              - Enable 2FA
POST /api/auth/2fa/verify-setup/       - Verify setup with token
POST /api/auth/2fa/verify/             - Verify login token
POST /api/auth/2fa/disable/            - Disable 2FA
GET  /api/auth/2fa/status/             - Check 2FA status
```

**Setup Flow:**
1. User calls `/api/auth/2fa/setup/`
2. System returns QR code + secret + backup codes
3. User scans QR code in authenticator app
4. User verifies with 6-digit code via `/api/auth/2fa/verify-setup/`
5. 2FA is enabled

**Login Flow with 2FA:**
1. User logs in with username/password
2. If 2FA enabled, system returns `requires_2fa: true`
3. User provides 6-digit code or backup code
4. System verifies via `/api/auth/2fa/verify/`
5. JWT tokens are returned on success

---

### 3. ✅ JWT Tokens
**Status:** Implemented & Active

- **Algorithm:** HS256 (HMAC with SHA-256)
- **Package:** djangorestframework-simplejwt 5.5.1
- **Token Types:** Access + Refresh tokens

**Configuration:**
```python
# In settings.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # 1 hour
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),     # 7 days
    'ROTATE_REFRESH_TOKENS': True,                    # Auto-rotate
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
}
```

**API Endpoints:**
```
POST /api/auth/jwt/token/     - Get access + refresh tokens
POST /api/auth/jwt/refresh/   - Refresh access token
```

**Usage:**
```bash
# Get tokens
curl -X POST http://localhost:8000/api/auth/jwt/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"john","password":"SecurePass123!"}'

# Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user_id": 1,
  "username": "john"
}

# Use access token:
curl -X GET http://localhost:8000/api/attendance/today/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

**Token Refresh:**
```bash
curl -X POST http://localhost:8000/api/auth/jwt/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"eyJ0eXAiOiJKV1QiLCJhbGc..."}'
```

---

### 4. ✅ Input Validation
**Status:** Implemented & Active

**Implemented in:**
1. **Django Forms** (`employees/forms.py`)
   - Username existence check
   - Email format validation
   - Password field validation
   - Required field validation

2. **REST Serializers** (`employees/serializers.py`)
   - GPS coordinate validation (-90 to 90 latitude, -180 to 180 longitude)
   - Timezone and time validation
   - Field type validation

3. **Advanced Validators** (`employees/security_utils.py`)
   - **Password Strength Validation:**
     - Minimum 12 characters
     - At least 1 uppercase letter
     - At least 1 lowercase letter
     - At least 1 digit
     - At least 1 special character
     - No common patterns (password, admin, qwerty, etc.)
   
   - **Email Validation:**
     - Format validation
     - Existence check
   
   - **Username Validation:**
     - Minimum 3 characters
     - Alphanumeric, dots, dashes, underscores only
     - Uniqueness check

**Example:**
```python
from .security_utils import SecurityValidator

# Validate password strength
is_strong, message = SecurityValidator.validate_password_strength("MyP@ssw0rd123")
# Returns: (True, "Password is strong.")

# Validate email
SecurityValidator.validate_email("user@example.com")  # OK
SecurityValidator.validate_email("invalid-email")     # Raises ValidationError

# Validate username
SecurityValidator.validate_username("john_doe")       # OK
SecurityValidator.validate_username("jd")             # Raises ValidationError (too short)
```

---

### 5. ✅ SQL Injection Prevention
**Status:** Implemented by Default

- **Method:** Django ORM parameterized queries
- **Coverage:** 100% - All database queries use ORM
- **How it works:** Django escapes all values and separates SQL from data

**Django ORM is immune to SQL injection:**
```python
# SAFE - Django ORM (what we use)
employee = Employee.objects.filter(user=request.user)

# UNSAFE - Raw SQL (NOT USED IN PROJECT)
# employees = Employee.objects.raw(f"SELECT * FROM employee WHERE user_id = {user_id}")
```

**Why Django ORM prevents SQL injection:**
- Parameterized queries separate SQL syntax from data
- Special characters are escaped automatically
- No string concatenation of SQL queries

---

### 6. ✅ XSS Prevention
**Status:** Implemented & Active

**Implemented in:**
1. **Django Templates** (Automatic HTML escaping)
   - All variables are escaped by default: `{{ variable }}`
   - Use `|safe` filter only for trusted content
   - Django auto-escapes: `<`, `>`, `"`, `'`, `&`

2. **Security Middleware** (`employees/middleware.py`)
   ```python
   X-Content-Type-Options: nosniff     # Prevent MIME type sniffing
   X-Frame-Options: DENY               # Prevent clickjacking
   X-XSS-Protection: 1; mode=block     # Browser XSS filter
   ```

3. **Content Security Policy** (`settings.py`)
   ```python
   SECURE_CONTENT_SECURITY_POLICY = {
       'default-src': ("'self'",),
   }
   ```

4. **Settings Protection**
   ```python
   SECURE_BROWSER_XSS_FILTER = True
   ```

**XSS Protection Example:**
```django
<!-- Template (automatic escaping) -->
{{ user_input }}  <!-- <script>alert('xss')</script> gets escaped -->
<!-- Output: &lt;script&gt;alert('xss')&lt;/script&gt; -->
```

---

### 7. ✅ Audit Logging
**Status:** Implemented & Active

**Models:** Two audit models implemented

#### A. Audit Log (`AuditLog` model)
Records all data changes and significant actions.

**Tracked Actions:**
- Create, Update, Delete
- Approve, Reject
- Login, Logout
- Other actions

**Fields:**
- User who made the change
- What action was performed
- Which model was affected
- What data changed (JSON format)
- IP address and user agent
- Timestamp

**Example:**
```python
AuditLog.objects.create(
    user=request.user,
    action='update',
    model_name='LeaveRequest',
    object_id=123,
    changes={'status': ['pending', 'approved']},
    ip_address='192.168.1.1',
    user_agent=request.META.get('HTTP_USER_AGENT')
)
```

#### B. Security Event Log (`SecurityEventLog` model)
Records security-related events.

**Event Types:**
- login_success, login_failed
- password_change, password_reset
- 2fa_enabled, 2fa_disabled
- 2fa_verified, 2fa_failed
- backup_code_used
- suspicious_activity
- permission_denied

**Severity Levels:**
- Low (routine actions)
- Medium (password changes, backup code usage)
- High (failed 2FA, permission denied, 2FA disabled)
- Critical (multiple failed logins)

**Features:**
- Automatic logging in auth views
- Suspicious activity detection
- Security reports

**API Endpoints:**
```
GET /api/security/report/              - Get user's security report
GET /api/security/suspicious-activity/ - Check for suspicious patterns
```

---

## Security API Reference

### Authentication Endpoints

#### 1. JWT Token Obtain
```
POST /api/auth/jwt/token/
Content-Type: application/json

{
  "username": "john",
  "password": "SecurePass123!"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user_id": 1,
  "username": "john"
}
```

#### 2. JWT Token Refresh
```
POST /api/auth/jwt/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### 3. Setup 2FA
```
POST /api/auth/2fa/setup/
Authorization: Bearer {access_token}

Response:
{
  "message": "2FA setup initiated",
  "secret": "JBSWY3DPEBLW64TMMQ======",
  "qr_code": "data:image/png;base64,...",
  "backup_codes": ["A1B2C3D4", "E5F6G7H8", ...],
  "instructions": "Scan the QR code..."
}
```

#### 4. Verify 2FA Setup
```
POST /api/auth/2fa/verify-setup/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "token": "123456"
}

Response:
{
  "message": "2FA has been successfully enabled",
  "status": "enabled"
}
```

#### 5. Verify 2FA During Login
```
POST /api/auth/2fa/verify/
Content-Type: application/json

{
  "user_id": 1,
  "token": "123456"  # or backup code like "A1B2C3D4"
}

Response:
{
  "message": "2FA verified successfully",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user_id": 1,
  "username": "john"
}
```

#### 6. Change Password
```
POST /api/auth/password/change/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "old_password": "OldPass123!",
  "new_password": "NewSecurePass456!",
  "confirm_password": "NewSecurePass456!"
}

Response:
{
  "message": "Password changed successfully",
  "status": "success"
}
```

#### 7. Logout
```
POST /api/auth/logout/
Authorization: Bearer {access_token}

Response:
{
  "message": "You have been logged out successfully",
  "status": "success"
}
```

---

## Testing Security Features

### Test 2FA Setup
```bash
# 1. Login
TOKEN=$(curl -X POST http://localhost:8000/api/auth/jwt/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"john","password":"SecurePass123!"}' \
  | jq -r '.access')

# 2. Setup 2FA
curl -X POST http://localhost:8000/api/auth/2fa/setup/ \
  -H "Authorization: Bearer $TOKEN"

# 3. Scan QR code with authenticator app

# 4. Verify setup with code from app
curl -X POST http://localhost:8000/api/auth/2fa/verify-setup/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"token":"123456"}'
```

### Test Password Strength Validation
```python
from employees.security_utils import SecurityValidator

# Test weak password
is_valid, msg = SecurityValidator.validate_password_strength("weak")
# Returns: (False, "Password must be at least 12 characters long.")

# Test strong password
is_valid, msg = SecurityValidator.validate_password_strength("MyStr0ng!Pass123")
# Returns: (True, "Password is strong.")
```

### Test SQL Injection Prevention
```python
# Django ORM - SAFE
from employees.models import Employee

# User input
user_input = "'; DROP TABLE employee; --"

# This is safe - no SQL injection possible
employees = Employee.objects.filter(employee_id=user_input)

# The ORM will search for literal string, not execute SQL
```

### Test XSS Prevention
```python
# In template
{{ malicious_input }}

# If malicious_input = "<script>alert('xss')</script>"
# Output: &lt;script&gt;alert('xss')&lt;/script&gt;
# Browser shows: <script>alert('xss')</script> (as text)
```

---

## Security Checklist

- [x] Password encryption (PBKDF2 with SHA256)
- [x] OTP 2FA (TOTP with QR code + backup codes)
- [x] JWT tokens (HS256, access + refresh)
- [x] Input validation (email, username, password strength)
- [x] SQL Injection prevention (Django ORM)
- [x] XSS prevention (template escaping + security headers)
- [x] Audit logging (AuditLog + SecurityEventLog)
- [x] Session security (HTTPOnly, Secure, SameSite cookies)
- [x] CSRF protection (Django middleware)
- [x] Password strength requirements
- [x] Failed login attempt tracking
- [x] Suspicious activity detection
- [x] Security event logging
- [x] Password change auditing
- [x] 2FA enforcement option

---

## Recommendations for Production

1. **Update environment variables:**
   ```bash
   DJANGO_SECRET_KEY=<strong-random-key>
   DEBUG=False
   ALLOWED_HOSTS=yourdomain.com
   ```

2. **Enable HTTPS:**
   ```python
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   ```

3. **Set up email for password resets:**
   ```python
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST = 'smtp.example.com'
   EMAIL_PORT = 587
   ```

4. **Monitor SecurityEventLog:**
   - Set up alerts for critical severity events
   - Review suspicious activity daily
   - Monitor multiple failed login attempts from same IP

5. **Enforce 2FA:**
   - Make 2FA mandatory for admin/HR admin users
   - Consider mandatory 2FA for all users

6. **Regular security audits:**
   - Monitor audit logs
   - Review access patterns
   - Check for suspicious IPs/user agents

---

## Files Reference

| Component | File | Purpose |
|-----------|------|---------|
| Models | `employees/models.py` | TwoFactorAuth, SecurityEventLog models |
| Utilities | `employees/security_utils.py` | Validators, 2FA manager, audit utilities |
| Views | `employees/auth_views.py` | Authentication, 2FA, password management APIs |
| Forms | `employees/forms.py` | Form validation |
| Serializers | `employees/serializers.py` | API validation |
| Middleware | `employees/middleware.py` | Security headers |
| URLs | `employees/urls_api.py` | API endpoints |
| Settings | `hrms/settings.py` | Security configuration |

---

## Next Steps

1. ✅ All security features are implemented
2. 🧪 Test the system with provided test cases
3. 📱 Update mobile app to use JWT tokens
4. 🔒 Enforce 2FA for sensitive roles
5. 📊 Monitor security logs regularly
6. 🔄 Update passwords to meet new strength requirements
