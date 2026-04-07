# 🔧 TRACK THIS - CONNECTION FIX GUIDE

## ❌ Problem You're Seeing
**Error**: "failed to connect to /192.168.254.107 (port 8000) from /10.0.2.15 (port 5656)"

**What it means**: Your Android app is trying to reach Django server but can't connect.

---

## ✅ SOLUTION (Follow Steps Exactly)

### **STEP 1: Start Django on 0.0.0.0:8000** ⭐ MOST IMPORTANT

**Why**: Using `0.0.0.0` tells Django to listen on ALL network interfaces (not just localhost)

1. Open **Command Prompt** or **PowerShell**

2. Navigate to backend:
```bash
cd "c:\Raph Folders\VS File Code\HrmanagementSystem\hrms"
```

3. Run this EXACT command:
```bash
python manage.py runserver 0.0.0.0:8000
```

**Expected Output**:
```
Django version 6.0.3, using settings 'hrms.settings'
Starting development server at http://0.0.0.0:8000/
Quit the server with CTRL-BREAK.
```

⚠️ **KEEP THIS TERMINAL OPEN!** (Don't close it)

---

### **STEP 2: Check Your Computer's IP Address**

The IP `192.168.254.107` in your screenshot is correct, but let's verify it hasn't changed.

1. Open **NEW** Command Prompt/PowerShell

2. Type:
```bash
ipconfig
```

3. Look for your WiFi adapter and find **IPv4 Address**:
```
Wireless LAN adapter Wi-Fi:
   IPv4 Address. . . . . . . . . . : 192.168.254.107
   Subnet Mask . . . . . . . . . . : 255.255.255.0
```

**Note the IP address** (e.g., `192.168.254.107`)

---

### **STEP 3: Check if IP Changed**

If your IPv4 Address is **NOT** `192.168.254.107`:

1. Open Android Studio
2. Edit: `app/src/main/java/com/trackthis/api/RetrofitClient.kt`
3. Find line:
```kotlin
private const val BASE_URL = "http://192.168.254.107:8000/api/"
```
4. Replace `192.168.254.107` with your NEW IP address
5. Rebuild project: Build → Rebuild Project
6. Run app again

---

### **STEP 4: Open Windows Firewall (CRUCIAL!)**

Windows likely blocks port 8000 by default. We need to allow it.

#### **For Windows 10/11**:

1. Click **Start Menu**
2. Search: `Windows Defender Firewall with Advanced Security`
3. Click to open
4. On LEFT side, click: **Inbound Rules**
5. On RIGHT side, click: **New Rule...**

**In the New Inbound Rule Wizard**:

**Screen 1 - Rule Type**:
- Select: **Port**
- Click: **Next**

**Screen 2 - Protocol and Ports**:
- Select: **TCP** (already selected)
- Select: **Specific local ports**
- Type: `8000`
- Click: **Next**

**Screen 3 - Action**:
- Select: **Allow the connection**
- Click: **Next**

**Screen 4 - Profile**:
- ✅ Check: **Domain**
- ✅ Check: **Private** (IMPORTANT)
- ✅ Check: **Public**
- Click: **Next**

**Screen 5 - Name**:
- Name: `Django Mobile API`
- Description: `Allow Django backend for Track This app`
- Click: **Finish**

**Expected**: You should see rule added to Inbound Rules list

---

### **STEP 5: Verify Connection (TEST FIRST!)**

Before trying the app, test from browser to confirm it works:

1. On **SAME COMPUTER** where Django is running, open **Chrome browser**

2. Type in address bar:
```
http://192.168.254.107:8000/api/auth/jwt/token/
```

3. Press Enter

**Expected Result** ✅:
```
Method "GET" not allowed
```

OR you'll see a JSON response with error about POST method.

**Either of these means CONNECTION IS WORKING!** ✓

**If you see** ❌:
```
This site can't be reached
192.168.254.107 refused to connect
```

Then go back to **Steps 1, 3, and 4** and verify each one.

---

### **STEP 6: Update Android App (If Needed)**

If you changed the IP in Step 3:

1. In Android Studio, rebuild:
   ```
   Build → Rebuild Project
   ```

2. Run app:
   ```
   Run → Run 'app'
   ```

---

### **STEP 7: Login in App**

Once Step 5 browser test works, try login in app:

**Credentials** (or create your own):
- Username: `employee1`
- Password: `emp123`

**Expected**: Dashboard screen appears

---

## 🆘 Troubleshooting Checklist

| Issue | Solution |
|-------|----------|
| "Connection refused" | Check Step 1 - Django must run on 0.0.0.0:8000 |
| "Connection timed out" | Check Step 4 - Firewall must allow port 8000 |
| Browser test (Step 5) fails | Django not listening - restart with 0.0.0.0:8000 |
| Browser test works but app fails | IP mismatch - check Step 2 and update Step 3 |
| "Permission denied" in firewall | Run command prompt as Administrator |

---

## 🔍 How to Debug

### **Check if Port 8000 is Open**:
```bash
netstat -an | findstr :8000
```

Should show: `LISTENING` (means Django is listening)

### **Check if Firewall Rule Exists**:
Search: "Windows Defender Firewall with Advanced Security" → Inbound Rules → Look for "Django Mobile API"

### **Restart Everything**:
1. Close Android app
2. Stop Django (Ctrl+C in terminal)
3. Close Android Studio
4. Restart command prompt
5. Run Step 1 again
6. Run app again

---

## 📱 From Your Phone/Emulator

If using **Physical Phone**:
- Make sure phone is on SAME WiFi network as computer
- Use your computer's IP from Step 2

If using **Android Emulator**:
- Emulator automatically routes to host computer
- Keep IP as `192.168.254.107` or your correct IP

---

## ✅ Final Verification Checklist

- [ ] Django running with: `python manage.py runserver 0.0.0.0:8000`
- [ ] IPv4 address confirmed with `ipconfig`
- [ ] Firewall rule created for port 8000
- [ ] Browser test shows "Method GET not allowed" (working!)
- [ ] Android app IP matches your computer's IPv4
- [ ] App rebuilt after any IP changes
- [ ] Can login with username/password
- [ ] See Dashboard screen

---

## 🎯 SUCCESS INDICATORS

✅ **Working when you see**:
- Browser loads `http://192.168.254.107:8000/api/auth/jwt/token/` successfully
- Android app progress bar disappears
- Dashboard screen appears with employee name
- Check-In button visible

---

## 💡 Why This Happened

Django by default only listens on `localhost` (127.0.0.1). This works fine for same-computer testing but NOT for phones/emulators on the network.

Using `0.0.0.0:8000` tells Django: "Listen on all network interfaces so people can reach me from anywhere on the network."

---

**After completing these steps, your app should connect successfully!**

If still having issues, reply with:
1. Browser test result (Step 5)
2. Output from `ipconfig`
3. Any error messages in app
