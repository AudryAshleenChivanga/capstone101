#!/usr/bin/env python3
"""
Quick script to register a test clinician for video consultation testing.
"""

import requests
import sys

API_BASE = "http://localhost:8000"

def register_clinician():
    """Register a test clinician."""
    
    print("\n" + "="*60)
    print("  CLINICIAN REGISTRATION")
    print("  H. pylori CDSS Video Consultation System")
    print("="*60 + "\n")
    
    # Clinician data
    clinician_data = {
        "username": "dr_john",
        "email": "john.doe@clinic.com",
        "password": "clinician123",
        "full_name": "Dr. John Doe",
        "specialty": "General Practice",
        "institution": "Community Health Clinic",
        "license_number": "MED-2024-67890",
        "phone": "+1 (555) 987-6543",
        "bio": "General practitioner with focus on gastroenterology referrals and H. pylori screening.",
        "profile_photo": "https://randomuser.me/api/portraits/men/32.jpg",
        "role": "clinician"
    }
    
    print("📋 Creating clinician account:")
    print(f"   Username: {clinician_data['username']}")
    print(f"   Email: {clinician_data['email']}")
    print(f"   Password: {clinician_data['password']}")
    print(f"   Name: {clinician_data['full_name']}")
    print()
    
    # Need admin authentication
    print("🔐 Admin authentication required:")
    admin_username = input("   Admin username [admin]: ").strip() or "admin"
    
    import getpass
    admin_password = getpass.getpass("   Admin password: ")
    
    try:
        # Login as admin
        print("\n🔄 Authenticating as admin...")
        login_response = requests.post(
            f"{API_BASE}/auth/login",
            json={"username": admin_username, "password": admin_password},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print("❌ Admin authentication failed!")
            print(f"   Error: {login_response.json().get('detail', 'Unknown error')}")
            return False
        
        token = login_response.json()["access_token"]
        print("✅ Admin authenticated!")
        print()
        
        # Register clinician
        print("🔄 Registering clinician...")
        register_response = requests.post(
            f"{API_BASE}/auth/register",
            json=clinician_data,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if register_response.status_code == 201:
            print("✅ SUCCESS! Clinician account created!")
            print()
            print("=" * 60)
            print("  LOGIN CREDENTIALS")
            print("=" * 60)
            print(f"  Username: {clinician_data['username']}")
            print(f"  Password: {clinician_data['password']}")
            print("=" * 60)
            print()
            print("📌 Next steps:")
            print("   1. Go to http://localhost:8001/login.html")
            print("   2. Login with the credentials above")
            print("   3. Navigate to 'Video Consultation'")
            print("   4. Book an appointment with Dr. Sarah Martinez")
            print()
            print("🎉 You can now test the complete video consultation workflow!")
            print()
            return True
        else:
            error_detail = register_response.json().get('detail', 'Unknown error')
            print(f"❌ Registration failed: {error_detail}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to the API server!")
        print("   Make sure the server is running at http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    try:
        success = register_clinician()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Registration cancelled by user.")
        sys.exit(1)

