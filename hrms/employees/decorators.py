"""
Custom decorators for role-based access control in Django views.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Employee


def get_user_role(user):
    """Helper function to get the role of a user."""
    try:
        employee = Employee.objects.get(user=user)
        return employee.role
    except Employee.DoesNotExist:
        return None


def admin_required(view_func):
    """
    Decorator to restrict access to Super Admin only.
    Redirects to home page or shows 403 error for unauthorized users.
    """
    @wraps(view_func)
    @login_required(login_url='home')
    def wrapper(request, *args, **kwargs):
        role = get_user_role(request.user)
        if role == 'admin':
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("You do not have permission to access this page. Super Admin access required.")
    return wrapper


def hr_admin_required(view_func):
    """
    Decorator to restrict access to HR Admin and Super Admin.
    """
    @wraps(view_func)
    @login_required(login_url='home')
    def wrapper(request, *args, **kwargs):
        role = get_user_role(request.user)
        if role in ['admin', 'hradmin']:
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("You do not have permission to access this page. HR Admin access required.")
    return wrapper


def manager_required(view_func):
    """
    Decorator to restrict access to Manager, HR Admin, and Super Admin.
    """
    @wraps(view_func)
    @login_required(login_url='home')
    def wrapper(request, *args, **kwargs):
        role = get_user_role(request.user)
        if role in ['admin', 'hradmin', 'manager']:
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("You do not have permission to access this page. Manager access required.")
    return wrapper


def employee_required(view_func):
    """
    Decorator to ensure user is authenticated (all employees).
    """
    @wraps(view_func)
    @login_required(login_url='home')
    def wrapper(request, *args, **kwargs):
        try:
            Employee.objects.get(user=request.user)
            return view_func(request, *args, **kwargs)
        except Employee.DoesNotExist:
            return HttpResponseForbidden("Employee profile not found.")
    return wrapper


def role_required(*allowed_roles):
    """
    Flexible decorator to restrict access to specific roles.
    Usage: @role_required('admin', 'hradmin')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required(login_url='home')
        def wrapper(request, *args, **kwargs):
            role = get_user_role(request.user)
            if role in allowed_roles:
                return view_func(request, *args, **kwargs)
            roles_text = ', '.join(allowed_roles).upper()
            return HttpResponseForbidden(f"You do not have permission to access this page. Required roles: {roles_text}")
        return wrapper
    return decorator


def get_permission_context(request):
    """
    Helper function to get permission context for templates.
    Add to view context to check permissions in templates.
    
    Returns:
        dict: Dictionary with permission flags
    Example:
        context = get_permission_context(request)
        # context = {
        #     'is_admin': True,
        #     'is_hr_admin': True,
        #     'is_manager': False,
        #     'is_employee': True,
        #     'user_role': 'admin'
        # }
    """
    role = get_user_role(request.user)
    
    return {
        'user_role': role,
        'is_admin': role == 'admin',
        'is_hr_admin': role in ['admin', 'hradmin'],
        'is_manager': role in ['admin', 'hradmin', 'manager'],
        'is_employee': role in ['admin', 'hradmin', 'manager', 'employee'],
        'can_manage_all': role in ['admin', 'hradmin'],
        'can_manage_team': role in ['admin', 'hradmin', 'manager'],
    }
