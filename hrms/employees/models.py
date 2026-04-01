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


# Department Model
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    head = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_departments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


# Leave Type Model
class LeaveType(models.Model):
    name = models.CharField(max_length=50, unique=True)  # Sick Leave, Casual Leave, etc.
    description = models.TextField(blank=True)
    max_days_per_year = models.IntegerField(default=10)
    requires_approval = models.BooleanField(default=True)
    color_code = models.CharField(max_length=7, default='#FF5733', help_text="Hex color code for UI display")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


# Leave Request Model
class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT, related_name='requests')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    approval_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.employee.user.first_name} - {self.leave_type.name} ({self.start_date})"
    
    @property
    def number_of_days(self):
        """Calculate number of days for the leave request."""
        return (self.end_date - self.start_date).days + 1


# Salary Slip Model
class SalarySlip(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_slips')
    month = models.DateField(help_text="First day of the month")
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    working_days = models.IntegerField(default=30)
    present_days = models.IntegerField(default=0)
    absent_days = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    is_processed = models.BooleanField(default=False)
    processed_date = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_salary_slips')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('employee', 'month')
        ordering = ['-month']
        indexes = [
            models.Index(fields=['employee', 'month']),
        ]
    
    def __str__(self):
        return f"{self.employee} - {self.month.strftime('%B %Y')}"


# Document Model
class Document(models.Model):
    DOCUMENT_CATEGORY_CHOICES = [
        ('identification', 'Identification'),
        ('qualifications', 'Qualifications'),
        ('certifications', 'Certifications'),
        ('financial', 'Financial'),
        ('medical', 'Medical'),
        ('legal', 'Legal'),
        ('other', 'Other'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=DOCUMENT_CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='documents/%Y/%m/')
    file_size = models.IntegerField(null=True, blank=True, help_text="File size in bytes")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_documents')
    expiry_date = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_documents')
    verified_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee', 'category']),
        ]
    
    def __str__(self):
        return f"{self.employee} - {self.title}"


# Attendance Policy Model
class AttendancePolicy(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    working_hours_per_day = models.IntegerField(default=8, help_text="Working hours per day")
    allow_late_by_minutes = models.IntegerField(default=15, help_text="Allow late check-in by X minutes")
    early_checkout_minutes = models.IntegerField(default=15, help_text="Allow early checkout by X minutes")
    monthly_working_days = models.IntegerField(default=30)
    require_geolocation = models.BooleanField(default=True, help_text="Require GPS location for check-in")
    max_distance_meters = models.IntegerField(default=1000, help_text="Maximum distance from office in meters")
    auto_checkout_after_hours = models.IntegerField(default=12, help_text="Auto checkout after X hours")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


# Audit Log Model for tracking all changes
class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)  # e.g., 'LeaveRequest', 'Employee'
    object_id = models.IntegerField(null=True, blank=True)
    object_description = models.CharField(max_length=255, blank=True)
    changes = models.JSONField(default=dict, blank=True)  # Store what changed
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['model_name', 'object_id']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.action} on {self.model_name} at {self.created_at}"
