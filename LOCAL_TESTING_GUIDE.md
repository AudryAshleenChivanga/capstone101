# Local Testing Guide - User Registration

## ✅ Preliminary Tests - PASSED!

All backend tests passed successfully:
- ✅ Imports working
- ✅ Database connected (3 users found)
- ✅ Registration endpoint working (new user created: ID 4)
- ✅ Login authentication working (admin login successful)

---

## 🚀 Step-by-Step Testing Instructions

### Step 1: Start the Test Server

**Option A - Using the Batch File:**
```bash
start_test_server.bat
```

**Option B - Manual Command:**
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
[*] Starting H. pylori CDSS...
[OK] Configuration validated
[OK] Database initialized
[*] Admin user exists - updating password...
[OK] Admin password updated: admin / Admin@2024
[OK] Application ready!
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

### Step 2: Test the Signup Page

1. **Open your browser** and go to:
   ```
   http://localhost:8000/ui/signup.html
   ```

2. **Fill in the registration form** with test data:
   ```
   Full Name: Test Clinician
   Username: testclinician
   Email: testclinician@hospital.com
   Password: Test@12345
   Confirm Password: Test@12345
   Specialty: General Practice (optional)
   Institution: Test Hospital (optional)
   License Number: TEST123 (optional)
   ```

3. **Check the "I agree to Terms of Service" checkbox**

4. **Click "Create Account"**

5. **Expected Result:**
   - ✅ Green success message: "Account created successfully! Redirecting to login..."
   - ✅ Auto-redirect to login page after 2 seconds

---

### Step 3: Test Login

1. **On the login page** (http://localhost:8000/ui/login.html):
   ```
   Username: testclinician
   Password: Test@12345
   ```

2. **Click "Sign in"**

3. **Expected Result:**
   - ✅ Successful login
   - ✅ Redirect to dashboard
   - ✅ See your name in the top-right corner
   - ✅ Access all clinician features

---

### Step 4: Test Different Scenarios

#### Test 4.1: Duplicate Username
1. Try to register again with username: `testclinician`
2. **Expected**: Error message "Username already registered"

#### Test 4.2: Duplicate Email
1. Try to register with email: `testclinician@hospital.com`
2. **Expected**: Error message "Email already registered"

#### Test 4.3: Password Mismatch
1. Enter different passwords in Password and Confirm Password fields
2. **Expected**: Red border on Confirm Password field + error message

#### Test 4.4: Weak Password
1. Try password: `test123` (less than 8 characters)
2. **Expected**: Browser validation error

#### Test 4.5: Missing Required Fields
1. Leave Full Name or Username empty
2. **Expected**: "Please fill out this field" validation

---

### Step 5: Test Admin Login

1. **Login as admin:**
   ```
   Username: admin
   Password: Admin@2024
   ```

2. **Verify admin features:**
   - Access to Admin Dashboard
   - Can see user management
   - Can create users with different roles

---

### Step 6: Test Mobile Responsiveness

1. **Open browser Dev Tools** (F12)
2. **Toggle device toolbar** (Ctrl+Shift+M)
3. **Select mobile device** (e.g., iPhone 12)
4. **Navigate to signup page**
5. **Verify:**
   - ✅ Form fields stack vertically
   - ✅ Touch-friendly buttons
   - ✅ Easy scrolling
   - ✅ Readable text (16px minimum)

---

## 🔍 Checking Server Logs

While testing, monitor the terminal where the server is running. You should see:

**Successful Registration:**
```
INFO:     127.0.0.1:xxxxx - "POST /auth/register/public HTTP/1.1" 201 Created
```

**Successful Login:**
```
INFO:     127.0.0.1:xxxxx - "POST /auth/login HTTP/1.1" 200 OK
```

**Failed Registration (duplicate):**
```
INFO:     127.0.0.1:xxxxx - "POST /auth/register/public HTTP/1.1" 400 Bad Request
```

---

## 🧪 API Testing (Optional)

If you want to test the API directly:

### Test Registration Endpoint:
```powershell
$body = @{
    username = "apitest"
    email = "apitest@example.com"
    password = "Test@12345"
    full_name = "API Test User"
    role = "clinician"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/auth/register/public" -Method POST -Body $body -ContentType "application/json"
```

**Expected Response:**
```json
{
  "id": 5,
  "username": "apitest",
  "email": "apitest@example.com",
  "role": "clinician",
  "full_name": "API Test User",
  "is_active": true,
  "created_at": "2025-01-22T..."
}
```

### Test Login Endpoint:
```powershell
$body = @{
    username = "apitest"
    password = "Test@12345"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/auth/login" -Method POST -Body $body -ContentType "application/json"
```

**Expected Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 5,
    "username": "apitest",
    "role": "clinician",
    ...
  }
}
```

---

## ✅ Testing Checklist

Mark each item as you test:

### UI Testing:
- [ ] Signup page loads correctly
- [ ] All form fields visible and functional
- [ ] Password validation works
- [ ] Username format validation works
- [ ] Email validation works
- [ ] Terms checkbox required
- [ ] Success message displays
- [ ] Auto-redirect to login works
- [ ] Login with new account works
- [ ] Dashboard accessible after login

### Error Handling:
- [ ] Duplicate username error
- [ ] Duplicate email error
- [ ] Password mismatch error
- [ ] Weak password validation
- [ ] Required field validation
- [ ] Network error handling

### Mobile Testing:
- [ ] Responsive layout works
- [ ] Touch-friendly controls
- [ ] Scrolling smooth
- [ ] Text readable

### Admin Testing:
- [ ] Admin login works
- [ ] Admin dashboard accessible
- [ ] Can view registered users

### API Testing (Optional):
- [ ] POST /auth/register/public works
- [ ] POST /auth/login works
- [ ] Error responses correct

---

## 🐛 Troubleshooting

### Issue: Server won't start
**Solution:**
1. Check if port 8000 is already in use
2. Kill existing Python processes:
   ```powershell
   Get-Process python | Stop-Process
   ```
3. Restart server

### Issue: "Module not found" error
**Solution:**
```bash
pip install -r requirements.txt
pip install google-auth google-auth-oauthlib
```

### Issue: Database error
**Solution:**
```bash
# Delete old database
del cdss.db

# Restart server (tables will be recreated)
python -m uvicorn main:app --reload
```

### Issue: Signup page doesn't load
**Solution:**
1. Check browser console (F12) for errors
2. Verify URL: http://localhost:8000/ui/signup.html
3. Clear browser cache (Ctrl+Shift+Delete)

### Issue: Can't login after registration
**Solution:**
1. Check server logs for errors
2. Verify user was created in database
3. Try admin login to verify server is working

---

## 📊 Database Verification

To check registered users in the database:

**Option 1 - Python Script:**
```python
from app.db import SessionLocal
from app.models import User

db = SessionLocal()
users = db.query(User).all()
for user in users:
    print(f"ID: {user.id}, Username: {user.username}, Role: {user.role}, Active: {user.is_active}")
db.close()
```

**Option 2 - SQLite CLI:**
```bash
sqlite3 cdss.db
SELECT id, username, email, role, is_active FROM users;
.exit
```

---

## 🎉 Success Criteria

Your local testing is successful if:
- ✅ All 4 backend tests pass (we already confirmed this)
- ✅ Signup page loads and is functional
- ✅ New users can register successfully
- ✅ Registration creates users with "clinician" role
- ✅ Users can login immediately after registration
- ✅ Dashboard accessible after login
- ✅ Duplicate detection works
- ✅ Password validation works
- ✅ Mobile responsive design works
- ✅ No console errors in browser
- ✅ No server errors in terminal

---

## 🚀 Next Step: Deploy to Render

Once local testing passes, you're ready to deploy:

1. **Commit changes:**
   ```bash
   git add app/routes_auth.py ui/signup.html ui/login.html ui/index.html
   git commit -m "Add public user registration functionality"
   git push origin main
   ```

2. **Render will auto-deploy** (if auto-deploy is enabled)

3. **Test on production:**
   - https://h-pylori-cdss.onrender.com/ui/signup.html
   - Register a test user
   - Login
   - Verify dashboard access

---

## 📝 Test Report Template

After testing, document your results:

```
LOCAL TESTING REPORT - User Registration
Date: [DATE]
Tester: [YOUR NAME]

BACKEND TESTS:
✅ Imports: PASS
✅ Database: PASS (3 users found)
✅ Registration: PASS (User ID 4 created)
✅ Login: PASS (Admin authentication successful)

UI TESTS:
[ ] Signup page loads: PASS/FAIL
[ ] Form validation: PASS/FAIL
[ ] User registration: PASS/FAIL
[ ] Login: PASS/FAIL
[ ] Dashboard access: PASS/FAIL

MOBILE TESTS:
[ ] Responsive design: PASS/FAIL
[ ] Touch controls: PASS/FAIL

ERROR HANDLING:
[ ] Duplicate username: PASS/FAIL
[ ] Duplicate email: PASS/FAIL
[ ] Password validation: PASS/FAIL

NOTES:
[Any issues or observations]

READY FOR PRODUCTION: YES/NO
```

---

**Happy Testing! 🧪**

If you encounter any issues, check the troubleshooting section or review the server logs for error messages.


