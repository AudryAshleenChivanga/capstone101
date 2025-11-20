"""
Register users via API endpoint (works from anywhere)
Run locally: python register_production_users.py
"""
import requests
import json

# Production API URL
API_BASE = "https://h-pylori-cdss.onrender.com"

def register_user(username, email, password, role, full_name, specialty="General Practice"):
    """Register user via API"""
    
    user_data = {
        "username": username,
        "email": email,
        "password": password,
        "full_name": full_name,
        "role": role,
        "specialty": specialty,
        "institution": "H. pylori CDSS"
    }
    
    try:
        # Try the register endpoint
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=user_data,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            print(f"[SUCCESS] Created {role}: {username}")
            return True
        elif response.status_code == 400:
            error = response.json()
            if "already registered" in str(error).lower():
                print(f"[EXISTS] User '{username}' already exists")
            else:
                print(f"[ERROR] {error.get('detail', error)}")
            return False
        else:
            print(f"[ERROR] Status {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Connection failed: {e}")
        return False

def main():
    print("="*70)
    print("REGISTERING USERS IN PRODUCTION VIA API")
    print("="*70)
    print(f"Target: {API_BASE}")
    print()
    
    # Users to create
    users = [
        {
            "username": "clinician1",
            "email": "clinician1@hospital.com",
            "password": "Clinician@2024",
            "role": "clinician",
            "full_name": "Dr. Clinical Staff",
            "specialty": "General Practice"
        },
        {
            "username": "specialist1",
            "email": "specialist1@hospital.com",
            "password": "Specialist@2024",
            "role": "specialist",
            "full_name": "Dr. Gastro Specialist",
            "specialty": "Gastroenterology"
        }
    ]
    
    success_count = 0
    for user in users:
        if register_user(**user):
            success_count += 1
        print()
    
    print("="*70)
    print(f"Successfully created {success_count} of {len(users)} users")
    print("="*70)
    print("\nLOGIN CREDENTIALS:")
    for user in users:
        print(f"\n{user['role'].upper()}:")
        print(f"  URL:      {API_BASE}/")
        print(f"  Username: {user['username']}")
        print(f"  Password: {user['password']}")
    print("\n" + "="*70)

if __name__ == "__main__":
    main()

