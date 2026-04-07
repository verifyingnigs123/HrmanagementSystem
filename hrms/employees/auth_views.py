"""
Authentication API endpoints with JWT and 2FA support.
Provides secure login, token refresh, and 2FA management endpoints.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.template.loader import render_to_string
import logging
import secrets
import string

from .models import TwoFactorAuth, SecurityEventLog
from .security_utils import (
    TwoFactorAuthManager, LoginSecurityManager, 
    SecurityValidator, SecurityAuditManager
)

logger = logging.getLogger(__name__)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer that adds 2FA requirement."""
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Check if user has 2FA enabled
        try:
            twofa = TwoFactorAuth.objects.get(user=self.user)
            if twofa.is_enabled:
                # Remove user info from response, will be added after 2FA
                data.pop('access', None)
                data.pop('refresh', None)
                data['requires_2fa'] = True
                data['user_id'] = self.user.id
                data['message'] = '2FA verification required'
        except TwoFactorAuth.DoesNotExist:
            data['requires_2fa'] = False
        
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token obtain view with login security logging."""
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        # Get client IP and user agent
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        username = request.data.get('username', '')
        
        # Track login attempt
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(username=username)
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                LoginSecurityManager.log_login_attempt(user, ip_address, user_agent, success=True)
            else:
                LoginSecurityManager.log_login_attempt(user, ip_address, user_agent, success=False)
        except User.DoesNotExist:
            LoginSecurityManager.log_login_attempt(None, ip_address, user_agent, success=False)
            response = super().post(request, *args, **kwargs)
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Extract client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_2fa_token(request):
    """
    Verify 2FA token and return JWT tokens if valid.
    Expects: user_id, token (6-digit code or backup code)
    """
    user_id = request.data.get('user_id')
    token = request.data.get('token', '').strip()
    
    ip_address = CustomTokenObtainPairView.get_client_ip(request)
    
    if not user_id or not token:
        return Response(
            {'error': 'user_id and token are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    from django.contrib.auth.models import User
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'error': 'Invalid user'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Verify 2FA token
    success,  message = TwoFactorAuthManager.verify_login_token(user, token)
    
    if success:
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': message,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
        }, status=status.HTTP_200_OK)
    else:
        return Response(
            {'error': message},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def setup_2fa(request):
    """
    Setup 2FA for the current user.
    Returns QR code and backup codes.
    """
    try:
        secret, qr_code_url, backup_codes = TwoFactorAuthManager.enable_2fa(request.user)
        
        return Response({
            'message': '2FA setup initiated',
            'secret': secret,
            'qr_code': qr_code_url,
            'backup_codes': backup_codes,
            'instructions': 'Scan the QR code with your authenticator app, or enter the secret key manually. Then verify with a code from your authenticator to complete the setup.',
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error setting up 2FA: {str(e)}")
        return Response(
            {'error': 'Failed to setup 2FA'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_2fa_setup(request):
    """
    Verify 2FA setup with a token.
    Expects: token (6-digit code from authenticator app)
    """
    token = request.data.get('token', '').strip()
    
    if not token:
        return Response(
            {'error': 'token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    success, message = TwoFactorAuthManager.verify_2fa_setup(request.user, token)
    
    if success:
        return Response({
            'message': message,
            'status': 'enabled'
        }, status=status.HTTP_200_OK)
    else:
        return Response(
            {'error': message},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disable_2fa(request):
    """Disable 2FA for the current user."""
    success, message = TwoFactorAuthManager.disable_2fa(request.user)
    
    if success:
        return Response({
            'message': message,
            'status': 'disabled'
        }, status=status.HTTP_200_OK)
    else:
        return Response(
            {'error': message},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_2fa_status(request):
    """Get current 2FA status for the user."""
    try:
        twofa = TwoFactorAuth.objects.get(user=request.user)
        return Response({
            'is_enabled': twofa.is_enabled,
            'is_authenticator_enabled': twofa.is_authenticator_enabled,
            'is_sms_enabled': twofa.is_sms_enabled,
            'backup_codes_remaining': len(twofa.backup_codes),
            'verified_at': twofa.verified_at,
        }, status=status.HTTP_200_OK)
    except TwoFactorAuth.DoesNotExist:
        return Response({
            'is_enabled': False,
            'message': '2FA not configured for this user'
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change user password with validation.
    Expects: old_password, new_password, confirm_password
    """
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    
    # Validate required fields
    if not all([old_password, new_password, confirm_password]):
        return Response(
            {'error': 'old_password, new_password, and confirm_password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify old password
    if not request.user.check_password(old_password):
        SecurityAuditManager.log_password_change(request.user, request.POST.get('ip', ''))
        return Response(
            {'error': 'Current password is incorrect'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Validate password match
    if new_password != confirm_password:
        return Response(
            {'error': 'New passwords do not match'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Same as current
    if request.user.check_password(new_password):
        return Response(
            {'error': 'New password cannot be the same as current password'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate password strength
    is_strong, strength_message = SecurityValidator.validate_password_strength(new_password)
    if not is_strong:
        return Response(
            {'error': strength_message},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check password reuse
    is_different, reuse_message = SecurityValidator.check_password_reuse(
        request.user, new_password
    )
    if not is_different:
        return Response(
            {'error': reuse_message},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Set new password
    request.user.set_password(new_password)
    request.user.save()
    
    ip_address = CustomTokenObtainPairView.get_client_ip(request)
    SecurityAuditManager.log_password_change(request.user, ip_address)
    
    return Response({
        'message': 'Password changed successfully',
        'status': 'success'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_request(request):
    """
    Request password reset.
    Generates OTP and sends it to user's email.
    Expects: email or username
    """
    email = request.data.get('email')
    username = request.data.get('username')
    
    from django.contrib.auth.models import User
    from django.conf import settings
    
    user = None
    if email:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            pass
    elif username:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            pass
    
    if user and user.email:
        try:
            # Generate 6-digit OTP
            otp_code = ''.join(secrets.choice(string.digits) for _ in range(6))
            
            # Store OTP in SecurityEventLog temporarily (with type 'password_reset_otp')
            SecurityEventLog.objects.create(
                user=user,
                event_type='password_reset_otp',
                description=f'Password reset OTP: {otp_code}',
                severity='medium',
                ip_address=CustomTokenObtainPairView.get_client_ip(request),
            )
            
            logger.info(f"[OTP Debug] Generated OTP for {user.email}: {otp_code}")
            
            # Send email with OTP - plain text
            subject = 'Password Reset Request - Your OTP Code'
            message = f"Dear {user.first_name or user.username},\n\nYou requested a password reset.\n\nYour One-Time Password (OTP) is:\n\n{otp_code}\n\nThis OTP is valid for 15 minutes. Do not share this code with anyone.\n\nIf you did not request a password reset, please ignore this email.\n\n---\nHR Management System"
            
            # HTML formatted email
            html_message = f"""
<html>
  <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
      <h2 style="color: #333; margin-bottom: 20px;">Password Reset Request</h2>
      <p style="color: #666; margin-bottom: 10px;">Dear {user.first_name or user.username},</p>
      <p style="color: #666; margin-bottom: 20px;">You requested a password reset. Your One-Time Password (OTP) is:</p>
      
      <div style="background-color: #f0f0f0; padding: 15px; border-left: 4px solid #2563eb; margin: 20px 0;">
        <h1 style="color: #2563eb; margin: 0; letter-spacing: 2px; font-size: 32px; text-align: center;">{otp_code}</h1>
      </div>
      
      <p style="color: #999; font-size: 12px; margin-top: 20px;">This OTP is valid for 15 minutes. Do not share this code with anyone.</p>
      <p style="color: #999; font-size: 12px;">If you did not request a password reset, please ignore this email.</p>
      <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
      <p style="color: #999; font-size: 11px; text-align: center;">HR Management System</p>
    </div>
  </body>
</html>
            """
            
            # Try to send email
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
                logger.info(f"[OTP Debug] Email sent successfully to {user.email}")
                SecurityAuditManager.log_password_change(
                    user, 
                    CustomTokenObtainPairView.get_client_ip(request),
                    'Password reset OTP sent'
                )
                
                return Response({
                    'message': 'Password reset OTP has been sent to your email address. Check your email for the OTP code.',
                    'status': 'success',
                    'expired_in_minutes': 15
                }, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"[OTP Debug] Failed to send password reset email to {user.email}: {str(e)}")
                return Response({
                    'message': 'Failed to send reset email. Please check your email settings and try again.',
                    'status': 'error',
                    'error_detail': 'Email service error'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Error in password reset request: {str(e)}")
            return Response({
                'message': 'An error occurred processing your request.',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Security: Don't reveal if user exists
    return Response({
        'message': 'If an account exists with this email/username, a password reset OTP has been sent to your email address.',
        'status': 'success',
        'expired_in_minutes': 15
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_reset_otp_and_reset_password(request):
    """
    Verify reset OTP and reset password.
    Expects: email or username, otp_code, new_password, confirm_password
    """
    email = request.data.get('email')
    username = request.data.get('username')
    otp_code = request.data.get('otp_code', '').strip()
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    
    from django.contrib.auth.models import User
    from django.utils import timezone
    from datetime import timedelta
    
    # Validate all required fields
    if not otp_code or not new_password or not confirm_password:
        return Response({
            'error': 'otp_code, new_password, and confirm_password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Find user
    user = None
    if email:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            pass
    elif username:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            pass
    
    if not user:
        return Response({
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Verify new passwords match
    if new_password != confirm_password:
        return Response({
            'error': 'New passwords do not match'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate password strength
    is_strong, strength_message = SecurityValidator.validate_password_strength(new_password)
    if not is_strong:
        return Response({
            'error': strength_message
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Verify OTP code (check in SecurityEventLog)
    # Look for the most recent password_reset_otp event
    otp_event = SecurityEventLog.objects.filter(
        user=user,
        event_type='password_reset_otp',
        created_at__gte=timezone.now() - timedelta(minutes=15)  # OTP valid for 15 minutes
    ).order_by('-created_at').first()
    
    if not otp_event:
        return Response({
            'error': 'OTP has expired or is invalid. Please request a new password reset OTP.'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Extract OTP from the description
    # Description format: "Password reset OTP: 123456"
    stored_otp = otp_event.description.split(': ')[-1]
    
    if stored_otp != otp_code:
        return Response({
            'error': 'Invalid OTP code'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Mark OTP as used
    otp_event.severity = 'low'
    otp_event.description = f'Password reset OTP verified: {otp_code}'
    otp_event.save()
    
    # Reset password
    user.set_password(new_password)
    user.save()
    
    SecurityAuditManager.log_password_change(
        user, 
        CustomTokenObtainPairView.get_client_ip(request),
        'Password reset via OTP'
    )
    
    return Response({
        'message': 'Password has been reset successfully. You can now login with your new password.',
        'status': 'success'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_security_report(request):
    """Get security report for the current user."""
    days = request.query_params.get('days', 30)
    try:
        days = int(days)
    except ValueError:
        days = 30
    
    report = SecurityAuditManager.get_security_report(request.user, days=days)
    
    return Response({
        'user': request.user.username,
        'days': days,
        'report': report
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_suspicious_activity(request):
    """Check for suspicious activity on user account."""
    suspicious = LoginSecurityManager.get_suspicious_patterns(request.user)
    
    return Response({
        'user': request.user.username,
        'suspicious_patterns': suspicious
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logout user and blacklist their tokens.
    For JWT, the client should discard the token.
    """
    ip_address = CustomTokenObtainPairView.get_client_ip(request)
    SecurityEventLog.objects.create(
        user=request.user,
        event_type='logout',
        ip_address=ip_address,
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        severity='low'
    )
    
    return Response({
        'message': 'You have been logged out successfully',
        'status': 'success'
    }, status=status.HTTP_200_OK)
