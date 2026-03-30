from django.contrib import admin
from .models import Role, Employee

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




