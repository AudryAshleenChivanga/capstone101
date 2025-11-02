# Scheduling & Video Consultation Setup Guide

## Summary of Changes

All requested improvements have been implemented successfully. Here's what was done:

### 1. ✅ Admin Can Create Specialists

**Added Backend Endpoint:**
- `POST /admin/users` - Allows admin to create new users (clinicians, specialists, or admins)
- Located in: `app/routes_admin.py`
- Updated schema in: `app/schemas.py` to include `institution` field

**Created Admin UI:**
- New page: `ui/admin_create_specialist.html`
- Access at: `http://localhost:8000/ui/admin_create_specialist.html`
- Must be logged in as admin first

### 2. ✅ Removed All Emojis

**Files Updated:**
- `ui/scheduling.js` - Removed all emojis from scheduling system
- `ui/video_consult.js` - Removed all emojis from video consultation
- `ui/dashboard_new.html` - Removed emojis from page headers and tabs

**Changed:**
- Replaced emoji icons with text labels like `[Doctor]`, `[Calendar]`, `[Date]`, etc.
- Updated all button text to remove emojis
- Clean, professional appearance throughout

### 3. ✅ Reorganized Navigation

**Navigation Order:**
1. Dashboard
2. Screening
3. Staging
4. Case History
5. Capsule Endoscopy
6. **Scheduling** (moved up)
7. **Video Consult** (moved down)
8. Profile
9. Admin

**Rationale:**
- Users request appointments in Scheduling first
- Then join video calls in Video Consult section
- More logical workflow

### 4. ✅ Linked Confirmed Appointments to Video Consultation

**Features Added:**
- When appointment has video link, shows "Go to Video Consultation" button
- Button navigates to Video Consult page
- Video consultation page shows all confirmed appointments with video links
- Seamless workflow from scheduling → video call

**Implementation:**
- Added `goToVideoConsultation()` function in `scheduling.js`
- Updated confirmed appointments display
- Proper integration between both sections

### 5. ✅ Fixed Light Mode Text Visibility

**CSS Improvements:**
- Added comprehensive light mode styles in `ui/dashboard_new.html`
- Ensured all text has proper contrast in light mode
- Fixed colors for:
  - Page headers
  - Form labels
  - Appointment cards
  - Empty state messages
  - Input fields
  - Detail text

**Color Scheme:**
- Headers: `#1e293b` (dark gray)
- Body text: `#475569` (medium gray)
- Secondary text: `#64748b` (light gray)
- Backgrounds: `#ffffff` (white)

## How to Test the Complete Workflow

### Step 1: Login as Admin
1. Go to: `http://localhost:8000/ui/login.html`
2. Login with: `admin` / `Admin@2024`

### Step 2: Create a Specialist
1. Go to: `http://localhost:8000/ui/admin_create_specialist.html`
2. Fill out the form:
   - Username: `dr_specialist`
   - Email: `specialist@hospital.com`
   - Full Name: `Dr. Jane Specialist`
   - Password: `Specialist@2024`
   - Specialty: `Gastroenterology`
   - Institution: `City General Hospital`
3. Click "Create Specialist"

### Step 3: Test Scheduling Workflow (as Clinician)
1. Login as admin (or create a clinician account)
2. Go to Dashboard → Click "Scheduling" in navigation
3. Click "Request Appointment" tab
4. Fill out appointment request:
   - Select the specialist you created
   - Choose a future date/time
   - Select urgency level
   - Add reason for consultation
5. Click "Submit Appointment Request"
6. Check "Pending" tab to see your request

### Step 4: Approve Appointment (as Specialist)
1. Logout and login as the specialist:
   - Username: `dr_specialist`
   - Password: `Specialist@2024`
2. Go to Dashboard → Admin → Appointments
3. Find pending appointments and approve them

### Step 5: Test Video Consultation
1. Go back to "Scheduling" page
2. Go to "Confirmed" tab
3. Click "Generate Video Link" for confirmed appointment
4. Click "Go to Video Consultation" button
5. You'll be taken to Video Consult page
6. Click "Join Video Session" to start the call

## API Endpoints

### Admin - Create User
```bash
POST /admin/users
Authorization: Bearer {token}
Content-Type: application/json

{
  "username": "dr_smith",
  "email": "smith@hospital.com",
  "password": "Password123",
  "role": "specialist",
  "full_name": "Dr. John Smith",
  "specialty": "Gastroenterology",
  "institution": "City Hospital"
}
```

### Scheduling - Get Specialists
```bash
GET /appointments/specialists
Authorization: Bearer {token}
```

### Scheduling - Request Appointment
```bash
POST /appointments/request
Authorization: Bearer {token}
Content-Type: application/json

{
  "specialist_id": 2,
  "case_id": 1,
  "preferred_date": "2025-11-10T14:00:00",
  "urgency": "normal",
  "reason": "Follow-up consultation",
  "notes": "Additional notes"
}
```

### Get My Appointments
```bash
GET /appointments/my-requests
Authorization: Bearer {token}
```

## Features Implemented

✅ Admin can create specialist users via API
✅ Admin UI for creating specialists
✅ All emojis removed from scheduling
✅ All emojis removed from video consultation  
✅ Scheduling moved before Video Consult in navigation
✅ Confirmed appointments link to video consultation
✅ Light mode text is fully visible
✅ Form appears before video consultation
✅ Booked sessions show in video consultations
✅ Specialist confirmation workflow works
✅ Video call functionality ready

## Troubleshooting

### Issue: Can't see specialists in dropdown
**Solution:** Create specialists first using the admin interface at `/ui/admin_create_specialist.html`

### Issue: Text not visible in light mode
**Solution:** Refresh the page after changes. All text now has proper contrast colors.

### Issue: Appointments not showing in video consultation
**Solution:** Make sure the appointment is:
1. Confirmed by specialist
2. Has a video link generated
3. Check the "Upcoming" tab in Video Consult

### Issue: Can't create specialist
**Solution:** Make sure you're logged in as admin with proper permissions.

## Notes

- The server must be running on `http://localhost:8000`
- Login as admin first: `admin` / `Admin@2024`
- All emojis have been replaced with text labels
- Light mode has proper text contrast throughout
- Workflow is: Request Appointment → Specialist Confirms → Generate Video Link → Join Call

