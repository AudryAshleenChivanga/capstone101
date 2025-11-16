# 🎥 Two-User Video Consultation Testing Guide

## ⚠️ Important: Why You Can't Use Same Browser Tabs

The authentication system uses **localStorage** to store login tokens. When you login as a different user in another tab of the **same browser**, it overwrites the previous user's token, logging them out.

---

## ✅ Solution: Use TWO Different Methods

Choose **ONE** of these methods to test with two users:

### Method 1: Two Different Browsers (EASIEST ⭐)

**User 1 (Clinician):**
- Use **Chrome**
- Go to: http://localhost:8001/login.html
- Login as: `dr_john` / `clinician123`

**User 2 (Specialist):**
- Use **Edge** (or Firefox)
- Go to: http://localhost:8001/login.html
- Login as: `dr_sarah` / `specialist123`

✅ Both users stay logged in independently!

---

### Method 2: Regular + Incognito Mode

**User 1 (Clinician):**
- Use **Regular Chrome window**
- Go to: http://localhost:8001/login.html
- Login as: `dr_john` / `clinician123`

**User 2 (Specialist):**
- Use **Chrome Incognito window** (Ctrl+Shift+N)
- Go to: http://localhost:8001/login.html
- Login as: `dr_sarah` / `specialist123`

✅ Incognito mode has separate localStorage!

---

### Method 3: Two Browser Profiles

**Create two Chrome profiles:**
1. Click your profile icon (top-right in Chrome)
2. Click "Add"
3. Create "Profile 1" and "Profile 2"
4. Each profile has its own localStorage

Then use one profile per user.

---

## 🚀 Complete Video Test Workflow

### Step 1: Setup (2 min)

**Register Clinician (if not done):**
```bash
python register_clinician.py
```

**Open Two Browsers:**
- Browser 1: Chrome → http://localhost:8001/login.html
- Browser 2: Edge → http://localhost:8001/login.html

---

### Step 2: Login Both Users (1 min)

**Browser 1 (Chrome) - Clinician:**
- Username: `dr_john`
- Password: `clinician123`
- ✅ You're logged in as Dr. John

**Browser 2 (Edge) - Specialist:**
- Username: `dr_sarah`
- Password: `specialist123`
- ✅ You're logged in as Dr. Sarah

---

### Step 3: Book Appointment (2 min)

**In Browser 1 (Clinician - Dr. John):**

1. Click **"Video Consultation"** in sidebar
2. Click **"Book Appointment"** tab
3. You'll see **Dr. Sarah Martinez** with her photo
4. Click **"Book Appointment"** button on her card
5. Fill in the modal form:
   - **Date & Time:** Tomorrow at 10:00 AM
   - **Reason:** "H. pylori treatment consultation"
   - **Notes:** "Patient with antibiotic resistance"
6. Click **"Request Appointment"**
7. ✅ Success! Appointment requested
8. Click **"My Requests"** tab to see your pending request

---

### Step 4: Approve Appointment (2 min)

**In Browser 2 (Specialist - Dr. Sarah):**

1. Click **"Video Consultation"** in sidebar
2. You should see **4 tabs** (specialists get extra "Pending Requests" tab)
3. Click **"Pending Requests"** tab
4. You'll see the appointment from Dr. John:
   - Clinician: Dr. John Doe
   - Date/Time
   - Reason: "H. pylori treatment consultation"
   - Notes: "Patient with antibiotic resistance"
5. Click **"Accept"** button
6. A modal appears - adjust date/time if needed
7. Add optional notes: "Looking forward to the consultation"
8. Click **"Confirm Acceptance"**
9. ✅ Success! Appointment accepted
10. Click **"Upcoming"** tab
11. You'll see the appointment with a green **"Join Video Session"** button

---

### Step 5: Join Video Call (3 min)

**In Browser 2 (Specialist - Dr. Sarah):**

1. In **"Upcoming"** tab, click **"Join Video Session"**
2. **New window opens:** http://localhost:8001/video.html?session=...
3. Browser asks: **"Allow camera and microphone?"**
4. Click **"Allow"** ✅
5. You'll see:
   - ✅ Your video feed (bottom-right corner)
   - ✅ Main video area (waiting for participant)
   - ✅ Session info in sidebar
   - ✅ Connection status: "Connected" (green dot)

**KEEP THIS WINDOW OPEN!** 🔴

**In Browser 1 (Clinician - Dr. John):**

6. Click **"Video Consultation"** → **"Upcoming"** tab
7. You'll see the accepted appointment
8. Click **"Join Video Session"**
9. **New window opens**
10. Allow camera and microphone permissions
11. **BOOM! 🎉 Both users can now see each other!**

---

### Step 6: Test Video Features (2 min)

**In Specialist Window (Dr. Sarah):**
- Click **"Video"** button → Camera turns off ⚪
- Click again → Camera turns back on 🟢
- Click **"Audio"** button → Muted 🔇
- Click again → Unmuted 🔊

**In Clinician Window (Dr. John):**
- Do the same tests
- Verify the other person sees/hears the changes

**Both Windows:**
- View participant list in sidebar
- See session information
- View connection status

**End Call:**
- Click **"End"** button in any window
- Confirm "Are you sure?"
- Both return to dashboard

---

## 🎯 Expected Results

### ✅ What You Should See:

1. **Both browsers stay logged in as different users**
2. **Appointment booking works smoothly**
3. **Specialist sees pending request**
4. **Approval workflow completes**
5. **Both get "Join Video Session" button**
6. **Video windows open with correct URL:**
   ```
   http://localhost:8001/video.html?session=...&token=...
   ```
   ❌ NOT: ~~http://localhost:3000/ui/video.html~~ (old/wrong)

7. **Camera/microphone permissions granted**
8. **Both users see each other in HD video**
9. **Audio works clearly**
10. **Controls function properly**

---

## 🐛 Troubleshooting

### Issue: "Logged out in other tab"
**Cause:** Using same browser without separate profiles/incognito
**Solution:** Use Method 1 (two browsers) or Method 2 (incognito)

### Issue: Wrong video URL (port 3000)
**Status:** ✅ FIXED! Backend was just restarted
**Solution:** Video URLs now correctly use http://localhost:8001

### Issue: "ERR_CONNECTION_REFUSED" on video.html
**Cause:** UI server not running on port 8001
**Solution:** Check PowerShell window showing "Serving HTTP on 0.0.0.0 port 8001"

### Issue: Can't see other participant
**Cause:** Only one user joined, or WebRTC connection issue
**Solution:**
1. Make sure BOTH users clicked "Join Video Session"
2. Both must allow camera/microphone
3. Wait 5-10 seconds for connection to establish
4. Check browser console (F12) for errors

### Issue: No camera/microphone access
**Solution:**
1. Click the lock icon in address bar
2. Allow camera and microphone
3. Refresh the video page
4. Check if another app is using the camera

---

## 📋 Quick Checklist

Before starting the test:

- [ ] Backend running on port 8000 ✅
- [ ] UI server running on port 8001 ✅
- [ ] Two different browsers ready (Chrome + Edge)
- [ ] Clinician registered (`dr_john`)
- [ ] Specialist registered (`dr_sarah`)

During test:

- [ ] Both users logged in (different browsers)
- [ ] Appointment booked by clinician
- [ ] Appointment accepted by specialist
- [ ] Both users see "Join Video Session" button
- [ ] Both users join video call
- [ ] Camera/microphone permissions granted
- [ ] Both users see each other
- [ ] Audio works both ways
- [ ] Video controls work
- [ ] Call ends cleanly

---

## 🎉 Success!

You've successfully completed the test when:

✅ Two users are logged in simultaneously (different browsers)
✅ Appointment workflow completed (book → approve → confirm)
✅ Video call established between both users
✅ Both can see and hear each other
✅ Controls work (mute/unmute, video on/off)
✅ Call ends properly

---

## 💡 Pro Tips

1. **Keep server windows open** - Don't close the PowerShell windows
2. **Use Chrome/Edge** - Best WebRTC support
3. **Check permissions** - Allow camera/mic when prompted
4. **Wait for connection** - WebRTC needs 5-10 seconds
5. **Test on same network** - Works best on localhost/LAN

---

## 🚀 Next Steps

After successful testing:

1. **Add more users** - Register additional clinicians/specialists
2. **Test edge cases** - Cancel, reject, reschedule
3. **Production setup** - Add TURN server for cross-network
4. **Enhancements** - Screen sharing, recording, chat

---

**Happy Video Consulting! 🩺📹**

Both servers are now running correctly. Follow this guide for successful testing!

