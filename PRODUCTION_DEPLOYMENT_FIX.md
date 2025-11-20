# Production Deployment Fix Guide

## Issue
Changes pushed to GitHub but not showing in production because:
1. Render hasn't redeployed automatically
2. Database tables for model management not created in production

---

## Step-by-Step Fix

### Step 1: Force Render to Redeploy

#### Option A: Manual Redeploy (Recommended)
1. Go to: https://dashboard.render.com/
2. Find your service: `h-pylori-cdss`
3. Click on the service name
4. In the top right, click **"Manual Deploy"** button
5. Select **"Deploy latest commit"**
6. Click **"Deploy"**
7. Wait 3-5 minutes for deployment to complete

#### Option B: Via Git Trigger
If manual deploy doesn't work, push a small change:
```bash
# Add a comment to force redeploy
echo "# Deployment trigger" >> README.md
git add README.md
git commit -m "Trigger Render redeploy"
git push origin main
```

---

### Step 2: Create Database Tables in Production

After deployment completes, you need to create the new database tables.

#### Access Render Shell
1. In Render dashboard, go to your service
2. Click the **"Shell"** tab
3. You'll get a command-line interface

#### Run Setup Commands
Copy and paste these commands **one at a time** in the Render Shell:

```bash
# Navigate to project directory
cd /opt/render/project/src

# Create model management tables
python create_model_tables.py
```

**Expected Output:**
```
Creating/updating database tables...
[OK] Tables created successfully

Found 0 existing model training records

Creating initial model training records for current production models...
[OK] Initial model records created

[OK] PredictionLog table exists with 0 records

============================================================
Database setup complete!
============================================================
```

---

### Step 3: Verify Everything Works

#### Test 1: Check Main App
1. Go to: https://h-pylori-cdss.onrender.com/
2. Login (admin / Admin@2024)
3. Go to Dashboard
4. Navigate to **Case History**
5. Switch to **Light Mode** (☀️ icon)
6. **Check Clinician Column** - Should be visible now ✅

#### Test 2: Check Model Management
1. From Dashboard, click **"Admin Panel"**
2. Look for **"🤖 AI Model Management"** button
3. Click it
4. You should see:
   - Two model cards (Screening & Staging)
   - Performance metrics
   - Three dynamic charts
   - Recent predictions table

If you see this, **IT'S WORKING!** 🎉

---

## Common Issues & Solutions

### Issue: "Manual Deploy" button is grayed out
**Solution**: Wait for any current deployment to finish first

### Issue: Render Shell shows "command not found"
**Solution**: Make sure you're in the right directory:
```bash
pwd  # Should show /opt/render/project/src
ls   # Should show main.py, app/, ui/, etc.
```

### Issue: "python: No such file or directory"
**Solution**: Try `python3` instead:
```bash
python3 create_model_tables.py
```

### Issue: Database script fails
**Solution**: Check if tables already exist:
```bash
python3 -c "from app.db import SessionLocal; from app.models import PredictionLog, ModelTraining; db = SessionLocal(); print(f'PredictionLog: {db.query(PredictionLog).count()}, ModelTraining: {db.query(ModelTraining).count()}')"
```

### Issue: Changes still not showing after redeploy
**Solution**: 
1. Clear browser cache (Ctrl+Shift+R / Cmd+Shift+R)
2. Try incognito/private window
3. Check Render logs for errors

### Issue: Model Management page shows 404
**Solution**: 
1. Verify redeploy completed successfully
2. Check Render logs for import errors
3. Restart the service from Render dashboard

---

## Quick Verification Checklist

After completing steps above:

- [ ] Render shows "Live" status (green)
- [ ] Can access main app: https://h-pylori-cdss.onrender.com/
- [ ] Can login successfully
- [ ] Clinician column visible in light mode
- [ ] "AI Model Management" button appears in Admin Panel
- [ ] Model Management dashboard loads
- [ ] Charts are visible and loading data
- [ ] No console errors (press F12 to check)

---

## If Nothing Works - Nuclear Option

If after all steps above nothing works:

### 1. Check Render Service Logs
```
Dashboard → Your Service → Logs tab
```
Look for errors during startup

### 2. Check Build Logs
```
Dashboard → Your Service → Events tab
```
Verify build completed successfully

### 3. Restart Service
```
Dashboard → Your Service → Settings
Click "Suspend Service" → Wait 30s → Click "Resume Service"
```

### 4. Verify Environment Variables
```
Dashboard → Your Service → Environment
```
Make sure these exist:
- DATABASE_URL
- JWT_SECRET
- SCREEN_MODEL_PATH
- STAGE_MODEL_PATH

---

## Why This Happened

### Auto-Deploy Not Triggered
Render's auto-deploy can sometimes:
- Miss push events
- Be disabled in settings
- Fail silently
- Have webhook issues with GitHub

**Solution**: Always manually redeploy for critical changes

### Database Schema Changes
When you add new tables:
- SQLite doesn't auto-migrate
- Must run migration scripts manually
- Production and local DBs are separate

**Solution**: Always run setup scripts in production after deployment

---

## Prevention for Future

### For Code Changes:
1. Push to GitHub ✓
2. **Manually trigger Render redeploy** ✓
3. Wait for deployment to complete ✓
4. Clear browser cache ✓
5. Test in production ✓

### For Database Changes:
1. Push code to GitHub ✓
2. Redeploy on Render ✓
3. **Open Render Shell** ✓
4. **Run migration/setup scripts** ✓
5. Verify tables created ✓
6. Test features ✓

---

## Contact for Help

If still stuck after following this guide:
1. Check Render logs for specific errors
2. Screenshot any error messages
3. Verify all steps were completed
4. Try the nuclear option above

---

**Expected Time**: 10-15 minutes total
**Difficulty**: Easy (just clicking buttons and running one command)

Good luck! 🚀

