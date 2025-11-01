# Render Configuration for Python 3 Deployment

## 🐍 **Correct Render Settings (Python 3)**

### **General Settings**
- **Name:** `h-pylori-cdss` (or your service name)
- **Region:** Oregon (or closest to you)
- **Branch:** `main` ✅
- **Root Directory:** (leave blank)
- **Environment:** **Python 3** ✅

### **Build & Deploy**

#### **Build Command:**
```bash
pip install -r requirements.txt
```

#### **Start Command (Choose ONE):**

**Option 1: Direct uvicorn (Recommended)**
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Option 2: Using bash script**
```bash
bash start_server.sh
```

**Option 3: With multiple workers (Better performance)**
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT --workers 2
```

---

## 🔧 **Environment Variables**

### **Required Variables:**
```
JWT_SECRET = [Click "Generate" in Render dashboard]
JWT_EXPIRE_HOURS = 24
SCREEN_MODEL_PATH = models/screening_hp_pos_calibrated.joblib
STAGE_MODEL_PATH = models/staging_3class.joblib
SCREEN_THRESH = 0.60
ALLOWED_ORIGINS = https://h-pylori-cdss.onrender.com
```

### **Database (Optional - if using PostgreSQL):**
```
DATABASE_URL = [From Render PostgreSQL if you add one]
```

### **SMS/Email (Optional):**
```
TWILIO_ACCOUNT_SID = your_sid
TWILIO_AUTH_TOKEN = your_token
TWILIO_PHONE_NUMBER = +1234567890
SMTP_SERVER = smtp.gmail.com
SMTP_PORT = 587
SMTP_USERNAME = your_email@gmail.com
SMTP_PASSWORD = your_app_password
```

---

## 📋 **Step-by-Step: Update Your Render Service**

### **Step 1: Go to Settings**
1. Login to https://dashboard.render.com/
2. Click your service name
3. Click **"Settings"** (left sidebar)

### **Step 2: Verify Build & Deploy**
Scroll to **"Build & Deploy"** section:

```
Environment: Python 3               ✅ Confirm this
Python Version: 3.10                ✅ (or 3.11)
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### **Step 3: Verify Auto-Deploy**
```
Branch: main                        ✅ Confirm this
Auto-Deploy: Yes                    ✅ Confirm this
```

### **Step 4: Check Environment Variables**
Click **"Environment"** tab (left sidebar):
- Verify all required variables are set
- Generate JWT_SECRET if missing
- Add ALLOWED_ORIGINS with your Render URL

### **Step 5: Save and Deploy**
1. Click **"Save Changes"** (if you made any)
2. Click **"Manual Deploy"** (top right)
3. Select **"Deploy latest commit"**
4. Wait 3-5 minutes

---

## 🎯 **Why This Works Better Than Windows Scripts**

### **Your Local Scripts (Windows Only):**
- `start_server.bat` - Windows batch file ❌ Won't work on Render (Linux)
- `restart_server.ps1` - PowerShell script ❌ Won't work on Render (Linux)
- `.\start_server` - Windows PowerShell command ❌ Won't work on Render

### **Render (Linux Server):**
- Needs bash scripts (`.sh`) or direct commands ✅
- Uses `$PORT` environment variable (Render provides this) ✅
- No virtual environment activation needed (Render handles it) ✅

---

## ✅ **What We Fixed**

### **Before (Issues):**
1. Static files loaded before API routes
2. Windows-specific startup commands
3. Route conflicts

### **After (Fixed):**
1. ✅ API routes load BEFORE static mounts (`main.py` line 117-143)
2. ✅ Created Linux-compatible `start_server.sh`
3. ✅ Proper Render configuration documented
4. ✅ Environment variables properly set

---

## 🔍 **Troubleshooting**

### **Issue: "Command not found: start_server"**
**Fix:** Use full command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### **Issue: "ModuleNotFoundError"**
**Fix:** Build command should be: `pip install -r requirements.txt`

### **Issue: "Health check failed"**
**Fix:** 
1. Check Start Command uses `$PORT` (not hardcoded 8000)
2. Verify `/health` endpoint works
3. Wait 1-2 minutes after deploy

### **Issue: "Static files not loading"**
**Fix:** Already fixed in `main.py` - just redeploy with latest code

### **Issue: "Application timeout"**
**Fix:** 
1. Check logs in Render dashboard
2. Verify DATABASE_URL format if using PostgreSQL
3. Ensure ML models are in repository

---

## 📊 **Recommended Start Command**

For **best performance** on Render's free tier:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
```

For **paid tiers** (better performance):

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT --workers 2
```

**Why?**
- `--host 0.0.0.0` - Makes server accessible externally
- `--port $PORT` - Uses Render's assigned port (CRITICAL!)
- `--workers 1` - Good for free tier (512MB RAM)
- `--workers 2` - Better for paid tiers (more RAM)

---

## 🚀 **Deploy Now!**

### **Option A: If Settings Are Correct**
Just click **"Manual Deploy"** → **"Deploy latest commit"**

### **Option B: If You Need to Update Settings**
1. Update **Start Command** to: `uvicorn main:app --host 0.0.0.0 --port $PORT`
2. Verify **Build Command**: `pip install -r requirements.txt`
3. Click **"Save Changes"**
4. Click **"Manual Deploy"** → **"Clear build cache & deploy"**

---

## ✅ **After Successful Deploy**

Test these URLs:
1. **Landing Page:** https://h-pylori-cdss.onrender.com/
2. **Health Check:** https://h-pylori-cdss.onrender.com/health
3. **API Docs:** https://h-pylori-cdss.onrender.com/docs
4. **Login Page:** https://h-pylori-cdss.onrender.com/ui/login.html

Expected health check response:
```json
{
  "status": "healthy",
  "service": "H. pylori CDSS",
  "version": "1.0.0"
}
```

---

## 📝 **Quick Copy-Paste**

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Environment Variables to Add:**
```
JWT_SECRET=[Generate]
JWT_EXPIRE_HOURS=24
SCREEN_MODEL_PATH=models/screening_hp_pos_calibrated.joblib
STAGE_MODEL_PATH=models/staging_3class.joblib
SCREEN_THRESH=0.60
ALLOWED_ORIGINS=https://h-pylori-cdss.onrender.com
```

---

**Your settings are now optimized for Python 3 deployment on Render! 🐍🚀**

