#!/usr/bin/env python3
"""Test appointment booking to verify the flow works."""

import requests
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000"

print("\n" + "="*70)
print("  TESTING APPOINTMENT BOOKING FLOW")
print("="*70)

# Step 1: Login as Dr. John (clinician)
print("\n1️⃣ Logging in as Dr. John (clinician)...")
login_response = requests.post(
    f"{API_BASE}/auth/login",
    json={"username": "dr_john", "password": "clinician123"}
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.text}")
    exit(1)

token = login_response.json()["access_token"]
print("✅ Logged in successfully!")

# Step 2: Get specialist ID for Dr. Sarah
print("\n2️⃣ Getting Dr. Sarah's ID...")
specialists_response = requests.get(
    f"{API_BASE}/appointments/specialists",
    headers={"Authorization": f"Bearer {token}"}
)

if specialists_response.status_code != 200:
    print(f"❌ Failed to get specialists: {specialists_response.text}")
    exit(1)

specialists = specialists_response.json()
dr_sarah = next((s for s in specialists if s["username"] == "dr_sarah"), None)

if not dr_sarah:
    print("❌ Dr. Sarah not found in specialists list!")
    exit(1)

print(f"✅ Found Dr. Sarah (ID: {dr_sarah['id']})")

# Step 3: Book an appointment
print("\n3️⃣ Booking appointment with Dr. Sarah...")
tomorrow = datetime.now() + timedelta(days=1)
appointment_data = {
    "specialist_id": dr_sarah["id"],
    "requested_date": tomorrow.strftime("%Y-%m-%dT10:00:00"),
    "duration_minutes": 30,
    "reason": "H. pylori treatment consultation for resistant case",
    "clinician_notes": "Patient failed first-line therapy, needs specialist input"
}

booking_response = requests.post(
    f"{API_BASE}/appointments/request",
    headers={"Authorization": f"Bearer {token}"},
    json=appointment_data
)

print(f"Response Status: {booking_response.status_code}")
print(f"Response: {booking_response.text}")

if booking_response.status_code == 201:
    appointment = booking_response.json()
    print(f"\n✅ SUCCESS! Appointment created!")
    print(f"   Appointment ID: {appointment['id']}")
    print(f"   Status: {appointment['status']}")
    print(f"   Specialist: {appointment['specialist_name']}")
    print(f"   Date: {appointment['requested_date']}")
else:
    print(f"\n❌ FAILED! Status: {booking_response.status_code}")
    print(f"   Error: {booking_response.text}")

# Step 4: Verify it shows in Dr. Sarah's pending requests
print("\n4️⃣ Checking if it appears in Dr. Sarah's pending requests...")

# Login as Dr. Sarah
sarah_login = requests.post(
    f"{API_BASE}/auth/login",
    json={"username": "dr_sarah", "password": "specialist123"}
)

if sarah_login.status_code != 200:
    print(f"❌ Dr. Sarah login failed: {sarah_login.text}")
    exit(1)

sarah_token = sarah_login.json()["access_token"]

# Get pending requests
pending_response = requests.get(
    f"{API_BASE}/appointments/pending-requests",
    headers={"Authorization": f"Bearer {sarah_token}"}
)

print(f"Pending requests status: {pending_response.status_code}")

if pending_response.status_code == 200:
    pending = pending_response.json()
    print(f"✅ Dr. Sarah has {len(pending)} pending request(s)")
    for req in pending:
        print(f"   - From: {req['clinician_name']}, Reason: {req['reason']}")
else:
    print(f"❌ Failed to get pending requests: {pending_response.text}")

print("\n" + "="*70)
print("  TEST COMPLETE")
print("="*70 + "\n")

