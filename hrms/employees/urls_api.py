from django.urls import path
from . import api_views

app_name = 'api'

urlpatterns = [
    # Authentication
    path('auth/login/', api_views.mobile_login, name='mobile_login'),
    
    # Attendance endpoints
    path('attendance/today/', api_views.get_today_attendance, name='get_today_attendance'),
    path('attendance/check-in/', api_views.check_in, name='check_in'),
    path('attendance/check-out/', api_views.check_out, name='check_out'),
    path('attendance/history/', api_views.get_attendance_history, name='get_attendance_history'),
    
    # Employee profile
    path('employee/profile/', api_views.get_employee_profile, name='get_employee_profile'),
]
