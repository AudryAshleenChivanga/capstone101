# 🎥 Video Consultation - End-to-End Testing Guide

## 📋 System Overview

The H. pylori CDSS video consultation system uses WebRTC for peer-to-peer video calls with the following workflow:

```
1. Book Appointment → 2. Accept Appointment → 3. Create Video Session → 4. Join Call
```

---

## 🧪 **End-to-End Testing Steps**

### **Prerequisites**
✅ Server running: `python -m uvicorn main:app --reload`
✅ Two users (or two browser windows/incognito for testing):
   - **Clinician** (requester)
   - **Specialist** (acceptor)

---

## **Step 1: Create Users (If Not Already Done)**

### Option A: Using Admin Panel
1. Login as admin
2. Go to Admin Panel
3. Create two users:
   - User 1: `clinician1` (role: clinician)
   - User 2: `specialist1` (role: specialist)

### Option B: Using Registration Endpoint
```bash
# Register Clinician
curl -X POST http://127.0.0.1:8000/auth/register/public \
  -H "Content-Type: application/json" \
  -d '{
    "username": "clinician1",
    "email": "clinician1@test.com",
    "password": "test123",
    "full_name": "Dr. John Clinician"
  }'

# Promote to specialist (need admin)
# Login as admin and change role in Admin Panel
```

---

## **Step 2: Book an Appointment**

### **As Clinician:**

1. **Login**: `http://127.0.0.1:8000/ui/login.html`
   - Username: `clinician1`
   - Password: `test123`

2. **Navigate to Video Consult**:
   - Click "Video Consult" in sidebar
   - You'll see the "Book Consultation" tab

3. **View Available Specialists**:
   - Should see list of specialists
   - Each card shows:
     - Name
     - Specialty (Gastroenterology)
     - Email
     - Phone
     - "Book Consultation" button

4. **Book Appointment**:
   - Click "Book Consultation" on a specialist
   - Fill in the modal:
     - **Appointment Date**: Select future date/time
     - **Case ID** (optional): Link to existing case
     - **Reason**: "Follow-up consultation for H. pylori treatment"
   - Click "Send Request"
   - ✅ Success message: "Consultation request sent successfully"

5. **Verify Request Sent**:
   - Go to "My Requests" tab
   - Should see your appointment with status: **"Pending"**

---

## **Step 3: Accept Appointment**

### **As Specialist:**

1. **Login** (in new browser window/incognito):
   - URL: `http://127.0.0.1:8000/ui/login.html`
   - Username: `specialist1`
   - Password: `test123`

2. **Navigate to Video Consult**:
   - Click "Video Consult" in sidebar
   - Should see **3 tabs** (specialists have an extra tab):
     - Book Consultation
     - My Requests
     - **Pending Requests** ← New tab for specialists

3. **View Pending Requests**:
   - Click "Pending Requests" tab
   - Should see appointment request from clinician1
   - Shows:
     - Requesting clinician name
     - Date & time
     - Reason
     - Status: "Pending"
     - Action buttons: **Accept** | **Decline**

4. **Accept the Appointment**:
   - Click "Accept" button
   - ✅ Success: "Appointment accepted successfully"
   - Status changes to: **"Accepted"**

---

## **Step 4: Create Video Session**

### **As Either User (Clinician or Specialist):**

1. **Go to "Upcoming Sessions" Tab**:
   - Both users should now see the accepted appointment
   - Shows:
     - Date & time
     - Other participant's name
     - Case ID (if linked)
     - Status: "Accepted"
     - **"Start Video Call"** button (enabled only if accepted)

2. **Start Video Call**:
   - Click "Start Video Call"
   - System creates WebRTC session
   - Generates unique room ID
   - Creates host and guest tokens
   - Opens video call in new window/tab

**API Endpoint Called:**
```
POST /video/session/create
{
  "appointment_id": 123,
  "case_id": 456 (optional),
  "session_name": "consultation_abc123"
}
```

**Response:**
```json
{
  "session_id": "uuid-here",
  "room_name": "consultation_abc123",
  "host_token": "secure-token-1",
  "guest_token": "secure-token-2",
  "join_url_host": "http://127.0.0.1:8001/video.html?session=uuid&token=host-token",
  "join_url_guest": "http://127.0.0.1:8001/video.html?session=uuid&token=guest-token",
  "qr_code_url": "/video/session/uuid/qr?token=guest-token",
  "expires_at": "2025-11-24T10:00:00",
  "status": "active"
}
```

---

## **Step 5: Join Video Call**

### **Testing Video Connection:**

1. **First User (Host) Auto-Joins**:
   - Browser opens `video.html?session=xxx&token=host-token`
   - Camera/microphone permission requested
   - Video preview shows
   - "Waiting for participants..." message

2. **Second User (Guest) Joins**:
   - Copy the guest URL from the first user's session
   - OR click "Join Call" if they also see it in their upcoming sessions
   - Opens `video.html?session=xxx&token=guest-token`
   - Camera/microphone permission requested

3. **WebRTC Connection Established**:
   - Both users see each other's video
   - Audio enabled
   - Controls available:
     - 🎤 Mute/Unmute microphone
     - 📹 Enable/Disable camera
     - 🔊 Volume controls
     - 📞 End call

---

## **Step 6: Test Video Features**

### **During Call:**

✅ **Video Quality**:
   - Both video streams visible
   - Smooth playback (depends on network)
   - Proper resolution

✅ **Audio**:
   - Clear two-way audio
   - No echo (if using headphones)
   - Mute/unmute works

✅ **Controls**:
   - Toggle camera on/off
   - Toggle microphone on/off
   - End call button works

✅ **Session Management**:
   - Session ID tracked
   - Tokens validated
   - Participants list updated

---

## **Step 7: End Call & Verify Cleanup**

1. **End Call**:
   - Click "End Call" button
   - Video stops
   - Connection closes
   - Redirect back to dashboard (optional)

2. **Check Backend**:
   - Session marked as ended
   - Database updated (if using DB persistence)
   - Memory cleaned up

---

## 🔍 **Testing Checklist**

### **Appointment Workflow:**
- [ ] Clinician can see all specialists
- [ ] Booking form validates inputs
- [ ] Appointment request created successfully
- [ ] Specialist receives pending request
- [ ] Specialist can accept/decline
- [ ] Both users see accepted appointment in "Upcoming Sessions"

### **Video Session Creation:**
- [ ] "Start Video Call" only enabled for accepted appointments
- [ ] Session created with unique ID
- [ ] Host and guest tokens generated
- [ ] Join URLs created correctly
- [ ] QR code generated (optional feature)
- [ ] Session expires in 2 hours

### **WebRTC Connection:**
- [ ] Camera permission requested
- [ ] Microphone permission requested
- [ ] Local video preview works
- [ ] Remote video stream received
- [ ] Two-way audio works
- [ ] Controls functional (mute, camera toggle)
- [ ] End call works cleanly

### **Error Handling:**
- [ ] Cannot create session for non-accepted appointment
- [ ] Invalid tokens rejected
- [ ] Expired sessions blocked
- [ ] Unauthorized users cannot join
- [ ] Network errors handled gracefully

---

## 🐛 **Common Issues & Fixes**

### **Issue 1: "Appointment must be accepted" Error**
**Cause**: Trying to start video call on pending appointment
**Fix**: Specialist must accept the appointment first

### **Issue 2: Camera/Microphone Not Working**
**Cause**: Browser permissions denied
**Fix**: 
- Check browser settings
- Allow camera/microphone for localhost
- Use HTTPS in production (required for WebRTC)

### **Issue 3: No Video Stream**
**Cause**: WebRTC connection failed
**Fix**:
- Check firewall settings
- Ensure both users on same network (for testing)
- Check browser console for errors
- Verify STUN/TURN servers configured (for production)

### **Issue 4: "Session not found" Error**
**Cause**: Session expired or invalid token
**Fix**:
- Sessions expire in 2 hours
- Create new session
- Check token is correct in URL

---

## 📊 **Backend API Endpoints**

### **Session Management:**
```
POST   /video/session/create          - Create new video session
GET    /video/session/{session_id}    - Get session details
DELETE /video/session/{session_id}    - End session
GET    /video/session/{session_id}/qr - Get QR code for joining
```

### **WebRTC Signaling:**
```
POST   /video/signal/offer             - Send WebRTC offer
POST   /video/signal/answer            - Send WebRTC answer
POST   /video/signal/ice-candidate     - Exchange ICE candidates
```

### **Appointment Management:**
```
GET    /appointments/specialists       - List all specialists
POST   /appointments/request           - Request appointment
PUT    /appointments/{id}/accept       - Accept appointment
PUT    /appointments/{id}/decline      - Decline appointment
GET    /appointments/my-requests       - My appointment requests
GET    /appointments/pending-requests  - Pending requests (specialists)
GET    /appointments/upcoming          - Upcoming accepted appointments
```

---

## 🧪 **Quick Test Script**

```bash
# 1. Create appointment (as clinician1)
curl -X POST http://127.0.0.1:8000/appointments/request \
  -H "Authorization: Bearer YOUR_CLINICIAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "specialist_id": 2,
    "appointment_date": "2025-11-25T10:00:00",
    "reason": "H. pylori follow-up",
    "case_id": 1
  }'

# 2. Accept appointment (as specialist1)
curl -X PUT http://127.0.0.1:8000/appointments/1/accept \
  -H "Authorization: Bearer YOUR_SPECIALIST_TOKEN"

# 3. Create video session (as either user)
curl -X POST http://127.0.0.1:8000/video/session/create \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "appointment_id": 1,
    "session_name": "Test Consultation"
  }'

# 4. Get session info
curl -X GET http://127.0.0.1:8000/video/session/SESSION_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## ✅ **Success Criteria**

### **End-to-End Test Passes If:**

1. ✅ Clinician can book appointment with specialist
2. ✅ Specialist receives and accepts appointment
3. ✅ Both users see appointment in upcoming sessions
4. ✅ Video session created successfully
5. ✅ Both users can join with their respective URLs
6. ✅ Video and audio work bidirectionally
7. ✅ Controls (mute, camera, end call) functional
8. ✅ Session tracked in database
9. ✅ Clean disconnection when call ends
10. ✅ No console errors or crashes

---

## 🚀 **Next Steps**

- [ ] Test on different browsers (Chrome, Firefox, Safari)
- [ ] Test on mobile devices
- [ ] Test with poor network conditions
- [ ] Add screen sharing feature
- [ ] Add chat during video call
- [ ] Add recording capability (if needed)
- [ ] Deploy to production with HTTPS
- [ ] Configure STUN/TURN servers for production

---

**Video Consultation System: Ready for Testing!** 🎥

