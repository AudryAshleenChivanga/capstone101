"""
Test that production users can login successfully
"""
import requests

API_BASE = "https://h-pylori-cdss.onrender.com"

print("="*70)
print("TESTING PRODUCTION LOGINS")
print("="*70)
print()

# Test credentials
test_users = [
    {"username": "clinician1", "password": "Clinician@2024", "role": "clinician"},
    {"username": "specialist1", "password": "Specialist@2024", "role": "specialist"},
    {"username": "dr_audry", "password": "Audry@2024", "role": "admin"}
]

success_count = 0

for user in test_users:
    print(f"Testing {user['role']}: {user['username']}...", end=" ")
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json={"username": user['username'], "password": user['password']},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token', '')
            print(f"[SUCCESS] Token: {token[:30]}...")
            success_count += 1
        else:
            print(f"[FAILED] Status {response.status_code}")
            print(f"         Response: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] {e}")

print()
print("="*70)
print(f"LOGIN TEST RESULTS: {success_count}/{len(test_users)} successful")
print("="*70)
print()

if success_count == len(test_users):
    print("✅ ALL USERS CAN LOGIN SUCCESSFULLY!")
    print()
    print("Your production deployment is ready!")
    print(f"URL: {API_BASE}/ui/login.html")
else:
    print("⚠️  Some users failed to login. Check errors above.")

print()

