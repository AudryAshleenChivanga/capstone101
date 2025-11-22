# Production Troubleshooting Guide - Render Deployment

## 🚨 Current Issues & Fixes

### **Issue 1: Registration Not Working (Authentication Error)**

**Symptoms:**
- Users getting "not authenticated" error when trying to register
- Error occurs on production (Render), not locally

**Root Causes:**
1. CORS configuration blocking requests
2. Endpoint not properly deployed
3. Browser cache with old JavaScript

**Fixes Applied:**

#### **1. Updated CORS Configuration**
**File:** `main.py`
```python
# More permissive CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allowing all origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)
```

#### **2. Updated Render Environment Variable**
**File:** `render.yaml`
```yaml
- key: ALLOWED_ORIGINS
  value: "*"
```

#### **3. Added Test Endpoint**
**File:** `app/routes_auth.py`
```python
@router.get("/register/public/test")
def test_public_registration_endpoint():
    return {"status": "ok", "endpoint": "/auth/register/public"}
```

#### **4. Updated Config to Handle Wildcard**
**File:** `app/config.py`
```python
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "...")
ALLOWED_ORIGINS: list = ["*"] if allowed_origins_str == "*" else allowed_origins_str.split(",")
```

---

### **Issue 2: Print Forms Not Working**

**Symptoms:**
- Print button not responding
- Print preview empty
- PDF export fails

**Root Causes:**
1. Print CSS not loading
2. Print data not populated
3. DOM not ready when print called

**Fixes Applied:**

#### **1. Enhanced Print Function**
**File:** `ui/app.js`
```javascript
function printScreeningResults() {
    // Ensure print data is populated
    if (window.currentScreeningResult) {
        populatePrintFields(window.currentScreeningResult);
    }
    
    // Small delay to ensure DOM updates
    setTimeout(() => {
        window.print();
    }, 100);
}
```

#### **2. Verify Print CSS Loaded**
**File:** `ui/dashboard.html`
```html
<link rel="stylesheet" href="print.css" media="print">
```

---

## 🧪 Testing Instructions

### **Test 1: Endpoint Health Check**

**URL:** `https://h-pylori-cdss.onrender.com/ui/test_endpoints.html`

This page will automatically test:
- ✅ Health check endpoint
- ✅ Registration endpoint accessibility
- ✅ Login endpoint
- ✅ Google OAuth endpoint

**Expected Results:**
```
✅ Health Check - SUCCESS
✅ Public Registration Endpoint (OPTIONS) - SUCCESS
✅ Login Endpoint (OPTIONS) - SUCCESS
```

### **Test 2: Manual Registration Test**

1. **Clear Browser Cache:**
   ```
   Chrome: Ctrl+Shift+Delete → Clear cache
   Firefox: Ctrl+Shift+Delete → Clear cache
   Safari: Cmd+Option+E
   ```

2. **Open in Incognito/Private Window:**
   ```
   https://h-pylori-cdss.onrender.com/ui/login.html
   ```

3. **Click "Sign up"**

4. **Fill Registration Form:**
   ```
   Full Name: Test User
   Email: test@example.com
   Password: Test@12345
   Confirm: Test@12345
   ```

5. **Submit**

**Expected:**
- ✅ Success message appears
- ✅ Form toggles back to login
- ✅ Can login with registered credentials

**If Still Failing:**
- Check browser console (F12) for errors
- Copy exact error message
- Test endpoint health at `/ui/test_endpoints.html`

### **Test 3: Print Functionality**

1. **Complete Screening Assessment**
   ```
   https://h-pylori-cdss.onrender.com/ui/dashboard.html
   ```

2. **Fill screening form and submit**

3. **Wait for results to appear**

4. **Click "Print" button**

**Expected:**
- ✅ Print dialog opens
- ✅ Preview shows professional format
- ✅ Letterhead visible
- ✅ Patient info populated
- ✅ Status indicator shown
- ✅ No navigation/buttons in preview

**If Print Not Working:**
- Check browser console for errors
- Try "PDF" button instead
- Manually open print: Ctrl+P (Cmd+P on Mac)
- Check print.css loaded in Network tab

---

## 🔍 Diagnostic Endpoints

### **1. Test Registration Endpoint Availability**
```
GET https://h-pylori-cdss.onrender.com/auth/register/public/test
```

**Expected Response:**
```json
{
  "status": "ok",
  "message": "Public registration endpoint is accessible",
  "endpoint": "/auth/register/public",
  "method": "POST",
  "authentication_required": false
}
```

### **2. Health Check**
```
GET https://h-pylori-cdss.onrender.com/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "H. pylori CDSS",
  "version": "1.0.0"
}
```

### **3. CORS Preflight**
```bash
curl -X OPTIONS https://h-pylori-cdss.onrender.com/auth/register/public \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type" \
  -H "Origin: https://h-pylori-cdss.onrender.com"
```

**Expected Headers:**
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
Access-Control-Allow-Headers: *
```

---

## 🚀 Deployment Checklist

### **Before Pushing to Production**

- [ ] All files committed to git
- [ ] CORS configuration updated
- [ ] Test endpoints added
- [ ] Print functionality enhanced
- [ ] Documentation updated

### **After Pushing**

- [ ] Wait 5 minutes for Render deployment
- [ ] Check Render logs for "Application ready!"
- [ ] Test health endpoint
- [ ] Test registration endpoint availability
- [ ] Test actual registration
- [ ] Test print functionality
- [ ] Clear browser cache if issues persist

---

## 📊 Render Deployment Status

### **Monitor Deployment:**
```
https://dashboard.render.com/
```

**Look for:**
1. Status: Building → Deploying → **Live** ✅
2. Logs: "Application ready!"
3. Health Check: Passing (200 OK)
4. No errors in deployment logs

### **Common Deployment Issues:**

#### **Issue: Build Fails**
**Solution:**
- Check Render logs for Python errors
- Verify requirements.txt has all packages
- Ensure Dockerfile is correct

#### **Issue: Health Check Fails**
**Solution:**
- Verify `/health` endpoint works
- Check if server is starting on correct port
- Review startup logs

#### **Issue: 502 Bad Gateway**
**Solution:**
- Application not started yet (wait 5 min)
- Health check failing
- Server crashed (check logs)

---

## 🐛 Common Errors & Solutions

### **Error: "Not Authenticated"**

**Possible Causes:**
1. ❌ Old cached JavaScript
2. ❌ CORS blocking request
3. ❌ Wrong endpoint URL
4. ❌ Endpoint requires auth (shouldn't)

**Solutions:**
```javascript
// Clear cache
localStorage.clear();
sessionStorage.clear();
// Hard refresh: Ctrl+Shift+R

// Check endpoint URL
console.log(API_BASE); // Should be: https://h-pylori-cdss.onrender.com

// Test endpoint directly
fetch('https://h-pylori-cdss.onrender.com/auth/register/public/test')
  .then(r => r.json())
  .then(console.log);
```

### **Error: "CORS Policy Blocked"**

**Solution:**
```
✅ Already fixed in this deployment
- ALLOWED_ORIGINS set to "*"
- CORS middleware configured for all methods
- Expose headers enabled
```

### **Error: Print Dialog Empty**

**Solution:**
```javascript
// Check if print.css loaded
document.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
    console.log(link.href);
});

// Should include: /ui/print.css

// Manual trigger print
window.print();

// Check print data populated
console.log(window.currentScreeningResult);
```

---

## 🔐 Security Note

**Current CORS Setting:**
```yaml
ALLOWED_ORIGINS: "*"
```

⚠️ **This is temporarily permissive for debugging**

**After Confirming Registration Works:**
Update `render.yaml`:
```yaml
- key: ALLOWED_ORIGINS
  value: https://h-pylori-cdss.onrender.com
```

Then redeploy.

---

## 📞 Support Commands

### **Check Render Environment Variables:**
```bash
# Via Render Dashboard
Settings → Environment → View all variables
```

### **View Live Logs:**
```bash
# Via Render Dashboard
Logs tab → Real-time streaming
```

### **Force Redeploy:**
```bash
# Via Render Dashboard
Manual Deploy → Deploy latest commit
```

---

## ✅ Success Criteria

Deployment is successful when:

- [ ] Endpoint health check passes (`/ui/test_endpoints.html` shows all green)
- [ ] User can register without authentication error
- [ ] User can login with registered credentials
- [ ] Print button opens print dialog
- [ ] Print preview shows professional format
- [ ] No CORS errors in browser console
- [ ] No 401/403 errors in Network tab

---

## 📝 Quick Reference

### **Production URLs**
- Dashboard: `https://h-pylori-cdss.onrender.com/ui/dashboard.html`
- Login: `https://h-pylori-cdss.onrender.com/ui/login.html`
- Chat: `https://h-pylori-cdss.onrender.com/ui/chat.html`
- Health Check: `https://h-pylori-cdss.onrender.com/health`
- Endpoint Test: `https://h-pylori-cdss.onrender.com/ui/test_endpoints.html`

### **API Endpoints**
- Register: `POST /auth/register/public`
- Login: `POST /auth/login`
- Test Registration: `GET /auth/register/public/test`
- Health: `GET /health`

---

**All fixes have been applied. Push to production and test!** 🚀

