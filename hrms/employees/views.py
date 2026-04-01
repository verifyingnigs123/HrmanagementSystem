from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from .models import Employee

@never_cache
def home(request):
    """Home/Login page - handles user authentication and redirects to dashboard."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    error_message = None
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            # Authentication failed - set error message
            error_message = 'Invalid username or password'
    
    return render(request, 'login.html', {'error_message': error_message})

@never_cache
@login_required(login_url='admin:login')
def dashboard(request):
    """Unified dashboard - shows different content based on user role."""
    try:
        employee = Employee.objects.get(user=request.user)
        role = employee.role
        
        # Prepare common context data needed by all dashboards
        context = {
            'role': role,
            'employee': employee,
            'total_employees': Employee.objects.count(),
            'active_employees': Employee.objects.filter(is_active=True).count(),
        }
        
        # Add role-specific data
        if role == 'admin':
            # Admin sees dashboard + statistics
            total_users = Employee.objects.values('user').distinct().count()
            departments = Employee.objects.values_list('department', flat=True).distinct().count()
            
            role_distribution = {}
            for role_choice, label in [('admin', 'Admin'), ('hradmin', 'HR Admin'), ('manager', 'Manager'), ('employee', 'Employee')]:
                role_distribution[label] = Employee.objects.filter(role=role_choice).count()
            
            context.update({
                'is_admin': True,
                'total_users': total_users,
                'total_departments': departments,
                'role_distribution': role_distribution,
                'all_employees': Employee.objects.select_related('user').all(),
            })
            
        elif role == 'hradmin':
            context['new_employees'] = Employee.objects.all().order_by('-hire_date')[:5]
            context['departments'] = list(Employee.objects.values_list('department', flat=True).distinct())
            context['all_employees'] = Employee.objects.select_related('user').all()
            
        elif role == 'manager':
            team_members = Employee.objects.filter(department=employee.department).exclude(user=request.user)
            context.update({
                'department': employee.department,
                'position': employee.position,
                'team_members': team_members,
                'team_count': team_members.count(),
            })
        
        return render(request, 'dashboard/dashboard.html', context)
    except Employee.DoesNotExist:
        return redirect('home')

@never_cache
@login_required(login_url='admin:login')
def employee_list(request):
    """List all employees with admin management features."""
    try:
        user_employee = Employee.objects.get(user=request.user)
        user_role = user_employee.role
    except Employee.DoesNotExist:
        return redirect('home')
    
    employees = Employee.objects.select_related('user').all()
    
    # Filter by role if parameter is provided
    role_filter = request.GET.get('role')
    if role_filter and role_filter in ['admin', 'hradmin', 'manager', 'employee']:
        employees = employees.filter(role=role_filter)
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter == 'active':
        employees = employees.filter(is_active=True)
    elif status_filter == 'inactive':
        employees = employees.filter(is_active=False)
    
    # Filter by department
    department_filter = request.GET.get('department')
    if department_filter:
        employees = employees.filter(department=department_filter)
    
    # Get all departments for filter dropdown
    departments = Employee.objects.values_list('department', flat=True).distinct()
    
    context = {
        'employees': employees,
        'departments': departments,
        'user_role': user_role,
        'can_manage': user_role in ['admin', 'hradmin'],
        'current_role_filter': role_filter,
        'current_status_filter': status_filter,
        'current_department_filter': department_filter,
    }
    
    return render(request, 'employees/employee_list.html', context)

@never_cache
@login_required(login_url='admin:login')
def employee_detail(request, pk):
    """View employee details."""
    employee = Employee.objects.get(pk=pk)
    context = {'employee': employee}
    return render(request, 'employees/employee_detail.html', context)

@never_cache
def forgot_password(request):
    """Forgot password page - allows users to request password reset."""
    success_message = None
    error_message = None
    
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # Check if email exists in system
        try:
            from django.contrib.auth.models import User
            user = User.objects.get(email=email)
            success_message = 'Password reset instructions have been sent to your email address.'
            # Note: In a production system, you would send an actual email with a reset link
            # For now, we just show the success message
        except User.DoesNotExist:
            error_message = 'No user account found with this email address.'
    
    context = {
        'success_message': success_message,
        'error_message': error_message,
    }
    return render(request, 'forgot_password.html', context)
