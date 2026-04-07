"""
Custom permission classes for role-based access control in REST API.
"""
from rest_framework.permissions import BasePermission
from .models import Employee


class IsAdmin(BasePermission):
    """Allow access only to Super Admin users."""
    message = "You do not have permission to perform this action. Super Admin access required."

    def has_permission(self, request, view):
        try:
            employee = Employee.objects.get(user=request.user)
            return employee.role == 'admin'
        except Employee.DoesNotExist:
            return False


class IsHRAdmin(BasePermission):
    """Allow access to HR Admin and Super Admin."""
    message = "You do not have permission to perform this action. HR Admin access required."

    def has_permission(self, request, view):
        try:
            employee = Employee.objects.get(user=request.user)
            return employee.role in ['admin', 'hradmin']
        except Employee.DoesNotExist:
            return False


class IsManager(BasePermission):
    """Allow access to Manager, HR Admin, and Super Admin."""
    message = "You do not have permission to perform this action. Manager access required."

    def has_permission(self, request, view):
        try:
            employee = Employee.objects.get(user=request.user)
            return employee.role in ['admin', 'hradmin', 'manager']
        except Employee.DoesNotExist:
            return False


class IsEmployee(BasePermission):
    """Allow access to all authenticated employees."""
    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsAdminOrReadOnly(BasePermission):
    """
    Allow Admin to create/update/delete.
    Others can only read.
    """
    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user and request.user.is_authenticated
        
        try:
            employee = Employee.objects.get(user=request.user)
            return employee.role == 'admin'
        except Employee.DoesNotExist:
            return False


class IsHRAdminOrReadOnly(BasePermission):
    """
    Allow HR Admin and Super Admin to create/update/delete.
    Others can only read.
    """
    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user and request.user.is_authenticated
        
        try:
            employee = Employee.objects.get(user=request.user)
            return employee.role in ['admin', 'hradmin']
        except Employee.DoesNotExist:
            return False


class IsOwnEmployee(BasePermission):
    """
    Allow users to access their own employee profile.
    Admins can access all.
    """
    message = "You can only access your own profile."

    def has_object_permission(self, request, view, obj):
        try:
            employee = Employee.objects.get(user=request.user)
            # Admin/HR Admin can access all, others can only access themselves
            if employee.role in ['admin', 'hradmin']:
                return True
            return obj.user == request.user
        except Employee.DoesNotExist:
            return False


class CanManageAttendance(BasePermission):
    """
    Allow HR Admin and Super Admin to manage attendance.
    Managers can view their team's attendance.
    Employees can only see their own.
    """
    message = "You do not have permission to manage attendance."

    def has_permission(self, request, view):
        try:
            employee = Employee.objects.get(user=request.user)
            # Admins can always manage
            if employee.role in ['admin', 'hradmin']:
                return True
            # Managers can view/manage
            if employee.role == 'manager':
                return True
            # Employees can view their own
            if employee.role == 'employee':
                return request.method in ['GET']
            return False
        except Employee.DoesNotExist:
            return False


class CanManageLeave(BasePermission):
    """
    Allow employees to request leave.
    Managers can approve/reject team leaves.
    HR Admin and Super Admin can manage all leaves.
    """
    message = "You do not have permission to manage leaves."

    def has_permission(self, request, view):
        try:
            employee = Employee.objects.get(user=request.user)
            return True  # All employees can access leave endpoints
        except Employee.DoesNotExist:
            return False


class CanViewSalary(BasePermission):
    """
    Allow employees to view their own salary slips.
    Managers can view their team's salary.
    HR Admin and Super Admin can view all.
    """
    message = "You do not have permission to view salary information."

    def has_permission(self, request, view):
        try:
            employee = Employee.objects.get(user=request.user)
            return True  # All employees can access
        except Employee.DoesNotExist:
            return False
