from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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


# Attendance Model for tracking employee check-in/check-out
class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('half_day', 'Half Day'),
        ('leave', 'Leave'),
        ('excused', 'Excused Absence'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    check_in_latitude = models.FloatField(null=True, blank=True, help_text="GPS latitude at check-in")
    check_in_longitude = models.FloatField(null=True, blank=True, help_text="GPS longitude at check-in")
    check_out_latitude = models.FloatField(null=True, blank=True, help_text="GPS latitude at check-out")
    check_out_longitude = models.FloatField(null=True, blank=True, help_text="GPS longitude at check-out")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='attendance_marked')
    
    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['-date']
        verbose_name_plural = "Attendance"
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.employee} - {self.date} ({self.status})"
