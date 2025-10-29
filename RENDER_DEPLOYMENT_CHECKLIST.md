# Render Deployment Checklist

## ✅ Before Manual Deploy

### 1. Environment Variables on Render
Make sure these are set in Render Dashboard → Environment:

```env
# Required
DATABASE_URL=<render_postgresql_url>
JWT_SECRET=<your_secure_random_string>

# ML Models
SCREEN_MODEL_PATH=models/screening_hp_pos_calibrated.joblib
STAGE_MODEL_PATH=models/staging_3class.joblib
SCREEN_THRESH=0.60

# Optional (for SMS/Email features)
TWILIO_ACCOUNT_SID=<your_twilio_sid>
TWILIO_AUTH_TOKEN=<your_twilio_token>
TWILIO_PHONE_NUMBER=<your_twilio_number>
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=<your_email>
SMTP_PASSWORD=<your_app_password>

# CORS (important!)
ALLOWED_ORIGINS=https://your-app.onrender.com,https://h-pylori-cdss.onrender.com
```

### 2. Build Command
```bash
pip install -r requirements.txt
```

### 3. Start Command
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 4. Files to Check Exist
- ✅ `main.py`
- ✅ `requirements.txt`
- ✅ `ui/` directory with HTML files
- ✅ `images/` directory
- ✅ `models/` directory with .joblib files
- ✅ `app/` directory with all route files

### 5. Git Push to Trigger Deploy
```bash
git add -A
git commit -m "Fix: Update static file serving for production"
git push origin main
```

## 🔍 Common Issues & Fixes

### Issue: "Only showing assets, no pages"
**Cause**: Static files mounted before API routes
**Fix**: Ensure API routers are included BEFORE `app.mount()` calls ✅ FIXED

### Issue: "404 on all pages"
**Cause**: Wrong directory structure or missing files
**Fix**: Check that `ui/index.html` exists

### Issue: "CORS errors"
**Cause**: ALLOWED_ORIGINS not including Render URL
**Fix**: Add your Render URL to ALLOWED_ORIGINS environment variable

### Issue: "Database errors"
**Cause**: DATABASE_URL not set or wrong format
**Fix**: Use Render PostgreSQL internal URL format

### Issue: "ML models not loading"
**Cause**: Model files not in repository
**Fix**: Ensure `models/*.joblib` files are committed to git

## 📊 After Deploy - Test These

1. ✅ Landing page loads: `https://your-app.onrender.com/`
2. ✅ Login page loads: `https://your-app.onrender.com/ui/login.html`
3. ✅ API health check: `https://your-app.onrender.com/health`
4. ✅ API docs: `https://your-app.onrender.com/docs`
5. ✅ Images load: Check if doctor images appear
6. ✅ Login works: Test with admin credentials
7. ✅ Dashboard loads: After successful login
8. ✅ Screening workflow: Test Stage 1-3
9. ✅ 3D Biopsy: Check if visualization loads

## 🚀 Deploy Now!

After making above changes:
1. Commit changes
2. Push to GitHub (main branch)
3. Go to Render Dashboard
4. Click "Manual Deploy" → "Deploy latest commit"
5. Wait 3-5 minutes
6. Test your app!

