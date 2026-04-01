from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date
from django.contrib.auth.models import User
from employees.models import (
    Employee, Department, LeaveType, AttendancePolicy,
    LeaveRequest, Attendance, SalarySlip, Document
)


class Command(BaseCommand):
    help = 'Populate sample data for HR Management System'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting sample data population...'))

        # Create Departments
        dept_sales, _ = Department.objects.get_or_create(
            name='Sales',
            defaults={'description': 'Sales and Business Development'}
        )
        dept_it, _ = Department.objects.get_or_create(
            name='IT',
            defaults={'description': 'Information Technology'}
        )
        dept_hr, _ = Department.objects.get_or_create(
            name='Human Resources',
            defaults={'description': 'Human Resources and Admin'}
        )
        self.stdout.write(self.style.SUCCESS('✓ Departments created'))

        # Create Leave Types
        leave_types = [
            ('Sick Leave', 10, True),
            ('Casual Leave', 12, True),
            ('Annual Leave', 20, True),
            ('Unpaid Leave', 5, False),
        ]
        for name, days, requires_approval in leave_types:
            LeaveType.objects.get_or_create(
                name=name,
                defaults={
                    'max_days_per_year': days,
                    'requires_approval': requires_approval,
                    'description': f'{name} policy'
                }
            )
        self.stdout.write(self.style.SUCCESS('✓ Leave Types created'))

        # Create Attendance Policy
        AttendancePolicy.objects.get_or_create(
            name='Standard Policy',
            defaults={
                'description': 'Standard attendance policy',
                'working_hours_per_day': 8,
                'allow_late_by_minutes': 15,
                'early_checkout_minutes': 15,
                'monthly_working_days': 30,
                'require_geolocation': True,
                'max_distance_meters': 1000,
                'auto_checkout_after_hours': 12,
            }
        )
        self.stdout.write(self.style.SUCCESS('✓ Attendance Policies created'))

        # Add sample attendance records for existing employees
        all_employees = Employee.objects.all()
        if all_employees.exists():
            for employee in all_employees:
                # Create 10 attendance records for the last 10 days
                for i in range(10, 0, -1):
                    record_date = date.today() - timedelta(days=i)
                    
                    # Skip weekends
                    if record_date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
                        continue
                    
                    Attendance.objects.get_or_create(
                        employee=employee,
                        date=record_date,
                        defaults={
                            'status': 'present',
                            'check_in_time': timezone.now().time(),
                            'check_out_time': (timezone.now() + timedelta(hours=8)).time(),
                        }
                    )
            self.stdout.write(self.style.SUCCESS('✓ Attendance records created'))
        
        # Add sample leave requests
        if all_employees.exists():
            sick_leave = LeaveType.objects.filter(name='Sick Leave').first()
            casual_leave = LeaveType.objects.filter(name='Casual Leave').first()
            
            for idx, employee in enumerate(list(all_employees)[:5]):  # First 5 employees
                if sick_leave and idx % 2 == 0:
                    LeaveRequest.objects.get_or_create(
                        employee=employee,
                        start_date=date.today() + timedelta(days=5),
                        end_date=date.today() + timedelta(days=6),
                        leave_type=sick_leave,
                        defaults={
                            'reason': f'Medical check-up for {employee.user.first_name}',
                            'status': 'pending',
                        }
                    )
                
                if casual_leave and idx % 3 == 0:
                    LeaveRequest.objects.get_or_create(
                        employee=employee,
                        start_date=date.today() - timedelta(days=10),
                        end_date=date.today() - timedelta(days=8),
                        leave_type=casual_leave,
                        defaults={
                            'reason': f'Personal reasons',
                            'status': 'approved',
                            'approved_by': User.objects.filter(is_staff=True).first(),
                            'approval_date': timezone.now(),
                        }
                    )
            self.stdout.write(self.style.SUCCESS('✓ Leave Requests created'))
        
        # Add sample salary slips
        if all_employees.exists():
            for idx, employee in enumerate(list(all_employees)[:3]):  # First 3 employees
                for month in range(1, 4):  # Last 3 months
                    slip_month = date.today().replace(day=1) - timedelta(days=month*30)
                    slip_month = slip_month.replace(day=1)
                    
                    SalarySlip.objects.get_or_create(
                        employee=employee,
                        month=slip_month,
                        defaults={
                            'basic_salary': 50000 + (idx * 10000),
                            'allowances': 5000,
                            'deductions': 2000,
                            'gross_salary': 55000 + (idx * 10000),
                            'net_salary': 53000 + (idx * 10000),
                            'working_days': 30,
                            'present_days': 28,
                            'absent_days': 0,
                            'is_processed': True,
                            'processed_date': timezone.now(),
                        }
                    )
            self.stdout.write(self.style.SUCCESS('✓ Salary Slips created'))
        
        self.stdout.write(self.style.SUCCESS(
            '\n✅ Sample data population completed successfully!'
        ))
        self.stdout.write(self.style.WARNING(
            '\nNote: Login to /admin/ to manage all entities'
        ))
