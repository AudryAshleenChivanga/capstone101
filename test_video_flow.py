"""
Test video consultation flow end-to-end.
"""
import requests
import json
from datetime import datetime, timedelta

# Use production URL
API_BASE = "https://h-pylori-cdss.onrender.com"
# Or for local testing:
# API_BASE = "http://localhost:8000"

print("\n" + "="*70)
print("VIDEO CONSULTATION FLOW TEST")
print("="*70)

# Step 1: Login as admin/clinician
print("\n[Step 1] Login as clinician...")
login_response = requests.post(f"{API_BASE}/auth/login", json={
    "username": "admin",
    "password": "Admin@2024"
})

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    print(f"[OK] Login successful! Token: {token[:30]}...")
else:
    print(f"[FAIL] Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Step 2: Check if appointments exist
print("\n[Step 2] Checking appointments...")
apt_response = requests.get(
    f"{API_BASE}/appointments/my", 
    headers=headers
)

if apt_response.status_code == 200:
    appointments = apt_response.json()
    print(f"[OK] Found {len(appointments)} appointments")
    
    # Find an accepted appointment
    accepted = [a for a in appointments if a['status'] == 'accepted']
    if accepted:
        appointment_id = accepted[0]['id']
        print(f"[OK] Found accepted appointment: #{appointment_id}")
    else:
        print("[WARN] No accepted appointments found")
        appointment_id = None
else:
    print(f"[FAIL] Failed to get appointments: {apt_response.status_code}")
    appointment_id = None

# Step 3: Create video session
print("\n[Step 3] Creating video session...")
session_data = {
    "session_name": "Test Consultation",
    "case_id": None
}

if appointment_id:
    session_data["appointment_id"] = appointment_id

print(f"Request data: {json.dumps(session_data, indent=2)}")
print(f"Calling: {API_BASE}/video/session/create")

session_response = requests.post(
    f"{API_BASE}/video/session/create",
    headers=headers,
    json=session_data
)

print(f"Response status: {session_response.status_code}")

if session_response.status_code == 200:
    session = session_response.json()
    print(f"[OK] Video session created successfully!")
    print(f"\nSession Details:")
    print(f"  Session ID: {session['session_id']}")
    print(f"  Room Name: {session['room_name']}")
    print(f"  Expires: {session['expires_at']}")
    print(f"\nJoin URLs:")
    print(f"  Host URL: {session['join_url_host']}")
    print(f"  Guest URL: {session['join_url_guest']}")
    
    # Check if URLs use production domain
    if "h-pylori-cdss.onrender.com" in session['join_url_host']:
        print(f"\n[OK] URLs use production domain - CORRECT!")
    elif "127.0.0.1" in session['join_url_host'] or "localhost" in session['join_url_host']:
        print(f"\n[FAIL] URLs use localhost - WRONG! Need to set FRONTEND_URL env var")
    
    session_id = session['session_id']
    
    # Step 4: Validate session can be retrieved
    print(f"\n[Step 4] Validating session retrieval...")
    validate_response = requests.get(
        f"{API_BASE}/video/session/{session_id}?token={session['host_token']}",
        headers=headers
    )
    
    if validate_response.status_code == 200:
        print(f"[OK] Session validation successful!")
        session_info = validate_response.json()
        print(f"  Room: {session_info['room_name']}")
        print(f"  Host: {session_info['host_name']}")
        print(f"  Active: {session_info['active']}")
    else:
        print(f"[FAIL] Session validation failed: {validate_response.status_code}")
        print(validate_response.text)
    
else:
    print(f"[FAIL] Video session creation failed!")
    print(f"Status: {session_response.status_code}")
    print(f"Response: {session_response.text}")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)

