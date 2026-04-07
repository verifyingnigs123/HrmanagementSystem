# Authorization & Permissions System

## Overview

This HR Management System implements a comprehensive role-based access control (RBAC) system with 4 permission levels:

1. **Super Admin (admin)** - Full system access
2. **HR Admin (hradmin)** - HR functions (employee management, attendance, payroll)
3. **Manager (manager)** - Team management capabilities
4. **Employee (employee)** - Self-service access only

## Role Hierarchy

```
Super Admin
├── Can access all features
├── Can manage all users and data
└── Can configure system settings

HR Admin
├── Can manage employees (view, create, update)
├── Can manage attendance records
├── Can manage leave requests
├── Can view payroll and salary slips
└── Can manage departments

Manager
├── Can view team member details
├── Can approve/manage team attendance
├── Can approve/reject team leave requests
└── Cannot modify system settings

Employee
├── Can view own profile
├── Can check in/out attendance
├── Can request leaves
├── Can view own salary slips
└── Can view own documents
```

## Using the Permission System

### 1. In Django Views (Function-Based Views)

#### Using Decorators

```python
from .decorators import (
    admin_required, 
    hr_admin_required, 
    manager_required, 
    employee_required,
    role_required
)

# Super Admin only
@admin_required
def admin_settings(request):
    return render(request, 'admin_settings.html')

# HR Admin or Super Admin
@hr_admin_required
def manage_employees(request):
    return render(request, 'manage_employees.html')

# Manager, HR Admin, or Super Admin
@manager_required
def team_management(request):
    return render(request, 'team_management.html')

# Any authenticated employee
@employee_required
def my_profile(request):
    return render(request, 'profile.html')

# Custom roles
@role_required('admin', 'hradmin')
def sensitive_operation(request):
    return render(request, 'sensitive.html')
```

#### Getting Permission Context in View

```python
from .decorators import get_permission_context

def my_view(request):
    # Get permission flags for template use
    context = get_permission_context(request)
    # Returns:
    # {
    #     'user_role': 'admin',
    #     'is_admin': True,
    #     'is_hr_admin': True,
    #     'is_manager': True,
    #     'is_employee': True,
    #     'can_manage_all': True,
    #     'can_manage_team': True,
    # }
    return render(request, 'template.html', context)
```

### 2. In REST API Views

#### Using Permission Classes

```python
from rest_framework.decorators import api_view, permission_classes
from .permissions import (
    IsAdmin,
    IsHRAdmin,
    IsManager,
    IsEmployee,
    IsOwnEmployee,
    CanManageAttendance,
    CanManageLeave,
    CanViewSalary
)

# Super Admin only
@api_view(['POST'])
@permission_classes([IsAdmin])
def create_user(request):
    # Only super admin can create users
    pass

# HR Admin or Super Admin
@api_view(['GET', 'PUT'])
@permission_classes([IsHRAdmin])
def manage_employees_api(request):
    # Only HR Admin and Super Admin can access
    pass

# Manager, HR Admin, or Super Admin
@api_view(['GET'])
@permission_classes([IsManager])
def view_team_attendance(request):
    # Managers can view team, HR Admin/Admin can view all
    pass

# All authenticated employees
@api_view(['GET'])
@permission_classes([IsEmployee])
def my_attendance(request):
    # All employees can access
    pass

# Multiple permissions (all must pass)
@api_view(['GET', 'POST'])
@permission_classes([IsHRAdmin, CanManageAttendance])
def manage_attendance_api(request):
    pass

# Permission or condition
@api_view(['GET', 'PUT'])
@permission_classes([IsOwnEmployee])
def view_own_profile_api(request):
    # Users can view own profile, admins can view all
    pass
```

### 3. In Templates

Use the permission context flags in templates:

```html
<!-- Check if user is admin -->
{% if is_admin %}
    <a href="/admin/settings/">Admin Settings</a>
{% endif %}

<!-- Check if user can manage -->
{% if can_manage_all %}
    <button>Manage All Employees</button>
{% elif can_manage_team %}
    <button>Manage Team</button>
{% endif %}

<!-- Show different content based on role -->
{% if user_role == 'admin' %}
    <div>System Administration Panel</div>
{% elif user_role == 'hradmin' %}
    <div>HR Administration Panel</div>
{% elif user_role == 'manager' %}
    <div>Team Management Dashboard</div>
{% else %}
    <div>Employee Self-Service Portal</div>
{% endif %}
```

## Adding Permissions to New Views/Endpoints

### Step 1: Identify Required Permission Level

Based on the action, determine the minimum role:
- **Super Admin**: System configuration, user creation/deletion
- **HR Admin**: Employee management, attendance, payroll
- **Manager**: Team viewing, team attendance/leave management
- **Employee**: Self-service operations

### Step 2: Add Authorization

#### For Function-Based Views:
```python
from .decorators import hr_admin_required, get_permission_context

@hr_admin_required
def new_hr_function(request):
    context = get_permission_context(request)
    # Implementation
    return render(request, 'template.html', context)
```

#### For API Views:
```python
from rest_framework.decorators import api_view, permission_classes
from .permissions import IsHRAdmin

@api_view(['POST'])
@permission_classes([IsHRAdmin])
def new_api_endpoint(request):
    # Implementation
    pass
```

## Testing Permissions

### Test Different Roles

1. Create test users with different roles:
```bash
python manage.py shell
from django.contrib.auth.models import User
from employees.models import Employee

# Create Super Admin
admin_user = User.objects.create_user(
    username='admin',
    email='admin@example.com',
    password='testpass123',
    first_name='Admin',
    last_name='User'
)
Employee.objects.create(user=admin_user, role='admin', employee_id='ADM001')

# Create HR Admin
hr_user = User.objects.create_user(
    username='hrmanager',
    email='hr@example.com',
    password='testpass123',
    first_name='HR',
    last_name='Manager'
)
Employee.objects.create(user=hr_user, role='hradmin', employee_id='HR001')
```

2. Test access by logging in as each role and checking:
   - Which pages are accessible
   - Which API endpoints work
   - Which actions are allowed/blocked

## Permission Errors

When a user attempts unauthorized access:

**Web Views**: Returns HTTP 403 Forbidden with message
```
You do not have permission to access this page. [Role] access required.
```

**API Endpoints**: Returns JSON error response
```json
{
    "detail": "You do not have permission to perform this action. [Role] access required."
}
```

## Best Practices

1. **Always add permission checks** to sensitive endpoints
2. **Use appropriate decorator/permission** for your needs
3. **Add context to templates** using `get_permission_context()`
4. **Check role manually** only when decorator isn't suitable
5. **Audit access** using AuditLog model for sensitive operations
6. **Test permissions** thoroughly for each role
7. **Validate in API views** that returned data matches user's role capability

## Common Patterns

### Allow Edit Only for Owner or Admin
```python
@employee_required
def edit_profile(request, pk):
    employee = Employee.objects.get(pk=pk)
    user_emp = Employee.objects.get(user=request.user)
    
    # Allow if own profile or admin
    if employee.user != request.user and user_emp.role not in ['admin', 'hradmin']:
        return HttpResponseForbidden("Cannot edit other employee's profile")
    
    # Process form...
```

### Show Different Data Based on Role
```python
@employee_required
def view_attendance(request):
    user_emp = Employee.objects.get(user=request.user)
    
    if user_emp.role == 'admin':
        # Admin sees all attendance
        attendance = Attendance.objects.all()
    elif user_emp.role == 'manager':
        # Manager sees team attendance
        attendance = Attendance.objects.filter(employee__department=user_emp.department)
    else:
        # Employee sees only own
        attendance = Attendance.objects.filter(employee=user_emp)
```

## Migration Guide

If adding roles to existing project:

1. **Create test data**:
   ```bash
   python manage.py populate_sample_data
   ```

2. **Update all sensitive views** with permission decorators

3. **Update all API endpoints** with permission classes

4. **Test thoroughly** with different roles

5. **Monitor access logs** after deployment

6. **Adjust permissions** based on feedback
