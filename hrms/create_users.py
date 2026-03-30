import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee

# Clear existing users (optional)
# User.objects.all().delete()

# Create users with different roles
users_data = [
    {
        'username': 'admin',
        'email': 'admin@hrms.com',
        'password': 'admin123',
        'first_name': 'System',
        'last_name': 'Admin',
        'role': 'admin',
        'employee_id': 'ADM001',
        'department': 'IT',
        'position': 'System Administrator',
        'is_staff': True,
        'is_superuser': True,
    },
    {
        'username': 'hradmin',
        'email': 'hradmin@hrms.com',
        'password': 'hradmin123',
        'first_name': 'HR',
        'last_name': 'Admin',
        'role': 'hradmin',
        'employee_id': 'HR001',
        'department': 'Human Resources',
        'position': 'HR Administrator',
        'is_staff': True,
        'is_superuser': False,
    },
    {
        'username': 'manager1',
        'email': 'manager@hrms.com',
        'password': 'manager123',
        'first_name': 'John',
        'last_name': 'Manager',
        'role': 'manager',
        'employee_id': 'MGR001',
        'department': 'Sales',
        'position': 'Sales Manager',
        'is_staff': False,
        'is_superuser': False,
    },
    {
        'username': 'employee1',
        'email': 'employee@hrms.com',
        'password': 'emp123',
        'first_name': 'Jane',
        'last_name': 'Employee',
        'role': 'employee',
        'employee_id': 'EMP001',
        'department': 'Sales',
        'position': 'Sales Representative',
        'is_staff': False,
        'is_superuser': False,
    },
]

for user_data in users_data:
    # Extract employee-specific data
    role = user_data.pop('role')
    employee_id = user_data.pop('employee_id')
    department = user_data.pop('department')
    position = user_data.pop('position')
    
    # Create or update user
    user, created = User.objects.get_or_create(
        username=user_data['username'],
        defaults={
            'email': user_data['email'],
            'first_name': user_data['first_name'],
            'last_name': user_data['last_name'],
            'is_staff': user_data['is_staff'],
            'is_superuser': user_data['is_superuser'],
        }
    )
    
    # Set password
    user.set_password(user_data['password'])
    user.save()
    
    # Create or update employee record
    employee, created = Employee.objects.get_or_create(
        user=user,
        defaults={
            'role': role,
            'employee_id': employee_id,
            'department': department,
            'position': position,
        }
    )
    
    if created:
        print(f"✅ Created user: {user.username} ({role})")
    else:
        print(f"⚠️  User already exists: {user.username}")

print("\n✨ User setup complete!")
