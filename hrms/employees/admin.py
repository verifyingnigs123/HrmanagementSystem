from django.contrib import admin
from .models import Role, Employee, Attendance

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
