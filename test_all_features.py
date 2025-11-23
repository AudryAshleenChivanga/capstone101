"""
Comprehensive System Test - All Features
Run: python test_all_features.py
"""
import requests
import json
from datetime import datetime

API_BASE = "http://127.0.0.1:8000"
test_results = []

def test(name, func):
    """Run a test and record result"""
    try:
        result = func()
        test_results.append({"name": name, "status": "PASS" if result else "FAIL", "error": None})
        print(f"{'[OK]' if result else '[FAIL]'} {name}")
        return result
    except Exception as e:
        test_results.append({"name": name, "status": "FAIL", "error": str(e)})
        print(f"[FAIL] {name}: {e}")
        return False

# Test 1: Server Health
def test_server():
    r = requests.get(f"{API_BASE}/health", timeout=5)
    return r.status_code == 200

# Test 2: Registration Endpoint
def test_registration_endpoint():
    r = requests.get(f"{API_BASE}/auth/register/public/test")
    return r.status_code == 200

# Test 3: Login Endpoint (without credentials)
def test_login_endpoint():
    # Just test endpoint exists (will fail auth but should not 404)
    r = requests.post(f"{API_BASE}/auth/login", json={"username": "test", "password": "test"})
    return r.status_code in [200, 401]  # 401 is expected for bad creds

# Test 4: Screening Endpoint
def test_screening_endpoint():
    # Check if endpoint exists (will fail auth)
    r = requests.post(f"{API_BASE}/recommend", json={})
    return r.status_code in [200, 401, 422]  # 401/422 expected without auth/data

# Test 5: Cases Endpoint
def test_cases_endpoint():
    r = requests.get(f"{API_BASE}/cases")
    return r.status_code in [200, 401]  # 401 expected without auth

# Test 6: Video Session Endpoint  
def test_video_endpoint():
    r = requests.post(f"{API_BASE}/video/session/create", json={})
    return r.status_code in [200, 401, 422]

# Test 7: Appointments Endpoint
def test_appointments_endpoint():
    r = requests.get(f"{API_BASE}/appointments/specialists")
    return r.status_code in [200, 401]

# Test 8: Model Management Endpoint (admin only)
def test_model_mgmt_endpoint():
    r = requests.get(f"{API_BASE}/api/model-management/health")
    return r.status_code in [200, 401, 403]

# Test 9: Static Files
def test_static_files():
    files = [
        "/ui/dashboard_new.html",
        "/ui/login.html",
        "/ui/app_new.js",
        "/ui/case_management.js",
        "/ui/workflow_forms.js",
        "/ui/video_consult.js"
    ]
    
    for f in files:
        r = requests.get(f"{API_BASE}{f}")
        if r.status_code != 200:
            print(f"  [FAIL] {f}: {r.status_code}")
            return False
    return True

# Test 10: Full Registration Flow
def test_full_registration():
    username = f"test_{int(datetime.now().timestamp())}"
    email = f"{username}@test.com"
    
    data = {
        "username": email,
        "email": email,
        "password": "Test123!",
        "full_name": "Test User",
        "role": "clinician"
    }
    
    r = requests.post(f"{API_BASE}/auth/register/public", json=data)
    if r.status_code != 201:
        print(f"  Registration failed: {r.status_code} - {r.text}")
        return False
    
    # Try to login with new account
    login_data = {
        "username": email,
        "password": "Test123!"
    }
    r = requests.post(f"{API_BASE}/auth/login", data=login_data)
    
    if r.status_code != 200:
        print(f"  Login failed: {r.status_code}")
        return False
    
    token = r.json().get('access_token')
    print(f"  [OK] Created and logged in as: {email}")
    return True

if __name__ == "__main__":
    print("\n[COMPREHENSIVE SYSTEM SCAN]")
    print("=" * 50)
    
    print("\n[Backend API Tests]")
    print("-" * 50)
    test("Server Health", test_server)
    test("Registration Endpoint", test_registration_endpoint)
    test("Login Endpoint", test_login_endpoint)
    test("Screening Endpoint", test_screening_endpoint)
    test("Cases Endpoint", test_cases_endpoint)
    test("Video Endpoint", test_video_endpoint)
    test("Appointments Endpoint", test_appointments_endpoint)
    test("Model Management Endpoint", test_model_mgmt_endpoint)
    
    print("\n[Frontend Files]")
    print("-" * 50)
    test("Static Files Loading", test_static_files)
    
    print("\n[User Flow]")
    print("-" * 50)
    test("Full Registration & Login", test_full_registration)
    
    print("\n" + "=" * 50)
    passed = sum(1 for t in test_results if t['status'] == 'PASS')
    total = len(test_results)
    print(f"\n[RESULTS] {passed}/{total} tests passed")
    
    if passed == total:
        print("[OK] ALL SYSTEMS OPERATIONAL!")
    else:
        print(f"[WARN] {total - passed} issues found - review above")
    
    print("\n[Manual Tests Still Needed]")
    print("- Login to dashboard")
    print("- Fill and submit Screening form")
    print("- Fill and submit Lab Screening form")
    print("- Fill and submit Staging form")
    print("- Sign a case")
    print("- Generate PDF")
    print("- Book video appointment")
    print("- Start video call")
    print("- Use capsule endoscopy")
    print("- Logout")

