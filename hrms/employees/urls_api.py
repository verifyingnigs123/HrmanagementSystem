from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import api_views, auth_views

app_name = 'api'

urlpatterns = [
    # JWT Authentication Endpoints
    path('auth/jwt/token/', auth_views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/jwt/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Legacy mobile login (Session-based)
    path('auth/login/', api_views.mobile_login, name='mobile_login'),
    
    # 2FA Endpoints
    path('auth/2fa/setup/', auth_views.setup_2fa, name='setup_2fa'),
    path('auth/2fa/verify-setup/', auth_views.verify_2fa_setup, name='verify_2fa_setup'),
    path('auth/2fa/verify/', auth_views.verify_2fa_token, name='verify_2fa_token'),
    path('auth/2fa/disable/', auth_views.disable_2fa, name='disable_2fa'),
    path('auth/2fa/status/', auth_views.get_2fa_status, name='get_2fa_status'),
    
    # Password Management
    path('auth/password/change/', auth_views.change_password, name='change_password'),
    path('auth/password/reset-request/', auth_views.reset_password_request, name='reset_password_request'),
    path('auth/password/verify-reset-otp/', auth_views.verify_reset_otp_and_reset_password, name='verify_reset_otp'),
    
    # Logout
    path('auth/logout/', auth_views.logout, name='logout'),
    
    # Security Endpoints
    path('security/report/', auth_views.get_security_report, name='get_security_report'),
    path('security/suspicious-activity/', auth_views.get_suspicious_activity, name='get_suspicious_activity'),
    
    # Attendance endpoints
    path('attendance/today/', api_views.get_today_attendance, name='get_today_attendance'),
    path('attendance/check-in/', api_views.check_in, name='check_in'),
    path('attendance/check-out/', api_views.check_out, name='check_out'),
    path('attendance/history/', api_views.get_attendance_history, name='get_attendance_history'),
    
    # Employee profile
    path('employee/profile/', api_views.get_employee_profile, name='get_employee_profile'),
]
