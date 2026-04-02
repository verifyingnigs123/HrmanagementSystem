#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms.settings')
django.setup()

from employees.models import Attendance, Employee
from django.contrib.auth.models import User

# Get all attendance records
all_attendance = Attendance.objects.all()
print(f"\n✅ Total Attendance Records in Database: {all_attendance.count()}\n")

if all_attendance.count() > 0:
    for att in all_attendance:
        print(f"📅 Date: {att.date}")
        print(f"👤 Employee: {att.employee.user.username}")
        print(f"⏱️  Status: {att.status}")
        print(f"🔵 Check-in: {att.check_in_time}")
        print(f"🔴 Check-out: {att.check_out_time}")
        print(f"📍 GPS Check-in: ({att.check_in_latitude}, {att.check_in_longitude})")
        print(f"📍 GPS Check-out: ({att.check_out_latitude}, {att.check_out_longitude})")
        print("---")
else:
    print("❌ No attendance records found in database")
