#!/usr/bin/env python
"""
Email Configuration Diagnostic Script
Tests if emails can be sent from HRMS
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms.settings')
sys.path.insert(0, os.path.dirname(__file__))

# Add the hrms folder to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'hrms'))

# Change to hrms directory
os.chdir(os.path.join(os.path.dirname(__file__), 'hrms'))

django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("\n" + "="*70)
print("EMAIL CONFIGURATION DIAGNOSTIC")
print("="*70)

print("\n1. CHECKING EMAIL SETTINGS:")
print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"   EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"   EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

# Check if credentials are set
if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
    print("\n❌ ERROR: Email credentials not set!")
    print("   Please check your .env file and ensure:")
    print("   - EMAIL_HOST_USER=raphjohnvisayas@gmail.com")
    print("   - EMAIL_HOST_PASSWORD=nkmf gfgr fagf vrzj")
    sys.exit(1)

print("\n2. ATTEMPTING TO SEND TEST EMAIL...")
try:
    result = send_mail(
        subject='🧪 HRMS Email Configuration Test',
        message='If you receive this email, the HRMS email configuration is working correctly!\n\nYour password reset OTP system is ready to use.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['raphjohnvisayas@gmail.com'],
        fail_silently=False,
    )
    print(f"\n✅ SUCCESS! Email sent successfully!")
    print(f"   Messages sent: {result}")
    print(f"\n   Check your Gmail inbox for the test email.")
    print(f"   If not in Inbox, check Spam/Promotions folder.")
    
except Exception as e:
    print(f"\n❌ FAILED! Email could not be sent.")
    print(f"   Error Type: {type(e).__name__}")
    print(f"   Error Message: {str(e)}")
    print(f"\n   TROUBLESHOOTING:")
    print(f"   1. Check if Gmail App Password is correct")
    print(f"   2. Ensure 2FA is enabled on Gmail account")
    print(f"   3. Check if firewall blocks SMTP port 587")
    print(f"   4. Verify .env file has correct credentials (no extra spaces)")
    
    import traceback
    print(f"\n   FULL ERROR TRACEBACK:")
    traceback.print_exc()

print("\n" + "="*70)
