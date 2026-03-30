from django.db import models
from django.contrib.auth.models import User

# Role choices
ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('hradmin', 'HR Admin'),
    ('manager', 'Manager'),
    ('employee', 'Employee'),
]

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    employee_id = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    hire_date = models.DateField(null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.role})"
    
    def get_role_label(self):
        """Get the display label for the role."""
        role_map = {
            'admin': 'System Admin',
            'hradmin': 'HR Admin',
            'manager': 'Manager',
            'employee': 'Employee'
        }
        return role_map.get(self.role, self.role)
    
    class Meta:
        ordering = ['employee_id']

