#!/usr/bin/env python3
"""Test video session creation."""

import requests

API_BASE = "http://localhost:8000"

print("\n" + "="*70)
print("  TESTING VIDEO SESSION CREATION")
print("="*70)

# Login as Dr. John
print("\n1️⃣ Logging in as Dr. John...")
login = requests.post(
    f"{API_BASE}/auth/login",
    json={"username": "dr_john", "password": "clinician123"}
)

if login.status_code != 200:
    print(f"❌ Login failed: {login.text}")
    exit(1)

token = login.json()["access_token"]
print("✅ Logged in!")

# Create video session for appointment #2
print("\n2️⃣ Creating video session for appointment #2...")
session_response = requests.post(
    f"{API_BASE}/video/session/create",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "appointment_id": 2,
        "session_name": "Test Consultation"
    }
)

print(f"Status: {session_response.status_code}")
print(f"Response: {session_response.text}")

if session_response.status_code == 200:
    session_data = session_response.json()
    print("\n✅ Session created successfully!")
    print(f"Session ID: {session_data['session_id']}")
    print(f"Join URL: {session_data['join_url_host']}")
    
    session_id = session_data['session_id']
    session_token = session_data['host_token']
    
    # Test getting session info
    print(f"\n3️⃣ Testing session info retrieval...")
    info_response = requests.get(
        f"{API_BASE}/video/session/{session_id}?token={session_token}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status: {info_response.status_code}")
    print(f"Response: {info_response.text}")
    
    if info_response.status_code == 200:
        print("✅ Session info retrieved successfully!")
    else:
        print(f"❌ Failed to get session info!")
else:
    print(f"\n❌ Failed to create session!")

print("\n" + "="*70 + "\n")

