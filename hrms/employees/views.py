from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_http_methods
from .models import Employee

def home(request):
    """Home/Login page - handles user authentication and redirects to dashboard."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            # Authentication failed - show error and re-render form
            from django import forms
            form = forms.Form()
            form.add_error(None, 'Invalid username or password')
            return render(request, 'home.html', {'form': form})
    
    return render(request, 'home.html')

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
            role_counts = {}
            for role_choice, label in [('admin', 'Admin'), ('hradmin', 'HR Admin'), ('manager', 'Manager'), ('employee', 'Employee')]:
                role_counts[label] = Employee.objects.filter(role=role_choice).count()
            context['role_counts'] = role_counts
            
        elif role == 'hradmin':
            context['new_employees'] = Employee.objects.all().order_by('-hire_date')[:5]
            context['departments'] = list(Employee.objects.values_list('department', flat=True).distinct())
            
        elif role == 'manager':
            team_members = Employee.objects.filter(department=employee.department).exclude(user=request.user)
            context.update({
                'department': employee.department,
                'position': employee.position,
                'team_members': team_members,
                'team_count': team_members.count(),
            })
        
        return render(request, 'employees/dashboard.html', context)
    except Employee.DoesNotExist:
        return redirect('home')

@login_required(login_url='admin:login')
def employee_list(request):
    """List all employees."""
    employees = Employee.objects.select_related('user').all()
    context = {'employees': employees}
    return render(request, 'employees/employee_list.html', context)

@login_required(login_url='admin:login')
def employee_detail(request, pk):
    """View employee details."""
    employee = Employee.objects.get(pk=pk)
    context = {'employee': employee}
    return render(request, 'employees/employee_detail.html', context)


