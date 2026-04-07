#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms.settings')
sys.path.insert(0, r'c:\Raph Folders\VS File Code\HrmanagementSystem\hrms')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("\n" + "="*60)
print("EMAIL CONFIGURATION CHECK")
print("="*60)
print(f"HOST: {settings.EMAIL_HOST}")
print(f"PORT: {settings.EMAIL_PORT}")
print(f"USER: {settings.EMAIL_HOST_USER}")
print(f"PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD)}")
print(f"USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"FROM: {settings.DEFAULT_FROM_EMAIL}")
print("="*60 + "\n")

print("Attempting to send test email...")
try:
    result = send_mail(
        subject='🧪 Test Email from HRMS - Password Reset Test',
        message='If you see this email, the HRMS password reset email system is working correctly!\n\nYour OTP codes will be sent to this email.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['raphjohnvisayas@gmail.com'],
        fail_silently=False,
    )
    print(f"✅ SUCCESS! Email sent successfully (messages sent: {result})")
    print("\nCheck your Gmail inbox for the test email.")
    print("If not in Inbox, check Spam/Promotions folder.")
except Exception as e:
    print(f"❌ FAILED: {type(e).__name__}")
    print(f"Error message: {str(e)}\n")
    import traceback
    traceback.print_exc()
