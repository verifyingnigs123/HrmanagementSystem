@echo off
REM ================================================
REM TRACK THIS - QUICK CONNECTION FIX SCRIPT
REM ================================================
REM Run this to quickly fix the connection issue!

echo.
echo ============================================
echo TRACK THIS - CONNECTION TROUBLESHOOTER
echo ============================================
echo.

echo STEP 1: Checking your IPv4 Address...
echo.
ipconfig | findstr /I "IPv4"
echo.

echo STEP 2: Checking if Port 8000 is Open...
echo.
netstat -an | findstr :8000
echo.

echo STEP 3: Instructions to Fix
echo.
echo DO THIS:
echo 1. Open Command Prompt as ADMINISTRATOR
echo 2. Navigate to: cd "c:\Raph Folders\VS File Code\HrmanagementSystem\hrms"
echo 3. Run command: python manage.py runserver 0.0.0.0:8000
echo 4. KEEP THIS TERMINAL OPEN
echo.
echo FIREWALL:
echo 1. Search: "Windows Defender Firewall with Advanced Security"
echo 2. Click: Inbound Rules
echo 3. Click: New Rule
echo 4. Select: Port, then TCP port 8000
echo 5. Select: Allow connection
echo 6. Name: Django Mobile API
echo.
echo BROWSER TEST:
echo 1. Open Chrome
echo 2. Type: http://192.168.254.107:8000/api/auth/jwt/token/
echo 3. Should see error like "Method GET not allowed" (THIS IS GOOD!)
echo.
echo ============================================
echo Press any key to close...
pause
