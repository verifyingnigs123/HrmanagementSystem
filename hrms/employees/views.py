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
@login_required(login_url='home')
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
@login_required(login_url='home')
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
@login_required(login_url='home')
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


@never_cache
@login_required(login_url='home')
def employee_profile(request):
    """View and edit employee profile."""
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return redirect('home')
    
    context = {
        'employee': employee,
        'user': request.user,
    }
    return render(request, 'employees/profile.html', context)

@never_cache
@login_required(login_url='home')
def employee_leave_requests(request):
    """View all leave requests for the employee."""
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return redirect('home')
    
    context = {
        'employee': employee,
        'user': request.user,
    }
    return render(request, 'employees/leave_requests.html', context)

@never_cache
@login_required(login_url='home')
def employee_request_leave(request):
    """Request a new leave."""
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return redirect('home')
    
    context = {
        'employee': employee,
        'user': request.user,
    }
    return render(request, 'employees/request_leave.html', context)

@never_cache
@login_required(login_url='home')
def employee_attendance(request):
    """View attendance records for the employee."""
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return redirect('home')
    
    context = {
        'employee': employee,
        'user': request.user,
    }
    return render(request, 'employees/attendance.html', context)

@never_cache
@login_required(login_url='home')
def employee_salary_slips(request):
    """View salary slips for the employee."""
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return redirect('home')
    
    context = {
        'employee': employee,
        'user': request.user,
    }
    return render(request, 'employees/salary_slips.html', context)

@never_cache
@login_required(login_url='home')
def employee_documents(request):
    """View documents for the employee."""
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return redirect('home')
    
    context = {
        'employee': employee,
        'user': request.user,
    }
    return render(request, 'employees/documents.html', context)

@login_required(login_url='home')
def mobile_checkin(request):
    """Mobile check-in page with GPS support."""
    return render(request, 'mobile_checkin.html')

def pwa_manifest(request):
    """PWA Manifest for mobile app installation."""
    import json
    manifest = {
        "name": "HRMS Check-in",
        "short_name": "Check-in",
        "description": "Employee attendance check-in with GPS tracking",
        "start_url": "/mobile/check-in/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#1877f2",
        "orientation": "portrait-primary",
        "icons": [
            {
                "src": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 192 192'%3E%3Ccircle cx='96' cy='96' r='96' fill='%231877f2'/%3E%3Ctext x='50%25' y='50%25' text-anchor='middle' dy='.3em' fill='white' font-size='96' font-weight='bold' font-family='Arial'%3EHI%3C/text%3E%3C/svg%3E",
                "sizes": "192x192",
                "type": "image/svg+xml",
                "purpose": "any"
            },
            {
                "src": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'%3E%3Ccircle cx='256' cy='256' r='256' fill='%231877f2'/%3E%3Ctext x='50%25' y='50%25' text-anchor='middle' dy='.3em' fill='white' font-size='256' font-weight='bold' font-family='Arial'%3EHI%3C/text%3E%3C/svg%3E",
                "sizes": "512x512",
                "type": "image/svg+xml",
                "purpose": "any maskable"
            }
        ]
    }
    return response_json(manifest, content_type='application/manifest+json')

def service_worker(request):
    """Service Worker for offline support."""
    sw_js = """
const CACHE_NAME = 'hrms-checkin-v1';
const urlsToCache = [
  '/',
  '/mobile/check-in/',
  '/static/css/style.css',
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          return response;
        }
        return fetch(event.request).then(response => {
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }
          const responseToCache = response.clone();
          caches.open(CACHE_NAME)
            .then(cache => {
              cache.put(event.request, responseToCache);
            });
          return response;
        });
      })
      .catch(() => {
        return caches.match('/');
      })
  );
});
"""
    from django.http import HttpResponse
    response = HttpResponse(sw_js, content_type='application/javascript')
    response['Service-Worker-Allowed'] = '/'
    return response

from django.http import JsonResponse

def response_json(data, content_type='application/json'):
    """Return JSON response."""
    import json
    from django.http import HttpResponse
    return HttpResponse(
        json.dumps(data),
        content_type=content_type
    )

