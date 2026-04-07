"""
Security utilities and helpers for HRMS system.
Includes password validation, 2FA management, and security event logging.
"""
import re
import logging
import pyotp
import qrcode
from io import BytesIO
from base64 import b64encode
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import SecurityEventLog, TwoFactorAuth

logger = logging.getLogger(__name__)


class SecurityValidator:
    """Advanced password and security validation."""
    
    @staticmethod
    def validate_password_strength(password):
        """
        Validate password strength.
        Requirements:
        - Minimum 12 characters
        - At least 1 uppercase letter
        - At least 1 lowercase letter
        - At least 1 digit
        - At least 1 special character
        Returns: (is_valid, message)
        """
        if len(password) < 12:
            return False, "Password must be at least 12 characters long."
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter."
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter."
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit."
        
        special_chars = re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password)
        if not special_chars:
            return False, "Password must contain at least one special character."
        
        # Check for common patterns
        common_patterns = [
            '123456', '654321', 'qwerty', 'asdfgh',
            'password', 'admin', 'letmein', 'welcome'
        ]
        if any(pattern in password.lower() for pattern in common_patterns):
            return False, "Password contains common patterns. Please use a unique password."
        
        return True, "Password is strong."
    
    @staticmethod
    def validate_email(email):
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationError("Invalid email format.")
        return True
    
    @staticmethod
    def check_password_reuse(user, new_password, check_last_n_passwords=5):
        """
        Check if user is trying to reuse old passwords.
        Returns: (is_different, message)
        """
        # This would require storing password history
        # For now, just check against current password
        if user.check_password(new_password):
            return False, "Cannot reuse your current password."
        return True, "Password is different from previous passwords."
    
    @staticmethod
    def validate_username(username):
        """Validate username format."""
        if len(username) < 3:
            raise ValidationError("Username must be at least 3 characters long.")
        
        if not re.match(r'^[a-zA-Z0-9._-]+$', username):
            raise ValidationError("Username can only contain letters, numbers, dots, dashes, and underscores.")
        
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        
        return True


class TwoFactorAuthManager:
    """Manage 2FA operations for users."""
    
    @staticmethod
    def enable_2fa(user):
        """
        Enable 2FA for a user and return QR code.
        Returns: (secret_key, qr_code_data_url, backup_codes)
        """
        try:
            twofa = TwoFactorAuth.objects.get(user=user)
        except TwoFactorAuth.DoesNotExist:
            twofa = TwoFactorAuth.objects.create(user=user)
        
        # Generate new secret
        secret = twofa.generate_secret_key()
        backup_codes = twofa.generate_backup_codes()
        twofa.save()
        
        # Generate QR code
        provisioning_uri = twofa.get_totp_uri()
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        qr_code_data = b64encode(buffer.getvalue()).decode()
        qr_code_url = f"data:image/png;base64,{qr_code_data}"
        
        return secret, qr_code_url, backup_codes
    
    @staticmethod
    def verify_2fa_setup(user, token):
        """
        Verify that 2FA is correctly configured by checking a token.
        Returns: (success, message)
        """
        try:
            twofa = TwoFactorAuth.objects.get(user=user)
        except TwoFactorAuth.DoesNotExist:
            return False, "2FA not initialized."
        
        if twofa.verify_token(token):
            twofa.is_enabled = True
            twofa.is_authenticator_enabled = True
            twofa.verified_at = timezone.now()
            twofa.save()
            
            SecurityEventLog.objects.create(
                user=user,
                event_type='2fa_enabled',
                description='Two-factor authentication enabled',
                severity='low'
            )
            
            return True, "2FA has been successfully enabled."
        else:
            return False, "Invalid authentication code. Please try again."
    
    @staticmethod
    def verify_login_token(user, token):
        """
        Verify 2FA token during login.
        Returns: (success, message)
        """
        try:
            twofa = TwoFactorAuth.objects.get(user=user)
        except TwoFactorAuth.DoesNotExist:
            return False, "2FA not enabled for this user."
        
        if not twofa.is_enabled:
            return False, "2FA is not enabled."
        
        # Try TOTP token
        if twofa.is_authenticator_enabled and twofa.verify_token(token):
            SecurityEventLog.objects.create(
                user=user,
                event_type='2fa_verified',
                description='2FA verification successful',
                severity='low'
            )
            return True, "2FA verified successfully."
        
        # Try backup code
        if twofa.use_backup_code(token.upper()):
            SecurityEventLog.objects.create(
                user=user,
                event_type='backup_code_used',
                description=f'Backup code used for 2FA',
                severity='medium'
            )
            return True, "2FA verified with backup code."
        
        # Log failed attempt
        SecurityEventLog.objects.create(
            user=user,
            event_type='2fa_failed',
            description='Failed 2FA verification attempt',
            severity='high',
            is_suspicious=True
        )
        
        return False, "Invalid 2FA code."
    
    @staticmethod
    def disable_2fa(user):
        """Disable 2FA for a user."""
        try:
            twofa = TwoFactorAuth.objects.get(user=user)
            twofa.is_enabled = False
            twofa.is_authenticator_enabled = False
            twofa.is_sms_enabled = False
            twofa.secret_key = ''
            twofa.save()
            
            SecurityEventLog.objects.create(
                user=user,
                event_type='2fa_disabled',
                description='Two-factor authentication disabled',
                severity='high'
            )
            
            return True, "2FA has been disabled."
        except TwoFactorAuth.DoesNotExist:
            return False, "2FA not found for this user."


class LoginSecurityManager:
    """Manage and track login security events."""
    
    @staticmethod
    def log_login_attempt(user, ip_address='', user_agent='', success=True):
        """Log login attempts for security monitoring."""
        event_type = 'login_success' if success else 'login_failed'
        severity = 'low' if success else 'medium'
        
        SecurityEventLog.objects.create(
            user=user if success else None,
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            severity=severity
        )
        
        # Check for suspicious activity (multiple failed attempts)
        if not success:
            failed_attempts = SecurityEventLog.objects.filter(
                event_type='login_failed',
                ip_address=ip_address,
                created_at__gte=timezone.now() - timezone.timedelta(minutes=15)
            ).count()
            
            if failed_attempts >= 5:
                SecurityEventLog.objects.create(
                    event_type='suspicious_activity',
                    description=f'Multiple failed login attempts from {ip_address}',
                    ip_address=ip_address,
                    severity='critical',
                    is_suspicious=True
                )
                return False, "Too many failed attempts. Please try again later."
        
        return True, "Login attempt logged."
    
    @staticmethod
    def get_suspicious_patterns(user):
        """Check for suspicious login patterns for a user."""
        recent_events = SecurityEventLog.objects.filter(
            user=user,
            created_at__gte=timezone.now() - timezone.timedelta(hours=24)
        )
        
        suspicious_found = recent_events.filter(is_suspicious=True).count()
        failed_logins = recent_events.filter(event_type='login_failed').count()
        
        return {
            'suspicious_events': suspicious_found,
            'failed_login_attempts': failed_logins,
            'is_risky': suspicious_found > 0 or failed_logins > 3
        }


class SecurityAuditManager:
    """Manage security audits and create audit trails."""
    
    @staticmethod
    def log_password_change(user, ip_address='', user_agent=''):
        """Log password change event."""
        SecurityEventLog.objects.create(
            user=user,
            event_type='password_change',
            description='User password changed',
            ip_address=ip_address,
            user_agent=user_agent,
            severity='medium'
        )
    
    @staticmethod
    def log_permission_denied(user, action, reason, ip_address=''):
        """Log permission denied events."""
        SecurityEventLog.objects.create(
            user=user if user.is_authenticated else None,
            event_type='permission_denied',
            description=f'Permission denied for action: {action}. Reason: {reason}',
            ip_address=ip_address,
            severity='high',
            is_suspicious=True if reason == 'unauthorized_access' else False
        )
    
    @staticmethod
    def get_security_report(user, days=30):
        """Get security report for a user."""
        start_date = timezone.now() - timezone.timedelta(days=days)
        
        events = SecurityEventLog.objects.filter(
            user=user,
            created_at__gte=start_date
        )
        
        return {
            'total_events': events.count(),
            'login_count': events.filter(event_type__in=['login_success', 'login_failed']).count(),
            'password_changes': events.filter(event_type='password_change').count(),
            'failed_logins': events.filter(event_type='login_failed').count(),
            'suspicious_events': events.filter(is_suspicious=True).count(),
            '2fa_verifications': events.filter(event_type__startswith='2fa').count(),
            'events_by_type': dict(
                events.values('event_type').annotate(count=models.Count('id')).values_list('event_type', 'count')
            )
        }


# Import models here to avoid circular imports
from django.db import models
