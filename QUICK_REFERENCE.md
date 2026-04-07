# Quick Reference: Role-Based Authorization

## 4 User Roles

```
🔴 ADMIN (Super Admin)        - Full system access
🟡 HRADMIN (HR Admin)         - HR functions + employee management
🟠 MANAGER (Team Manager)     - Team management only
🟢 EMPLOYEE (Self-Service)    - Own records only
```

## Quick Usage

### Protect a Django View
```python
from .decorators import admin_required
# OR: hr_admin_required, manager_required, employee_required

@admin_required
def sensitive_view(request):
    return render(request, 'template.html')
```

### Protect an API Endpoint
```python
from rest_framework.decorators import api_view, permission_classes
from .permissions import IsHRAdmin

@api_view(['GET', 'POST'])
@permission_classes([IsHRAdmin])
def api_endpoint(request):
    return Response({'data': 'only HR admin sees this'})
```

### Add Permission Flags to Template Context
```python
from .decorators import get_permission_context

def my_view(request):
    context = get_permission_context(request)
    # Returns: is_admin, is_hr_admin, is_manager, user_role, etc.
    return render(request, 'template.html', context)
```

### Check Permissions in Template
```django
{% if is_admin %}
    <div>Admin-only content</div>
{% endif %}

{% if can_manage_team %}
    <div>Manager-level content</div>
{% endif %}

{% if user_role == 'employee' %}
    <div>Employee self-service</div>
{% endif %}
```

## Access Denied Response

**For Views**: HTTP 403 with message
```
You do not have permission to access this page. [Role] access required.
```

**For APIs**: HTTP 403 JSON with message
```json
{
    "detail": "You do not have permission to perform this action."
}
```

## Testing Permissions

1. **Create test users of each role**
   ```bash
   python manage.py shell
   from django.contrib.auth.models import User
   from employees.models import Employee
   
   # Create admin
   admin_user = User.objects.create_user(
       username='admin', password='test123'
   )
   Employee.objects.create(user=admin_user, role='admin')
   ```

2. **Test each URL/API with different users**
3. **Verify 403 errors for unauthorized users**

## Common Patterns

### Only Allow Owner or Admin
```python
@employee_required
def edit_profile(request, pk):
    emp = Employee.objects.get(pk=pk)
    user_emp = Employee.objects.get(user=request.user)
    
    if emp.user != request.user and user_emp.role not in ['admin', 'hradmin']:
        return HttpResponseForbidden("Cannot edit other's profile")
```

### Different View for Each Role
```python
context = get_permission_context(request)

if context['is_admin']:
    data = get_admin_data()
elif context['is_hr_admin']:
    data = get_hr_data()
elif context['is_manager']:
    data = get_manager_data()
else:
    data = get_employee_data(request.user)

context['data'] = data
return render(request, 'view.html', context)
```

### API: Check Role in View
```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def custom_endpoint(request):
    emp = Employee.objects.get(user=request.user)
    
    if emp.role not in ['admin', 'hradmin']:
        return Response(
            {'error': 'Only HR admins can do this'},
            status=403
        )
    # Process the request
```

## Decorator Quick Lookup

| Decorator | Access | Common Use |
|-----------|--------|-----------|
| `@admin_required` | Admin only | System settings |
| `@hr_admin_required` | Admin + HR Admin | Employee CRUD |
| `@manager_required` | Admin + HR Admin + Manager | Team management |
| `@employee_required` | All authenticated | Dashboard, profile |
| `@role_required('role1', 'role2')` | Custom roles | Flexible access |

## Permission Class Quick Lookup

| Class | Access | Common Use |
|-------|--------|-----------|
| `IsAdmin` | Admin only | API admin functions |
| `IsHRAdmin` | Admin + HR Admin | API HR functions |
| `IsManager` | Managers+ | API team functions |
| `IsEmployee` | All authenticated | API employee actions |
| `IsOwnEmployee` | Own + admins | Personal data API |
| `CanManageAttendance` | Role-based | Attendance API |

## Files to Know

| File | Purpose |
|------|---------|
| `employees/decorators.py` | Django view decorators |
| `employees/permissions.py` | REST API permission classes |
| `AUTHORIZATION_GUIDE.md` | Full documentation |
| `PERMISSIONS_IMPLEMENTATION.md` | What was added |

## Troubleshooting

**User gets 403?**
→ Check their Employee.role matches decorator/permission requirement

**Decorator not working?**
→ Make sure imports are correct: `from .decorators import ...`

**API returns 403 instead of 401?**
→ User is authenticated but doesn't have permission (not a login issue)

**Permission check in template returns False?**
→ Make sure you added `get_permission_context()` to view

**Users can access pages they shouldn't?**
→ Verify decorators are added to view (not just imports)

## Next Steps

1. ✅ Review the system - you're done!
2. 📖 Read AUTHORIZATION_GUIDE.md for more patterns
3. 🧪 Test with different user roles
4. 🔧 Add decorators to any custom views you create
5. 📝 Document role requirements for your team
