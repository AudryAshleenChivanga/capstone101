"""
Script to create the first admin account for H. pylori CDSS
"""
import requests
import json

# API endpoint
API_BASE = "http://localhost:8000"

# Admin credentials
admin_data = {
    "username": "admin",
    "email": "admin@hospital.com",
    "password": "Admin@2024",
    "role": "admin"
}

print("=" * 60)
print("Creating Admin Account for H. pylori CDSS")
print("=" * 60)
print()

try:
    # Register the admin user
    print("Registering admin user...")
    response = requests.post(
        f"{API_BASE}/auth/register/first",
        json=admin_data,
        timeout=10
    )
    
    if response.status_code == 201:
        user = response.json()
        print("[SUCCESS] Admin account created")
        print()
        print("=" * 60)
        print("CREDENTIALS")
        print("=" * 60)
        print(f"Username: {admin_data['username']}")
        print(f"Email:    {admin_data['email']}")
        print(f"Password: {admin_data['password']}")
        print(f"Role:     {user['role']}")
        print("=" * 60)
        print()
        print("You can now login at: http://localhost:8000/ui/index.html")
        print()
        
    elif response.status_code == 403:
        print("[WARNING] Admin user already exists!")
        print()
        print("If you forgot your password, you can:")
        print("1. Delete the cdss.db file")
        print("2. Restart the server")
        print("3. Run this script again")
        print()
        print("Or try these credentials:")
        print("-" * 60)
        print(f"Username: {admin_data['username']}")
        print(f"Password: {admin_data['password']}")
        print("-" * 60)
        
    else:
        error = response.json()
        print(f"[ERROR] {error.get('detail', 'Unknown error')}")
        
except requests.exceptions.ConnectionError:
    print("[ERROR] Cannot connect to the server!")
    print()
    print("Please make sure the server is running:")
    print("  1. Open a new PowerShell window")
    print("  2. Navigate to the project directory")
    print("  3. Run: .\\run_api.ps1")
    print("  4. Wait for the server to start")
    print("  5. Run this script again")
    print()
    
except Exception as e:
    print(f"[ERROR] {str(e)}")
    print()

print()
print("Need help? Check README.md or QUICKSTART.md")
print()
