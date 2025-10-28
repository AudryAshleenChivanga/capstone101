"""
Comprehensive API Endpoint Testing Script
Tests all backend functionality and generates test report
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "username": "admin",
    "password": "Admin@2024"
}

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# Test results tracking
test_results = []

def log_test(test_name, passed, message=""):
    """Log test result"""
    status = f"{Colors.GREEN}✓ PASS{Colors.ENDC}" if passed else f"{Colors.RED}✗ FAIL{Colors.ENDC}"
    print(f"{status} {test_name}")
    if message:
        print(f"    {message}")
    test_results.append({
        "test": test_name,
        "passed": passed,
        "message": message
    })

def test_health_check():
    """Test 1: Health Check Endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        passed = response.status_code == 200
        log_test("Health Check", passed, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        log_test("Health Check", False, str(e))
        return False

def test_authentication():
    """Test 2: Authentication (Login)"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data=TEST_USER,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            log_test("Authentication", True, f"Token received: {token[:20]}...")
            return token
        else:
            log_test("Authentication", False, f"Status: {response.status_code}")
            return None
    except Exception as e:
        log_test("Authentication", False, str(e))
        return None

def test_get_current_user(token):
    """Test 3: Get Current User Info"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=10)
        passed = response.status_code == 200
        if passed:
            user = response.json()
            log_test("Get Current User", True, f"User: {user.get('username')}")
        else:
            log_test("Get Current User", False, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        log_test("Get Current User", False, str(e))
        return False

def test_stage1_symptom_assessment(token):
    """Test 4: Stage 1 - Symptom Assessment"""
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "patient_name": "John Test Doe",
            "age": 45,
            "sex": "M",
            "residence": "urban",
            "phone": "+250788123456",
            "abdominal_pain": 1,
            "bloating": 1,
            "nausea": 1,
            "heartburn": 1,
            "family_history_gastric": 1,
            "symptom_duration_weeks": 4
        }
        response = requests.post(
            f"{BASE_URL}/workflow/stage1/symptom-assessment",
            headers=headers,
            json=payload,
            timeout=15
        )
        passed = response.status_code == 200
        if passed:
            result = response.json()
            patient_id = result.get('patient_id')
            risk_level = result.get('assessment', {}).get('risk_level')
            log_test("Stage 1 Symptom Assessment", True, 
                    f"Patient ID: {patient_id}, Risk: {risk_level}")
            return patient_id
        else:
            log_test("Stage 1 Symptom Assessment", False, 
                    f"Status: {response.status_code}, Error: {response.text}")
            return None
    except Exception as e:
        log_test("Stage 1 Symptom Assessment", False, str(e))
        return None

def test_stage2_lab_screening(token, patient_id):
    """Test 5: Stage 2 - Lab Screening"""
    if not patient_id:
        log_test("Stage 2 Lab Screening", False, "No patient_id from Stage 1")
        return None
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "patient_id": patient_id,
            "stool_antigen": "positive",
            "hp_igg": "positive",
            "hemoglobin": 13.5,
            "crp": 8.2,
            "wbc": 7.5
        }
        response = requests.post(
            f"{BASE_URL}/workflow/stage2/lab-screening",
            headers=headers,
            json=payload,
            timeout=15
        )
        passed = response.status_code == 200
        if passed:
            result = response.json()
            status = result.get('screening_result', {}).get('status')
            log_test("Stage 2 Lab Screening", True, f"H. pylori Status: {status}")
            return result.get('case_id')
        else:
            log_test("Stage 2 Lab Screening", False, 
                    f"Status: {response.status_code}, Error: {response.text}")
            return None
    except Exception as e:
        log_test("Stage 2 Lab Screening", False, str(e))
        return None

def test_stage3_ric_staging(token, patient_id):
    """Test 6: Stage 3 - RIC Staging"""
    if not patient_id:
        log_test("Stage 3 RIC Staging", False, "No patient_id from previous stages")
        return None
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "patient_id": patient_id,
            "mic_clarithromycin": 0.5,
            "mic_metronidazole": 8.0,
            "mic_levofloxacin": 1.0,
            "mutation_a2143g": 1,
            "mutation_rdxa": 1,
            "atrophy_score": 2,
            "metaplasia_score": 1,
            "inflammation_score": 2,
            "hp_density": 2
        }
        response = requests.post(
            f"{BASE_URL}/workflow/stage3/ric-staging",
            headers=headers,
            json=payload,
            timeout=15
        )
        passed = response.status_code == 200
        if passed:
            result = response.json()
            stage = result.get('staging_result', {}).get('stage')
            log_test("Stage 3 RIC Staging", True, f"Disease Stage: {stage}")
            return result.get('case_id')
        else:
            log_test("Stage 3 RIC Staging", False, 
                    f"Status: {response.status_code}, Error: {response.text}")
            return None
    except Exception as e:
        log_test("Stage 3 RIC Staging", False, str(e))
        return None

def test_list_cases(token):
    """Test 7: List Cases with Filters"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/cases?page=1&page_size=10",
            headers=headers,
            timeout=10
        )
        passed = response.status_code == 200
        if passed:
            data = response.json()
            total = data.get('total', 0)
            log_test("List Cases", True, f"Total cases: {total}")
        else:
            log_test("List Cases", False, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        log_test("List Cases", False, str(e))
        return False

def test_search_patients(token):
    """Test 8: Search Patients"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/patients/search?query=John",
            headers=headers,
            timeout=10
        )
        passed = response.status_code == 200
        if passed:
            patients = response.json()
            log_test("Search Patients", True, f"Found {len(patients)} patients")
        else:
            log_test("Search Patients", False, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        log_test("Search Patients", False, str(e))
        return False

def test_legacy_recommendation(token):
    """Test 9: Legacy Recommendation Endpoint (Compatibility)"""
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "task": "screening",
            "age": 50,
            "sex": "F",
            "residence": "rural",
            "stool_ag": 1,
            "hemoglobin": 12.5
        }
        response = requests.post(
            f"{BASE_URL}/recommend",
            headers=headers,
            json=payload,
            timeout=15
        )
        passed = response.status_code == 200
        if passed:
            result = response.json()
            prob = result.get('screen_prob', 0)
            log_test("Legacy Recommendation", True, f"Screen Probability: {prob:.2f}")
        else:
            log_test("Legacy Recommendation", False, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        log_test("Legacy Recommendation", False, str(e))
        return False

def generate_report():
    """Generate test report"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}TEST SUMMARY{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
    
    passed_tests = sum(1 for r in test_results if r['passed'])
    total_tests = len(test_results)
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {Colors.GREEN}{passed_tests}{Colors.ENDC}")
    print(f"Failed: {Colors.RED}{total_tests - passed_tests}{Colors.ENDC}")
    print(f"Pass Rate: {Colors.BOLD}{pass_rate:.1f}%{Colors.ENDC}\n")
    
    if passed_tests == total_tests:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED!{Colors.ENDC}")
        print(f"{Colors.GREEN}Backend is working seamlessly!{Colors.ENDC}\n")
    else:
        print(f"{Colors.YELLOW}Some tests failed. Review the details above.{Colors.ENDC}\n")
    
    # Save report to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"test_report_{timestamp}.json"
    with open(report_file, 'w') as f:
        json.dump({
            "timestamp": timestamp,
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": total_tests - passed_tests,
            "pass_rate": pass_rate,
            "results": test_results
        }, f, indent=2)
    print(f"Report saved to: {report_file}\n")

def main():
    """Main test runner"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}H. pylori CDSS API Testing{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
    print(f"Testing backend at: {BASE_URL}\n")
    
    # Test 1: Health Check
    if not test_health_check():
        print(f"\n{Colors.RED}Server is not running! Start the server first.{Colors.ENDC}\n")
        return
    
    # Test 2: Authentication
    token = test_authentication()
    if not token:
        print(f"\n{Colors.RED}Authentication failed! Cannot continue tests.{Colors.ENDC}\n")
        return
    
    # Test 3: Get User Info
    test_get_current_user(token)
    
    # Test 4-6: Multi-Stage Workflow
    print(f"\n{Colors.BOLD}Testing Multi-Stage Workflow{Colors.ENDC}")
    patient_id = test_stage1_symptom_assessment(token)
    if patient_id:
        test_stage2_lab_screening(token, patient_id)
        test_stage3_ric_staging(token, patient_id)
    
    # Test 7: List Cases
    test_list_cases(token)
    
    # Test 8: Search Patients
    test_search_patients(token)
    
    # Test 9: Legacy Compatibility
    test_legacy_recommendation(token)
    
    # Generate report
    generate_report()

if __name__ == "__main__":
    main()

