#!/usr/bin/env python3
"""
Script to register specialists (gastroenterologists) for the H. pylori CDSS system.
Run this script to add specialists who can receive appointment requests from clinicians.
"""

import requests
import getpass
import json

API_BASE = "http://localhost:8000"

def register_specialist():
    print("\n" + "="*60)
    print("  H. PYLORI CDSS - SPECIALIST REGISTRATION")
    print("="*60 + "\n")
    
    # Get admin credentials
    print("🔐 Admin Authentication Required\n")
    admin_username = input("Admin Username: ").strip()
    admin_password = getpass.getpass("Admin Password: ")
    
    # Login as admin
    print("\n🔄 Authenticating...")
    login_response = requests.post(
        f"{API_BASE}/auth/login",
        json={"username": admin_username, "password": admin_password}
    )
    
    if login_response.status_code != 200:
        print("❌ Authentication failed! Please check your credentials.")
        return
    
    token = login_response.json()["access_token"]
    print("✅ Authentication successful!\n")
    
    # Get specialist information
    print("👨‍⚕️ Specialist Information\n")
    print("-" * 60)
    
    specialist_data = {}
    
    specialist_data["username"] = input("Username: ").strip()
    specialist_data["email"] = input("Email: ").strip()
    specialist_data["password"] = getpass.getpass("Password: ")
    specialist_data["full_name"] = input("Full Name (e.g., Dr. Sarah Martinez): ").strip()
    specialist_data["specialty"] = input("Specialty (e.g., Gastroenterology): ").strip()
    specialist_data["institution"] = input("Institution/Hospital: ").strip()
    specialist_data["license_number"] = input("License Number (optional): ").strip() or None
    specialist_data["bio"] = input("Bio (optional): ").strip() or None
    specialist_data["role"] = "specialist"
    
    # Ask for profile photo
    photo_choice = input("\nAdd profile photo URL? (y/n): ").lower()
    if photo_choice == 'y':
        specialist_data["profile_photo"] = input("Photo URL: ").strip()
    else:
        specialist_data["profile_photo"] = None
    
    # Register the specialist
    print("\n🔄 Registering specialist...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    register_response = requests.post(
        f"{API_BASE}/auth/register",
        json=specialist_data,
        headers=headers
    )
    
    if register_response.status_code == 201:
        user = register_response.json()
        print("\n" + "="*60)
        print("✅ SPECIALIST REGISTERED SUCCESSFULLY!")
        print("="*60)
        print(f"\n📋 Details:")
        print(f"   ID: {user['id']}")
        print(f"   Username: {user['username']}")
        print(f"   Email: {user['email']}")
        print(f"   Full Name: {user['full_name']}")
        print(f"   Specialty: {specialist_data['specialty']}")
        print(f"   Institution: {specialist_data['institution']}")
        print("\n🎉 This specialist can now receive appointment requests!")
        print("="*60 + "\n")
    else:
        error = register_response.json()
        print(f"\n❌ Registration Failed: {error.get('detail', 'Unknown error')}\n")

def register_multiple_specialists():
    """Register multiple specialists at once."""
    print("\n" + "="*60)
    print("  BULK SPECIALIST REGISTRATION")
    print("="*60 + "\n")
    
    # Get admin credentials once
    admin_username = input("Admin Username: ").strip()
    admin_password = getpass.getpass("Admin Password: ")
    
    # Login
    login_response = requests.post(
        f"{API_BASE}/auth/login",
        json={"username": admin_username, "password": admin_password}
    )
    
    if login_response.status_code != 200:
        print("❌ Authentication failed!")
        return
    
    token = login_response.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Predefined specialists
    specialists = [
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
    
    registered_count = 0
    failed_count = 0
    
    for specialist in specialists:
        print(f"\n🔄 Registering {specialist['full_name']}...")
        
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=specialist,
            headers=headers
        )
        
        if response.status_code == 201:
            print(f"✅ {specialist['full_name']} registered successfully!")
            registered_count += 1
        else:
            error = response.json()
            print(f"❌ Failed: {error.get('detail', 'Unknown error')}")
            failed_count += 1
    
    print("\n" + "="*60)
    print(f"✅ Registered: {registered_count}")
    print(f"❌ Failed: {failed_count}")
    print("="*60 + "\n")


if __name__ == "__main__":
    print("\nChoose registration method:")
    print("1. Register single specialist (interactive)")
    print("2. Register 3 sample specialists (quick setup)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        register_specialist()
    elif choice == "2":
        register_multiple_specialists()
    else:
        print("Invalid choice!")

