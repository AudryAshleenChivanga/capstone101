"""
Register users in production using admin authentication
"""
import requests
import time

API_BASE = "https://h-pylori-cdss.onrender.com"

print("="*70)
print("AUTHENTICATED USER REGISTRATION")
print("="*70)
print(f"Target: {API_BASE}")
print()

# Step 1: Wake up service
print("Step 1: Waking up Render service...")
try:
    response = requests.get(f"{API_BASE}/health", timeout=90)
    if response.status_code == 200:
        print("[OK] Service is awake!")
    else:
        print(f"[WARNING] Status {response.status_code}")
except Exception as e:
    print(f"[WARNING] Health check: {e}")

time.sleep(2)
print()

# Step 2: Login as admin to get token
print("Step 2: Logging in as admin...")
admin_credentials = {
    "username": "admin",
    "password": "Admin@2024"
}

try:
    response = requests.post(
        f"{API_BASE}/auth/login",
        json=admin_credentials,
        timeout=30
    )
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        print("[OK] Admin login successful!")
        print(f"     Token: {access_token[:20]}...")
    else:
        print(f"[FAILED] Admin login failed: {response.status_code}")
        print(f"         Response: {response.text}")
        print()
        print("POSSIBLE ISSUE: Admin user doesn't exist or wrong password")
        print()
        print("SOLUTION: Use Render Shell method instead:")
        print("1. Go to Render Dashboard → Your service → Shell")
        print("2. Run: python create_production_users.py")
        exit(1)
        
except Exception as e:
    print(f"[FAILED] Login error: {e}")
    exit(1)

print()

# Step 3: Register users with admin token
print("Step 3: Registering users with admin authentication...")
print()

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

users_to_register = [
    {
        "username": "clinician1",
        "email": "clinician1@hospital.com",
        "password": "Clinician@2024",
        "full_name": "Dr. Clinical Staff",
        "role": "clinician",
        "specialty": "General Practice",
        "institution": "District Hospital"
    },
    {
        "username": "specialist1",
        "email": "specialist1@hospital.com",
        "password": "Specialist@2024",
        "full_name": "Dr. Gastro Specialist",
        "role": "specialist",
        "specialty": "Gastroenterology",
        "institution": "Referral Hospital"
    },
    {
        "username": "dr_audry",
        "email": "audry@hospital.com",
        "password": "Audry@2024",
        "full_name": "Dr. Audry Chivanga",
        "role": "admin",
        "specialty": "Medical Informatics",
        "institution": "H. pylori CDSS Research"
    }
]

success_count = 0
existing_count = 0
failed_users = []

for user in users_to_register:
    print(f"Registering {user['role']}: {user['username']}...", end=" ")
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=user,
            headers=headers,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            print("[SUCCESS]")
            success_count += 1
        elif response.status_code == 400:
            error = response.json()
            detail = error.get('detail', '')
            if "already registered" in str(detail).lower() or "already exists" in str(detail).lower():
                print("[EXISTS] (Already in database)")
                existing_count += 1
            else:
                print(f"[FAILED] {detail}")
                failed_users.append(user['username'])
        else:
            print(f"[FAILED] Status {response.status_code}")
            print(f"         Response: {response.text[:200]}")
            failed_users.append(user['username'])
            
    except Exception as e:
        print(f"[FAILED] {str(e)[:100]}")
        failed_users.append(user['username'])

print()
print("="*70)
print("REGISTRATION SUMMARY")
print("="*70)
print(f"New users created:   {success_count}")
print(f"Already existed:     {existing_count}")
print(f"Failed:              {len(failed_users)}")
if failed_users:
    print(f"Failed usernames:    {', '.join(failed_users)}")
print()

if success_count + existing_count > 0:
    print("="*70)
    print("PRODUCTION LOGIN CREDENTIALS")
    print("="*70)
    print(f"\nAccess URL: {API_BASE}/ui/login.html\n")
    
    for user in users_to_register:
        if user['username'] not in failed_users:
            print(f"{user['role'].upper()}: {user['username']}")
            print(f"  Password: {user['password']}")
            print(f"  Email: {user['email']}")
            print()
    
    print("="*70)
    print("\nNEXT STEPS:")
    print("1. Visit: https://h-pylori-cdss.onrender.com/ui/login.html")
    print("2. Test login with above credentials")
    print("3. Verify dashboard access")
    print()
    print("="*70)
else:
    print("\nNo users were registered. Check errors above.")
    print()

