# Video Consultation System - Complete Setup & Usage Guide

## ✅ What's Been Implemented

The H. pylori CDSS now has a complete video consultation system with:

1. **Specialist Registration** - Easy-to-use registration form for gastroenterology specialists
2. **Appointment Scheduling** - Clinicians can book appointments with specialists
3. **Approval Workflow** - Specialists can view, approve, or reject appointment requests
4. **Live Video Calls** - WebRTC-based video consultations with audio/video controls
5. **Status Tracking** - Real-time appointment status updates and notifications

---

## 📋 Prerequisites

1. Make sure your FastAPI server is running:
   ```bash
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Make sure your UI server is running:
   ```bash
   cd ui
   python -m http.server 8001
   ```

3. Access the application at: `http://localhost:8001/dashboard_new.html`

---

## 🚀 Quick Start: Testing the Complete Workflow

### Step 1: Register a Specialist

**Option A: Use the Web Form** (Recommended)
1. Open: `http://localhost:8001/register_specialist.html`
2. Fill in the specialist information:
   - **Username**: `dr_sarah` (or any username)
   - **Email**: `sarah@hospital.com`
   - **Password**: `specialist123`
   - **Full Name**: `Dr. Sarah Martinez`
   - **Specialty**: `Gastroenterology`
   - **Institution**: `Central Medical Hospital`
   - **Bio**: `10 years of experience in gastroenterology...`
3. Click "Register Specialist"
4. You'll be redirected to the login page

**Option B: Use Python Script** (For multiple specialists)
```bash
python register_specialist.py
```
Follow the prompts to create a specialist account.

**Option C: Via API** (Advanced)
```bash
curl -X POST http://localhost:8000/auth/register/first \
  -H "Content-Type: application/json" \
  -d '{
    "username": "dr_sarah",
    "email": "sarah@hospital.com",
    "password": "specialist123",
    "full_name": "Dr. Sarah Martinez",
    "specialty": "Gastroenterology",
    "institution": "Central Medical Hospital",
    "role": "specialist"
  }'
```

### Step 2: Login as Clinician

1. Go to: `http://localhost:8001/login.html`
2. Login with your existing clinician account (or create one if needed)
3. You'll be redirected to the dashboard

### Step 3: Book an Appointment

1. In the dashboard, click **"Video Consultation"** in the sidebar
2. You'll see three tabs:
   - **Book Appointment**: See available specialists
   - **My Requests**: View your pending/sent appointment requests
   - **Upcoming**: View confirmed appointments

3. In the **Book Appointment** tab:
   - You'll see the registered specialist (Dr. Sarah Martinez)
   - Click **"Book Appointment"**
   
4. Fill in the booking form:
   - **Preferred Date & Time**: Select a future date/time
   - **Related Case**: (Optional) Link to an existing case
   - **Urgency Level**: Normal, Urgent, or Emergency
   - **Reason**: Describe why you need the consultation
   - **Additional Notes**: Any extra information

5. Click **"Request Appointment"**
6. You'll see a success message and the appointment appears in "My Requests"

### Step 4: Approve the Appointment (As Specialist)

1. **Logout** from the clinician account (click your name → Sign Out)
2. **Login** as the specialist:
   - Username: `dr_sarah`
   - Password: `specialist123`

3. Go to **"Video Consultation"** in the sidebar
4. You'll see **four tabs** (specialists have an extra "Pending Requests" tab):
   - Book Appointment
   - My Requests
   - Upcoming
   - **Pending Requests** ⬅️ This is specialist-only

5. Click the **"Pending Requests"** tab
6. You'll see the appointment request from the clinician
7. Review the details:
   - Clinician name
   - Requested date/time
   - Reason for consultation
   - Any notes

8. Click **"Accept"**
9. A modal will appear:
   - Adjust the scheduled date/time if needed
   - Add notes for the clinician (optional)
   - Click **"Confirm Acceptance"**

10. The appointment is now **accepted** ✅

### Step 5: Join the Video Consultation

**As Clinician or Specialist:**

1. Login to your account
2. Go to **"Video Consultation"** → **"Upcoming"** tab
3. You'll see the accepted appointment with a green **"Join Video Session"** button
4. Click **"Join Video Session"**
5. A new window opens with the video consultation interface

**In the Video Room:**
- **Main Video Area**: Shows the remote participant
- **Local Video**: Your camera feed (bottom-right corner)
- **Controls**:
  - 🎥 **Video**: Toggle your camera on/off
  - 🎤 **Audio**: Toggle your microphone on/off
  - 🔴 **End**: End the consultation
- **Sidebar**:
  - Session info (room name, host, your role)
  - Participant list
  - Invite link (to share with others)
  - Quick actions

6. The browser will request camera/microphone permissions - **click "Allow"**
7. Your video feed will appear in the bottom-right corner
8. Wait for the other participant to join
9. Once both participants are in, you can see and hear each other
10. Use the controls to mute/unmute or turn video on/off
11. Click **"End"** when consultation is complete

---

## 🎯 Key Features

### For Clinicians:
- ✅ Browse available gastroenterology specialists
- ✅ Book appointments with preferred specialists
- ✅ View appointment request status (pending, accepted, rejected)
- ✅ Join video calls for accepted appointments
- ✅ Cancel pending appointment requests

### For Specialists:
- ✅ View all pending appointment requests
- ✅ Accept or reject requests with custom notes
- ✅ Adjust appointment date/time when accepting
- ✅ View upcoming confirmed appointments
- ✅ Join video calls for accepted appointments
- ✅ Professional profile display for clinicians

### For Both:
- ✅ Real-time video and audio communication
- ✅ Toggle camera and microphone
- ✅ Copy and share invite links
- ✅ View participant information
- ✅ End call functionality
- ✅ Return to dashboard after consultation

---

## 📁 Files Modified/Created

### New Files:
1. `ui/register_specialist.html` - Specialist registration form
2. `VIDEO_CONSULTATION_SETUP.md` - This guide

### Modified Files:
1. `ui/dashboard_new.html` - Added "Pending Requests" tab for specialists
2. `ui/video_consult.js` - Added specialist approval functions and video session joining
3. `ui/video.html` - Fixed API URLs and improved video call interface

### Backend Files (Already Existed):
- `app/routes_video.py` - Video session management
- `app/routes_scheduling.py` - Appointment scheduling and approval
- `app/models.py` - Database models for appointments and sessions

---

## 🔧 API Endpoints Used

### Authentication:
- `POST /auth/register/first` - Register first user (specialist)
- `POST /auth/login` - Login

### Scheduling:
- `GET /appointments/specialists` - Get list of specialists
- `POST /scheduling/appointments` - Create appointment request
- `GET /appointments/my-requests` - Get clinician's requests
- `GET /appointments/my-appointments` - Get upcoming appointments
- `GET /scheduling/pending` - Get pending requests (specialists only)
- `PUT /scheduling/appointments/{id}/respond` - Accept/reject appointment
- `PUT /scheduling/appointments/{id}/cancel` - Cancel appointment

### Video:
- `POST /video/session/create` - Create video session
- `GET /video/session/{id}` - Get session info
- `POST /video/session/{id}/end` - End video session

---

## 🐛 Troubleshooting

### Issue: "No specialists available"
**Solution**: Make sure you've registered at least one specialist using the registration form or script.

### Issue: "Failed to create video session: Cannot create video session. Appointment status is 'pending'"
**Solution**: The specialist must **accept** the appointment first before you can join the video call.

### Issue: Camera/microphone not working
**Solution**: 
1. Check browser permissions
2. Make sure you're using HTTPS or localhost (getUserMedia requires secure context)
3. Try a different browser (Chrome/Edge recommended)

### Issue: "Invalid session link"
**Solution**: Join the video call through the "Upcoming" tab, not by manually entering a URL.

### Issue: "Pending Requests tab not showing"
**Solution**: Make sure you're logged in as a user with the "specialist" role.

### Issue: Registration fails with "First user already registered"
**Solution**: This means the database already has users. You need admin privileges to register more specialists. Use the admin panel or contact an existing admin.

---

## 🎓 Usage Tips

1. **Best Practice**: Schedule appointments at least a few hours in advance
2. **Testing**: You can open two browser windows (one incognito) to test as both clinician and specialist
3. **Network**: For production, you'll need a TURN server for WebRTC to work across different networks
4. **Mobile**: The interface is responsive and works on mobile devices
5. **Recordings**: Currently not implemented, but can be added by storing video streams

---

## 📞 Next Steps

To complete the video consultation system:

1. **Add Email Notifications** - Notify specialists when they receive appointment requests
2. **Add SMS Reminders** - Send reminders before appointments
3. **Implement Screen Sharing** - Allow sharing clinical data during consultations
4. **Add Chat Feature** - Text chat alongside video
5. **Record Consultations** - Save recordings for future reference (with consent)
6. **Add Calendar Integration** - Sync with Google Calendar/Outlook
7. **Implement TURN Server** - For production WebRTC across networks

---

## ✨ System Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│  Clinician  │────────▶│   FastAPI    │◀────────│  Specialist │
│  Dashboard  │         │   Backend    │         │  Dashboard  │
└─────────────┘         └──────────────┘         └─────────────┘
       │                       │                         │
       │                       │                         │
       ▼                       ▼                         ▼
  ┌──────────┐          ┌──────────┐             ┌──────────┐
  │  Book    │          │  SQLite  │             │  Approve │
  │ Appoint. │          │ Database │             │  Request │
  └──────────┘          └──────────┘             └──────────┘
       │                       │                         │
       └───────────────────────┴─────────────────────────┘
                               │
                               ▼
                      ┌─────────────────┐
                      │  Video Session  │
                      │   (WebRTC)      │
                      └─────────────────┘
```

---

## 🎉 Congratulations!

You now have a fully functional video consultation system integrated into your H. pylori CDSS! 

Clinicians can schedule consultations with specialists, specialists can approve them, and both can conduct live video calls for remote medical consultations.

**Happy Consulting! 🩺📹**

