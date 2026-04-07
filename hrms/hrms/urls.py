"""
URL configuration for hrms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from employees import views

urlpatterns = [
    path('', views.home, name='home'),
    path('design/', views.design_template, name='design_template'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.employee_profile, name='employee_profile'),
    path('leave-requests/', views.employee_leave_requests, name='employee_leave_requests'),
    path('request-leave/', views.employee_request_leave, name='employee_request_leave'),
    path('attendance/', views.employee_attendance, name='employee_attendance'),
    path('salary-slips/', views.employee_salary_slips, name='employee_salary_slips'),
    path('documents/', views.employee_documents, name='employee_documents'),
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # User Management
    path('users/add/', views.add_user, name='add_user'),
    path('users/<int:pk>/update/', views.update_user, name='update_user'),
    path('users/<int:pk>/delete/', views.delete_user, name='delete_user'),
    
    # Mobile App
    path('mobile/check-in/', views.mobile_checkin, name='mobile_checkin'),
    
    # Mobile App API endpoints
    path('api/', include('employees.urls_api')),
    
    path('admin/', admin.site.urls),
]

