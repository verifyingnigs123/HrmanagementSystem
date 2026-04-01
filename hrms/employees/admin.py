from django.contrib import admin
from .models import (
    Role, Employee, Attendance, Department, LeaveType, 
    LeaveRequest, SalarySlip, Document, AttendancePolicy, AuditLog
)

# Customize admin site
admin.site.site_header = "HR Management System"
admin.site.site_title = "HRMS Admin Portal"
admin.site.index_title = "Welcome to HR Management System"

# Register models
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'user', 'role', 'department', 'position', 'is_active']
    list_filter = ['role', 'department', 'is_active', 'hire_date']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Info', {
            'fields': ('user', 'role')
        }),
        ('Employee Details', {
            'fields': ('employee_id', 'department', 'position', 'phone')
        }),
        ('Personal Info', {
            'fields': ('date_of_birth',)
        }),
        ('Employment', {
            'fields': ('hire_date', 'salary', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'status', 'check_in_time', 'check_out_time']
    list_filter = ['date', 'status', 'employee__department']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'employee__employee_id']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Employee & Date', {
            'fields': ('employee', 'date', 'status')
        }),
        ('Check-in Details', {
            'fields': ('check_in_time', 'check_in_latitude', 'check_in_longitude')
        }),
        ('Check-out Details', {
            'fields': ('check_out_time', 'check_out_latitude', 'check_out_longitude')
        }),
        ('Additional Info', {
            'fields': ('notes', 'marked_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'head', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'max_days_per_year', 'requires_approval', 'is_active']
    list_filter = ['requires_approval', 'is_active']
    search_fields = ['name']


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'status', 'number_of_days']
    list_filter = ['status', 'leave_type', 'start_date']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'employee__employee_id']
    readonly_fields = ['created_at', 'updated_at', 'number_of_days']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Employee & Leave Type', {
            'fields': ('employee', 'leave_type')
        }),
        ('Leave Duration', {
            'fields': ('start_date', 'end_date', 'number_of_days')
        }),
        ('Details', {
            'fields': ('reason',)
        }),
        ('Approval', {
            'fields': ('status', 'approved_by', 'approval_date', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SalarySlip)
class SalarySlipAdmin(admin.ModelAdmin):
    list_display = ['employee', 'month', 'gross_salary', 'net_salary', 'is_processed']
    list_filter = ['is_processed', 'month', 'employee__department']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'employee__employee_id']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'month'
    
    fieldsets = (
        ('Employee & Month', {
            'fields': ('employee', 'month')
        }),
        ('Salary Breakdown', {
            'fields': ('basic_salary', 'allowances', 'deductions', 'gross_salary', 'net_salary')
        }),
        ('Attendance', {
            'fields': ('working_days', 'present_days', 'absent_days')
        }),
        ('Processing', {
            'fields': ('is_processed', 'processed_date', 'processed_by', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'title', 'category', 'is_verified', 'expiry_date', 'created_at']
    list_filter = ['category', 'is_verified', 'created_at']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'title']
    readonly_fields = ['created_at', 'updated_at', 'file_size']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Employee & Title', {
            'fields': ('employee', 'title')
        }),
        ('File & Category', {
            'fields': ('category', 'file', 'file_size', 'description')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verified_by', 'verified_date')
        }),
        ('Expiry', {
            'fields': ('expiry_date',)
        }),
        ('Upload Info', {
            'fields': ('uploaded_by',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AttendancePolicy)
class AttendancePolicyAdmin(admin.ModelAdmin):
    list_display = ['name', 'working_hours_per_day', 'allow_late_by_minutes', 'require_geolocation', 'is_active']
    list_filter = ['require_geolocation', 'is_active']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'object_description', 'created_at']
    list_filter = ['action', 'model_name', 'created_at']
    search_fields = ['user__username', 'object_description', 'ip_address']
    readonly_fields = ['user', 'action', 'model_name', 'object_id', 'changes', 'ip_address', 'user_agent', 'created_at']
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        """Prevent manual creation of audit logs."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent editing of audit logs."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of audit logs."""
        return False
