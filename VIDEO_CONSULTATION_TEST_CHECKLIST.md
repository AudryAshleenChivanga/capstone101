# Video Consultation Testing Checklist ✅

## Quick Test Guide (15 minutes)

### 🚀 Prerequisites
- [ ] Backend running: `python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000`
- [ ] Frontend running: `cd ui && python -m http.server 8001`

---

## Test 1: Register a Specialist (5 min)

### Method 1: Quick Script (Recommended)
```bash
python quick_register_specialist.py
```

### Method 2: Web Form
1. [ ] Go to: `http://localhost:8001/register_specialist.html`
2. [ ] Fill in the form with specialist details
3. [ ] Click "Register Specialist"
4. [ ] Verify redirect to login page

**Expected Result:** ✅ Specialist account created successfully

**Credentials for Testing:**
- Username: `dr_sarah`
- Password: `specialist123`

---

## Test 2: Book an Appointment as Clinician (3 min)

1. [ ] Login as clinician at `http://localhost:8001/login.html`
2. [ ] Go to **"Video Consultation"** in sidebar
3. [ ] Click **"Book Appointment"** tab
4. [ ] Verify you see "Dr. Sarah Martinez" with:
   - Name, specialty, institution
   - Email and phone
   - "Book Appointment" button
5. [ ] Click **"Book Appointment"**
6. [ ] Fill in booking form:
   - Date & Time: Tomorrow at 10:00 AM
   - Urgency: Normal
   - Reason: "H. pylori treatment consultation"
   - Notes: "Patient has antibiotic resistance"
7. [ ] Click **"Request Appointment"**
8. [ ] Verify success toast notification
9. [ ] Click **"My Requests"** tab
10. [ ] Verify appointment appears with status "pending"

**Expected Result:** ✅ Appointment request created and visible

---

## Test 3: Approve Appointment as Specialist (3 min)

1. [ ] Click user name → **"Sign Out"**
2. [ ] Login as specialist:
   - Username: `dr_sarah`
   - Password: `specialist123`
3. [ ] Go to **"Video Consultation"**
4. [ ] Verify you see **4 tabs** (including "Pending Requests")
5. [ ] Click **"Pending Requests"** tab
6. [ ] Verify you see the appointment request with:
   - Clinician name
   - Requested date/time
   - Reason
   - "Accept" and "Reject" buttons
7. [ ] Click **"Accept"**
8. [ ] In the modal:
   - Verify scheduled date is pre-filled
   - Optionally adjust date/time
   - Add notes: "Looking forward to the consultation"
   - Click **"Confirm Acceptance"**
9. [ ] Verify success toast notification
10. [ ] Verify request disappears from "Pending Requests"
11. [ ] Click **"Upcoming"** tab
12. [ ] Verify appointment appears with:
    - Status "accepted"
    - Green "Join Video Session" button

**Expected Result:** ✅ Appointment approved and ready for video call

---

## Test 4: Join Video Consultation (4 min)

### As Specialist:
1. [ ] In **"Upcoming"** tab, click **"Join Video Session"**
2. [ ] New window opens
3. [ ] Browser asks for camera/microphone permissions
4. [ ] Click **"Allow"**
5. [ ] Verify you see:
   - Your video feed (bottom-right corner)
   - Main video area (waiting for participant)
   - Session info in sidebar (Room name, Host name, Role)
   - Controls (Video, Audio, End buttons)
6. [ ] Leave this window open
7. [ ] Copy the invite link from the sidebar

### As Clinician:
8. [ ] Logout from specialist and login as clinician
9. [ ] Go to **"Video Consultation"** → **"Upcoming"**
10. [ ] Verify you see the accepted appointment
11. [ ] Click **"Join Video Session"**
12. [ ] New window opens
13. [ ] Allow camera/microphone permissions
14. [ ] Verify you see:
    - Your video feed (bottom-right)
    - Specialist's video feed (main area)
    - Connection status: "Connected" (green dot)
    - Both participants listed in sidebar

### Test Video Call Features:
15. [ ] Click **"Video"** button to toggle camera off/on
16. [ ] Verify local video stops/starts
17. [ ] Click **"Audio"** button to mute/unmute
18. [ ] Verify button changes to "Muted"/"Audio"
19. [ ] Test in both windows
20. [ ] Click **"Back to Dashboard"** button
21. [ ] Verify redirect to dashboard
22. [ ] Click **"End"** button in other window
23. [ ] Confirm end consultation
24. [ ] Verify redirect to dashboard

**Expected Result:** ✅ Video call works with audio/video controls

---

## ✅ Success Criteria

All tests passed if:
- ✅ Specialist can be registered
- ✅ Clinician can book appointments
- ✅ Specialist sees pending requests
- ✅ Specialist can approve appointments
- ✅ Both users see "Join Video Session" button
- ✅ Video call window opens with camera/microphone access
- ✅ Both participants can see each other
- ✅ Video and audio can be toggled
- ✅ Call can be ended properly

---

## 🐛 Common Issues & Solutions

### Issue: "No specialists available"
**Solution:** Register a specialist first using `quick_register_specialist.py`

### Issue: Can't join video - "Appointment status is 'pending'"
**Solution:** Specialist must **accept** the appointment first

### Issue: Camera not working
**Solution:** 
1. Check browser permissions (allow camera/mic)
2. Use Chrome/Edge (better WebRTC support)
3. Ensure you're on `localhost` (getUserMedia requires secure context)

### Issue: "Pending Requests" tab not visible
**Solution:** Make sure you're logged in as a user with role="specialist"

### Issue: Video window blank/black
**Solution:**
1. Reload the page
2. Check console for errors
3. Try different browser
4. Check if camera is being used by another app

---

## 📊 Test Results

Date: ___________

| Test | Status | Notes |
|------|--------|-------|
| Specialist Registration | ⬜ Pass ⬜ Fail | |
| Appointment Booking | ⬜ Pass ⬜ Fail | |
| Appointment Approval | ⬜ Pass ⬜ Fail | |
| Video Call | ⬜ Pass ⬜ Fail | |
| Audio/Video Toggle | ⬜ Pass ⬜ Fail | |
| End Call | ⬜ Pass ⬜ Fail | |

---

## 🎉 Next Steps After Testing

Once all tests pass:

1. **Production Deployment:**
   - Add TURN/STUN servers for cross-network video
   - Set up SSL/TLS certificates (HTTPS required)
   - Configure environment variables
   - Deploy to cloud (AWS, Azure, Heroku, etc.)

2. **Additional Features:**
   - Email notifications for appointment requests
   - SMS reminders before appointments
   - Screen sharing for clinical data
   - Chat feature alongside video
   - Recording functionality (with consent)
   - Calendar integration

3. **Security Enhancements:**
   - End-to-end encryption for video
   - HIPAA compliance measures
   - Audit logs for consultations
   - Session timeouts

4. **User Experience:**
   - Mobile app support
   - Waiting room feature
   - Virtual backgrounds
   - Connection quality indicators
   - Bandwidth adaptation

---

## 📞 Support

If you encounter issues not covered here:

1. Check the console for error messages
2. Review `VIDEO_CONSULTATION_SETUP.md` for detailed setup
3. Check backend logs: Look at the terminal running uvicorn
4. Check frontend logs: Open browser DevTools (F12) → Console tab

**Happy Testing! 🩺📹**

