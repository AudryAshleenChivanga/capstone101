#!/usr/bin/env python3
"""
Quick script to register 3 sample specialists.
Just run this script and it will register them automatically!
"""

import requests
import sys

API_BASE = "http://localhost:8000"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Admin@2024"

# Sample specialists
SPECIALISTS = [
    {
        "username": "dr.martinez",
        "email": "s.martinez@citymed.com",
        "password": "Specialist@2024",
        "full_name": "Dr. Sarah Martinez",
        "specialty": "Gastroenterology",
        "institution": "City Medical Center",
        "role": "specialist",
        "profile_photo": None
    },
    {
        "username": "dr.chen",
        "email": "j.chen@metrohosp.com",
        "password": "Specialist@2024",
        "full_name": "Dr. James Chen",
        "specialty": "Gastroenterology & Hepatology",
        "institution": "Metropolitan Hospital",
        "role": "specialist",
        "profile_photo": None
    },
    {
        "username": "dr.rodriguez",
        "email": "e.rodriguez@umc.edu",
        "password": "Specialist@2024",
        "full_name": "Dr. Emily Rodriguez",
        "specialty": "Gastroenterology",
        "institution": "University Medical Center",
        "role": "specialist",
        "profile_photo": None
    }
]

def main():
    print("\n" + "="*60)
    print("  REGISTERING SAMPLE SPECIALISTS")
    print("="*60 + "\n")
    
    # Login as admin
    print("[*] Authenticating as admin...")
    try:
        login_response = requests.post(
            f"{API_BASE}/auth/login",
            json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
            timeout=5
        )
        
        if login_response.status_code != 200:
            print("[X] Authentication failed!")
            print(f"   Error: {login_response.json().get('detail', 'Unknown error')}")
            print("\n[!] Make sure:")
            print("   1. Server is running (./START_APP.ps1)")
            print("   2. Admin credentials are correct")
            return
        
        token = login_response.json()["access_token"]
        print("[+] Authentication successful!\n")
        
    except requests.exceptions.ConnectionError:
        print("[X] Cannot connect to server!")
        print("\n[!] Please start the server first:")
        print("   .\\START_APP.ps1")
        return
    except Exception as e:
        print(f"[X] Error: {e}")
        return
    
    # Register specialists
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    registered_count = 0
    failed_count = 0
    
    for specialist in SPECIALISTS:
        print(f"[*] Registering {specialist['full_name']}...")
        print(f"   Username: {specialist['username']}")
        print(f"   Email: {specialist['email']}")
        print(f"   Specialty: {specialist['specialty']}")
        print(f"   Institution: {specialist['institution']}")
        
        try:
            response = requests.post(
                f"{API_BASE}/auth/register",
                json=specialist,
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 201:
                user = response.json()
                print(f"[+] Successfully registered! (ID: {user['id']})\n")
                registered_count += 1
            else:
                error = response.json()
                error_msg = error.get('detail', 'Unknown error')
                print(f"[X] Failed: {error_msg}\n")
                failed_count += 1
                
        except Exception as e:
            print(f"[X] Error: {e}\n")
            failed_count += 1
    
    # Summary
    print("="*60)
    print("  REGISTRATION COMPLETE")
    print("="*60)
    print(f"\n[+] Successfully registered: {registered_count}")
    print(f"[X] Failed: {failed_count}")
    
    if registered_count > 0:
        print("\n[!] Specialists are now available for appointment booking!")
        print("\n[>] Login Credentials:")
        print("   Usernames: dr.martinez, dr.chen, dr.rodriguez")
        print("   Password: Specialist@2024")
        print("\n[>] Test it:")
        print("   1. Go to http://localhost:8000/ui/dashboard_new.html")
        print("   2. Login as admin")
        print("   3. Click 'Video Consult' in sidebar")
        print("   4. You should see the specialist cards!")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()

