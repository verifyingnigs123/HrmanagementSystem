from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.db import models
from django.http import HttpResponseForbidden
import logging

logger = logging.getLogger(__name__)
from .models import (
    Employee, Attendance, LeaveRequest, LeaveType, 
    SalarySlip, Document, AttendancePolicy, AuditLog, SecurityEventLog
)
from .decorators import (
    admin_required, hr_admin_required, manager_required, 
    employee_required, get_permission_context
)

def design_template(request):
    """Design template showcase - for copying UI design."""
    return render(request, 'design_template.html')

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
@employee_required
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
        
        # Add permission context for template
        context.update(get_permission_context(request))
        
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
@hr_admin_required
def employee_list(request):
    """List all employees with admin management features - HR Admin and Super Admin only."""
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
    context.update(get_permission_context(request))
    
    return render(request, 'employees/employee_list.html', context)

@never_cache
@employee_required
def employee_detail(request, pk):
    """View employee details - users can view self, admins can view all."""
    employee = Employee.objects.get(pk=pk)
    
    # Check if user has permission to view this employee
    try:
        user_employee = Employee.objects.get(user=request.user)
        # Allow viewing if it's their own profile or if they're admin/hr_admin
        if employee.user != request.user and user_employee.role not in ['admin', 'hradmin']:
            return HttpResponseForbidden("You do not have permission to view this employee's details.")
    except Employee.DoesNotExist:
        return HttpResponseForbidden("Employee profile not found.")
    
    context = {
        'employee': employee,
        'is_own_profile': employee.user == request.user,
    }
    context.update(get_permission_context(request))
    return render(request, 'employees/employee_detail.html', context)

@never_cache
def forgot_password(request):
    """Forgot password page - allows users to request password reset."""
    error_message = None
    success_message = None
    email = ''
    
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # Check if email exists in system and send OTP
        try:
            from django.contrib.auth.models import User
            from django.core.mail import send_mail
            from django.conf import settings
            import secrets
            import string
            
            user = User.objects.get(email=email)
            
            # Generate 6-digit OTP
            otp_code = ''.join(secrets.choice(string.digits) for _ in range(6))
            
            # Store OTP in SecurityEventLog temporarily
            otp_event = SecurityEventLog.objects.create(
                user=user,
                event_type='password_reset_otp',
                description=f'Password reset OTP: {otp_code}',
                severity='medium',
                ip_address=request.META.get('REMOTE_ADDR', ''),
            )
            
            print(f"[OTP Debug] Generated OTP for {user.email}: {otp_code}")
            
            # Send email with OTP - clean formatting
            subject = 'Password Reset Request - Your OTP Code'
            message = f"Dear {user.first_name or user.username},\n\nYou requested a password reset.\n\nYour One-Time Password (OTP) is:\n\n{otp_code}\n\nThis OTP is valid for 15 minutes. Do not share this code with anyone.\n\nIf you did not request a password reset, please ignore this email.\n\n---\nHR Management System"
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
                
                print(f"[OTP Debug] Email sent successfully to {user.email}")
                logger.info(f"Password reset OTP email sent to {user.email}")
                
                # Redirect to verify OTP page
                return redirect(f'/verify-otp/?email={email}')
                
            except Exception as e:
                print(f"[OTP Debug] Email Error: {str(e)}")
                logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
                error_message = f'Failed to send email. Please try again or contact support.'
                
        except User.DoesNotExist:
            # Don't reveal if email exists (security) - show as success message
            print(f"[OTP Debug] Email not found: {email}")
            success_message = 'If an account exists with that email, a password reset OTP has been sent. Please check your email.'
        except Exception as e:
            print(f"[OTP Debug] Unexpected Error: {str(e)}")
            logger.error(f"Error in password reset request: {str(e)}")
            error_message = f'An error occurred. Please try again.'
    
    context = {
        'error_message': error_message,
        'success_message': success_message,
        'email': email,
    }
    return render(request, 'forgot_password.html', context)


@never_cache
def verify_otp(request):
    """Verify OTP and reset password."""
    success_message = None
    error_message = None
    email = request.GET.get('email', '')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        otp_code = request.POST.get('otp_code', '').strip()
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        from django.contrib.auth.models import User
        from django.utils import timezone
        from datetime import timedelta
        from .security_utils import SecurityValidator
        
        # Validate all required fields
        if not otp_code or not new_password or not confirm_password:
            error_message = 'All fields are required'
        elif new_password != confirm_password:
            error_message = 'Passwords do not match'
        else:
            # Validate password strength
            is_strong, strength_message = SecurityValidator.validate_password_strength(new_password)
            if not is_strong:
                error_message = strength_message
            else:
                # Find user
                try:
                    user = User.objects.get(email=email)
                    
                    # Verify OTP
                    otp_event = SecurityEventLog.objects.filter(
                        user=user,
                        event_type='password_reset_otp',
                        created_at__gte=timezone.now() - timedelta(minutes=15)
                    ).order_by('-created_at').first()
                    
                    if not otp_event:
                        error_message = 'OTP has expired. Please request a new password reset.'
                    else:
                        # Extract OTP from description
                        stored_otp = otp_event.description.split(': ')[-1]
                        
                        if stored_otp != otp_code:
                            error_message = 'Invalid OTP code'
                        else:
                            # Reset password
                            user.set_password(new_password)
                            user.save()
                            
                            # Mark OTP as used
                            otp_event.severity = 'low'
                            otp_event.save()
                            
                            # Log the password reset
                            SecurityEventLog.objects.create(
                                user=user,
                                event_type='password_reset_successful',
                                description='Password successfully reset via OTP verification',
                                severity='medium'
                            )
                            
                            success_message = 'Password has been reset successfully! You can now login with your new password.'
                            email = ''  # Clear email after successful reset
                            
                except User.DoesNotExist:
                    error_message = 'User not found'
    
    context = {
        'success_message': success_message,
        'error_message': error_message,
        'email': email,
    }
    return render(request, 'verify_otp.html', context)


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
    
    # Fetch leave requests for this employee
    leave_requests = LeaveRequest.objects.filter(employee=employee).select_related('leave_type', 'approved_by')
    
    # Calculate leave summary
    leave_types = LeaveType.objects.filter(is_active=True)
    leave_summary = []
    for leave_type in leave_types:
        allocated = leave_type.max_days_per_year
        used = LeaveRequest.objects.filter(
            employee=employee,
            leave_type=leave_type,
            status__in=['approved', 'pending']
        ).aggregate(total_days=models.Sum('number_of_days'))['total_days'] or 0
        
        leave_summary.append({
            'type': leave_type.name,
            'allocated': allocated,
            'used': used,
            'available': allocated - used,
            'pending': LeaveRequest.objects.filter(employee=employee, leave_type=leave_type, status='pending').count()
        })
    
    context = {
        'employee': employee,
        'user': request.user,
        'leave_requests': leave_requests,
        'leave_summary': leave_summary,
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
    
    # Get available leave types
    leave_types = LeaveType.objects.filter(is_active=True)
    
    context = {
        'employee': employee,
        'user': request.user,
        'leave_types': leave_types,
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
    
    # Fetch attendance records for this employee (last 30 days)
    from datetime import timedelta
    from django.utils import timezone
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    attendance_records = Attendance.objects.filter(
        employee=employee,
        date__gte=thirty_days_ago
    ).order_by('-date')
    
    # Calculate attendance statistics
    total_records = Attendance.objects.filter(employee=employee).count()
    present = Attendance.objects.filter(employee=employee, status='present').count()
    absent = Attendance.objects.filter(employee=employee, status='absent').count()
    late = Attendance.objects.filter(employee=employee, status='late').count()
    
    context = {
        'employee': employee,
        'user': request.user,
        'attendance_records': attendance_records,
        'stats': {
            'total': total_records,
            'present': present,
            'absent': absent,
            'late': late,
            'percentage': round((present / total_records * 100), 2) if total_records > 0 else 0,
        }
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
    
    # Fetch salary slips for this employee
    salary_slips = SalarySlip.objects.filter(employee=employee).order_by('-month')
    
    # Calculate salary summary
    ytd_salary = salary_slips.aggregate(total=models.Sum('net_salary'))['total'] or 0
    ytd_tax = salary_slips.aggregate(total=models.Sum('deductions'))['total'] or 0
    current_month_slip = salary_slips.first()
    
    context = {
        'employee': employee,
        'user': request.user,
        'salary_slips': salary_slips,
        'ytd_salary': ytd_salary,
        'ytd_tax': ytd_tax,
        'current_month_slip': current_month_slip,
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
    
    # Fetch documents for this employee
    documents = Document.objects.filter(employee=employee).order_by('-created_at')
    
    # Group documents by category
    doc_categories = {}
    for category_value, category_name in Document.DOCUMENT_CATEGORY_CHOICES:
        doc_categories[category_name] = documents.filter(category=category_value)
    
    context = {
        'employee': employee,
        'user': request.user,
        'documents': documents,
        'doc_categories': doc_categories,
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


@login_required(login_url='home')
@require_http_methods(["POST"])
def add_user(request):
    """Add a new user to the system."""
    from .forms import UserCreationForm
    from django.contrib.auth.models import User
    
    try:
        user_employee = Employee.objects.get(user=request.user)
        user_role = user_employee.role
        
        # Check if user has permission to add users
        if user_role not in ['admin', 'hradmin']:
            return JsonResponse({
                'success': False,
                'message': 'You do not have permission to add users.'
            }, status=403)
        
        form = UserCreationForm(request.POST)
        if form.is_valid():
            employee = form.save()
            return JsonResponse({
                'success': True,
                'message': f'User {employee.user.first_name} {employee.user.last_name} added successfully!',
                'employee_id': employee.id,
                'redirect': request.POST.get('next', '/employees/')
            })
        else:
            errors = {field: error[0] for field, error in form.errors.items()}
            return JsonResponse({
                'success': False,
                'message': 'Form validation failed.',
                'errors': errors
            }, status=400)
    
    except Employee.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Employee profile not found.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error adding user: {str(e)}'
        }, status=500)


@login_required(login_url='home')
@require_http_methods(["POST"])
def update_user(request, pk):
    """Update an existing user."""
    from .forms import UserUpdateForm
    
    try:
        user_employee = Employee.objects.get(user=request.user)
        user_role = user_employee.role
        
        # Check if user has permission to update users
        if user_role not in ['admin', 'hradmin']:
            return JsonResponse({
                'success': False,
                'message': 'You do not have permission to update users.'
            }, status=403)
        
        employee = Employee.objects.get(pk=pk)
        user = employee.user
        
        form = UserUpdateForm(request.POST)
        if form.is_valid():
            employee = form.save(user, employee)
            return JsonResponse({
                'success': True,
                'message': f'User {employee.user.first_name} {employee.user.last_name} updated successfully!',
                'employee_id': employee.id
            })
        else:
            errors = {field: error[0] for field, error in form.errors.items()}
            return JsonResponse({
                'success': False,
                'message': 'Form validation failed.',
                'errors': errors
            }, status=400)
    
    except Employee.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Employee not found.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating user: {str(e)}'
        }, status=500)


@login_required(login_url='home')
@require_http_methods(["POST"])
def delete_user(request, pk):
    """Delete a user from the system."""
    try:
        user_employee = Employee.objects.get(user=request.user)
        user_role = user_employee.role
        
        # Check if user has permission to delete users
        if user_role not in ['admin', 'hradmin']:
            return JsonResponse({
                'success': False,
                'message': 'You do not have permission to delete users.'
            }, status=403)
        
        employee = Employee.objects.get(pk=pk)
        user = employee.user
        user_name = f"{user.first_name} {user.last_name}"
        
        # Delete the user and employee
        user.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'User {user_name} deleted successfully!'
        })
    
    except Employee.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Employee not found.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting user: {str(e)}'
        }, status=500)

