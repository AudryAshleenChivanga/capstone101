# 🔍 Debug Capsule Endoscopy - Step by Step

## Issue
Button click doesn't trigger the RL simulation.

## Fixes Applied

1. ✅ Fixed event listener attachment on start button
2. ✅ Fixed scenario button active state tracking
3. ✅ Added comprehensive console logging
4. ✅ Fixed element ID mismatches (detectionsList → detectionsContainer)
5. ✅ Fixed CSS class names to match dashboard

## How to Debug

### Step 1: Hard Refresh Browser
**Critical!** Clear the cached JavaScript:
- **Windows:** Ctrl + Shift + R or Ctrl + F5
- **Mac:** Cmd + Shift + R

### Step 2: Open Browser Console
Press F12 → Click "Console" tab

### Step 3: Navigate to Capsule Endoscopy
Click "Capsule Endoscopy" in the sidebar

**Expected console output:**
```
Capsule endoscopy page shown, initializing...
Initializing Advanced Capsule Endoscopy...
Initialized 6 scenario buttons
Start button event listener attached
Capsule endoscopy ready
```

**If you see this**, the initialization worked! ✅

### Step 4: Click Start Button
Click "Start RL Training & Endoscopy"

**Expected console output:**
```
Start button clicked!
Starting capsule endoscopy: scenario=mixed
```

Then after a few seconds:
```
Simulation complete: {training_log: Array(20), ...}
```

### Step 5: Watch for API Call
In the console, you should see:
- Status messages updating
- Metrics changing
- Chart populating

**In the Network tab (F12 → Network):**
Look for:
- `POST /biopsy/capsule-endoscopy?scenario=mixed&num_steps=80`
- Status: 200 OK
- Response time: ~2-3 seconds

---

## Alternative: Test API Directly

I've created a simple test page to verify the API works:

### Open Test Page:
Go to: http://localhost:8000/test_capsule_api.html

Click "Test API Call" button

**If this works**, the API is fine and the issue is in the dashboard JavaScript.
**If this fails**, the issue is with the backend.

---

## Common Issues & Solutions

### Issue 1: "Start button not found!"
**Problem:** Element ID mismatch
**Solution:** Check that the button has `id="startBtn"`
```html
<button class="capsule-btn-primary" id="startBtn">
```

### Issue 2: No console output at all
**Problem:** JavaScript file not loaded or cached
**Solution:**
1. Hard refresh (Ctrl+Shift+R)
2. Check Network tab for `capsule_endoscopy.js` (should be 200 OK)
3. Clear browser cache completely

### Issue 3: "Capsule page not found"
**Problem:** `page-capsule` element doesn't exist
**Solution:** Check that dashboard HTML has:
```html
<div class="page" id="page-capsule" style="display: none;">
```

### Issue 4: Click registered but no API call
**Problem:** Fetch error or CORS issue
**Console will show:** Network error or CORS error
**Solution:**
- Check that server is running on port 8000
- Check browser console for network errors
- Verify API endpoint exists: `POST /biopsy/capsule-endoscopy`

### Issue 5: API returns 404
**Problem:** Route not registered
**Solution:** Check `app/routes_biopsy.py` has:
```python
@router.post("/capsule-endoscopy")
async def run_capsule_endoscopy(...):
```

### Issue 6: API returns 500
**Problem:** Backend error
**Console shows:** "Simulation failed: ..."
**Solution:** Check server terminal for Python errors

---

## What Each Console Message Means

| Message | Meaning | Status |
|---------|---------|--------|
| "Capsule endoscopy page shown, initializing..." | App_new.js called the init function | ✅ Good |
| "Initializing Advanced Capsule Endoscopy..." | Init function started | ✅ Good |
| "Capsule page not found, will initialize later" | Element not found yet | ⚠️ Warning |
| "Initialized X scenario buttons" | Scenario buttons set up | ✅ Good |
| "Start button event listener attached" | Button ready to click | ✅ Good |
| "Start button not found!" | Critical error | ❌ Error |
| "Capsule endoscopy ready" | All setup complete | ✅ Good |
| "Start button clicked!" | User clicked button | ✅ Good |
| "Starting capsule endoscopy: scenario=mixed" | API call starting | ✅ Good |
| "Simulation complete: {...}" | API returned data | ✅ Good |
| "Simulation error: ..." | API call failed | ❌ Error |

---

## Quick Checklist

Go through this checklist:

- [ ] Hard refreshed browser (Ctrl+Shift+R)
- [ ] Opened browser console (F12)
- [ ] Navigated to Capsule Endoscopy page
- [ ] Saw "Capsule endoscopy ready" in console
- [ ] Saw "Start button event listener attached" in console
- [ ] Clicked Start button
- [ ] Saw "Start button clicked!" in console
- [ ] Saw "Starting capsule endoscopy: scenario=mixed" in console

**Where did it stop?** That's where the problem is!

---

## Share Console Output

If it still doesn't work, please share:

1. **Full console output** from when you click Capsule Endoscopy
2. **Any red error messages**
3. **Network tab** - is capsule_endoscopy.js loading?
4. **Does the test page work?** (test_capsule_api.html)

With this info, I can pinpoint the exact issue!

---

**Status:** Debugging mode enabled ✅  
**Files Modified:** ui/capsule_endoscopy.js  
**Test Page:** http://localhost:8000/test_capsule_api.html  
**Next Step:** Hard refresh and check console!

