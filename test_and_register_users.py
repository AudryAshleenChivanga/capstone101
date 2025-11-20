"""
Wake up Render service and register users
"""
import requests
import time

API_BASE = "https://h-pylori-cdss.onrender.com"

print("="*70)
print("PRODUCTION USER REGISTRATION")
print("="*70)
print(f"Target: {API_BASE}")
print()

# Step 1: Wake up the service
print("Step 1: Waking up Render service (may take 30-60 seconds)...")
try:
    response = requests.get(f"{API_BASE}/health", timeout=90)
    if response.status_code == 200:
        print("[OK] Service is awake!")
        print(f"     Response: {response.json()}")
    else:
        print(f"[WARNING] Service responded with status {response.status_code}")
except requests.exceptions.Timeout:
    print("[WARNING] Health check timed out, but service might be waking up...")
except Exception as e:
    print(f"[WARNING] Health check failed: {e}")

print()
print("Step 2: Waiting 5 seconds for service to be fully ready...")
time.sleep(5)
print()

# Step 2: Register users
print("Step 3: Registering users...")
print()

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
    }
]

success_count = 0
failed_users = []

for user in users_to_register:
    print(f"Registering {user['role']}: {user['username']}...", end=" ")
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=user,
            timeout=60
        )
        
        if response.status_code in [200, 201]:
            print("[SUCCESS]")
            success_count += 1
        elif response.status_code == 400:
            error = response.json()
            if "already registered" in str(error).lower() or "already exists" in str(error).lower():
                print("[EXISTS] (Already registered)")
                success_count += 1  # Count as success
            else:
                print(f"[FAILED] {error.get('detail', error)}")
                failed_users.append(user['username'])
        else:
            print(f"[FAILED] Status {response.status_code}")
            failed_users.append(user['username'])
            print(f"         Response: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print("[FAILED] Timeout (service too slow)")
        failed_users.append(user['username'])
    except Exception as e:
        print(f"[FAILED] {str(e)[:100]}")
        failed_users.append(user['username'])

print()
print("="*70)
print("REGISTRATION SUMMARY")
print("="*70)
print(f"Success: {success_count}/{len(users_to_register)} users")
if failed_users:
    print(f"Failed: {', '.join(failed_users)}")
print()

if success_count > 0:
    print("LOGIN CREDENTIALS (Production):")
    print("-" * 70)
    for user in users_to_register:
        if user['username'] not in failed_users:
            print(f"\n{user['role'].upper()}:")
            print(f"  URL:      {API_BASE}/ui/login.html")
            print(f"  Username: {user['username']}")
            print(f"  Password: {user['password']}")
    print()
    print("-" * 70)
    print("\nNEXT STEPS:")
    print("1. Visit: https://h-pylori-cdss.onrender.com/ui/login.html")
    print("2. Test login with above credentials")
    print("3. Verify you can access the dashboard")
    print()

print("="*70)

