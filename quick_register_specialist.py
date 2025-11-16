#!/usr/bin/env python3
"""
Quick script to register a test specialist for video consultation testing.
Run this to quickly create a specialist account.
"""

import requests
import sys

API_BASE = "http://localhost:8000"

def register_test_specialist():
    """Register a test specialist with predefined data."""
    
    print("\n" + "="*60)
    print("  QUICK SPECIALIST REGISTRATION")
    print("  H. pylori CDSS Video Consultation System")
    print("="*60 + "\n")
    
    # Predefined test specialist data
    specialist_data = {
        "username": "dr_sarah",
        "email": "sarah.martinez@hospital.com",
        "password": "specialist123",
        "full_name": "Dr. Sarah Martinez",
        "specialty": "Gastroenterology",
        "institution": "Central Medical Hospital",
        "license_number": "MED-2024-12345",
        "phone": "+1 (555) 123-4567",
        "bio": "Board-certified gastroenterologist with 10 years of experience in H. pylori diagnosis and treatment. Specializing in advanced endoscopic procedures and antibiotic resistance management.",
        "profile_photo": "https://randomuser.me/api/portraits/women/44.jpg",
        "role": "specialist"
    }
    
    print("📋 Creating test specialist account:")
    print(f"   Username: {specialist_data['username']}")
    print(f"   Email: {specialist_data['email']}")
    print(f"   Password: {specialist_data['password']}")
    print(f"   Name: {specialist_data['full_name']}")
    print(f"   Specialty: {specialist_data['specialty']}")
    print(f"   Institution: {specialist_data['institution']}")
    print()
    
    # Try to register as first user (no auth required)
    print("🔄 Attempting registration as first user...")
    try:
        response = requests.post(
            f"{API_BASE}/auth/register/first",
            json=specialist_data,
            timeout=10
        )
        
        if response.status_code == 201:
            print("✅ SUCCESS! Specialist account created!")
            print()
            print("=" * 60)
            print("  LOGIN CREDENTIALS")
            print("=" * 60)
            print(f"  Username: {specialist_data['username']}")
            print(f"  Password: {specialist_data['password']}")
            print("=" * 60)
            print()
            print("📌 Next steps:")
            print("   1. Go to http://localhost:8001/login.html")
            print("   2. Login with the credentials above")
            print("   3. Navigate to 'Video Consultation' in the sidebar")
            print("   4. You'll see a 'Pending Requests' tab (specialist-only)")
            print()
            print("🎉 You can now approve appointment requests and conduct video consultations!")
            print()
            return True
            
        elif response.status_code == 403:
            # First user already exists, need admin auth
            print("⚠️  First user already registered.")
            print("    Trying with admin authentication...")
            print()
            
            # Try to get admin credentials
            print("🔐 Admin authentication required:")
            admin_username = input("   Admin username: ").strip()
            if not admin_username:
                print("❌ Admin username required. Exiting.")
                return False
                
            import getpass
            admin_password = getpass.getpass("   Admin password: ")
            if not admin_password:
                print("❌ Admin password required. Exiting.")
                return False
            
            # Login as admin
            print()
            print("🔄 Authenticating as admin...")
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
            
            # Register specialist with admin token
            print("🔄 Registering specialist...")
            register_response = requests.post(
                f"{API_BASE}/auth/register",
                json=specialist_data,
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            if register_response.status_code == 201:
                print("✅ SUCCESS! Specialist account created!")
                print()
                print("=" * 60)
                print("  LOGIN CREDENTIALS")
                print("=" * 60)
                print(f"  Username: {specialist_data['username']}")
                print(f"  Password: {specialist_data['password']}")
                print("=" * 60)
                print()
                print("📌 Next steps:")
                print("   1. Go to http://localhost:8001/login.html")
                print("   2. Login with the credentials above")
                print("   3. Navigate to 'Video Consultation' in the sidebar")
                print("   4. You'll see a 'Pending Requests' tab (specialist-only)")
                print()
                print("🎉 You can now approve appointment requests and conduct video consultations!")
                print()
                return True
            else:
                error_detail = register_response.json().get('detail', 'Unknown error')
                print(f"❌ Registration failed: {error_detail}")
                return False
        else:
            error_detail = response.json().get('detail', 'Unknown error')
            print(f"❌ Registration failed: {error_detail}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to the API server!")
        print("   Make sure the server is running at http://localhost:8000")
        print()
        print("   To start the server, run:")
        print("   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        print()
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function."""
    try:
        success = register_test_specialist()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Registration cancelled by user.")
        sys.exit(1)


if __name__ == "__main__":
    main()

