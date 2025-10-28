"""
Verification script to check if the H. pylori CDSS installation is complete.
"""
import os
import sys
from pathlib import Path


def check_file(filepath, description):
    """Check if a file exists."""
    if Path(filepath).exists():
        print(f"[OK] {description}: {filepath}")
        return True
    else:
        print(f"[MISSING] {description}: {filepath}")
        return False


def check_directory(dirpath, description):
    """Check if a directory exists."""
    if Path(dirpath).is_dir():
        print(f"[OK] {description}: {dirpath}")
        return True
    else:
        print(f"[MISSING] {description}: {dirpath}")
        return False


def main():
    print("="* 70)
    print("H. pylori CDSS - Installation Verification")
    print("="* 70)
    print()
    
    checks_passed = 0
    checks_total = 0
    
    print("Checking Directory Structure...")
    print("-" * 70)
    
    directories = [
        ("app", "Backend application directory"),
        ("ui", "Frontend directory"),
        ("tests", "Test directory"),
        ("models", "ML models directory"),
    ]
    
    for dir_path, desc in directories:
        checks_total += 1
        if check_directory(dir_path, desc):
            checks_passed += 1
    
    print()
    print("Checking Backend Files...")
    print("-" * 70)
    
    backend_files = [
        ("main.py", "FastAPI application"),
        ("app/__init__.py", "App package init"),
        ("app/config.py", "Configuration module"),
        ("app/db.py", "Database module"),
        ("app/models.py", "SQLAlchemy models"),
        ("app/schemas.py", "Pydantic schemas"),
        ("app/auth.py", "Authentication module"),
        ("app/ml.py", "ML module"),
        ("app/routes_auth.py", "Auth routes"),
        ("app/routes_reco.py", "Recommendation routes"),
        ("app/routes_sms.py", "SMS routes"),
        ("app/routes_telemed.py", "Telemedicine routes"),
    ]
    
    for file_path, desc in backend_files:
        checks_total += 1
        if check_file(file_path, desc):
            checks_passed += 1
    
    print()
    print("Checking Frontend Files...")
    print("-" * 70)
    
    frontend_files = [
        ("ui/index.html", "Login page"),
        ("ui/dashboard.html", "Dashboard page"),
        ("ui/styles.css", "Stylesheet"),
        ("ui/app.js", "Dashboard JavaScript"),
        ("ui/gauge.js", "Gauge visualization"),
    ]
    
    for file_path, desc in frontend_files:
        checks_total += 1
        if check_file(file_path, desc):
            checks_passed += 1
    
    print()
    print("Checking Test Files...")
    print("-" * 70)
    
    test_files = [
        ("tests/__init__.py", "Tests package init"),
        ("tests/conftest.py", "Pytest configuration"),
        ("tests/test_auth.py", "Authentication tests"),
        ("tests/test_recommend.py", "Recommendation tests"),
        ("tests/test_cases.py", "Case management tests"),
    ]
    
    for file_path, desc in test_files:
        checks_total += 1
        if check_file(file_path, desc):
            checks_passed += 1
    
    print()
    print("Checking Documentation...")
    print("-" * 70)
    
    doc_files = [
        ("README.md", "Main documentation"),
        ("QUICKSTART.md", "Quick start guide"),
        ("PROJECT_SUMMARY.md", "Project summary"),
        ("requirements.txt", "Python dependencies"),
    ]
    
    for file_path, desc in doc_files:
        checks_total += 1
        if check_file(file_path, desc):
            checks_passed += 1
    
    print()
    print("Checking Setup Scripts...")
    print("-" * 70)
    
    script_files = [
        ("run_api.ps1", "Windows run script"),
        ("run_api.sh", "Linux/Mac run script"),
        ("setup_env.ps1", "Windows env setup"),
        ("setup_env.sh", "Linux/Mac env setup"),
    ]
    
    for file_path, desc in script_files:
        checks_total += 1
        if check_file(file_path, desc):
            checks_passed += 1
    
    print()
    print("Checking ML Models...")
    print("-" * 70)
    
    model_files = [
        ("models/screening_hp_pos_calibrated.joblib", "Screening model"),
        ("models/staging_3class.joblib", "Staging model"),
    ]
    
    for file_path, desc in model_files:
        checks_total += 1
        if check_file(file_path, desc):
            checks_passed += 1
    
    print()
    print("Checking Configuration...")
    print("-" * 70)
    
    if Path(".env").exists():
        print("[OK] .env file exists")
        checks_passed += 1
    else:
        print("[WARNING] .env file NOT FOUND - You need to create it!")
        print("   Run: .\\setup_env.ps1 (Windows) or ./setup_env.sh (Linux/Mac)")
    checks_total += 1
    
    print()
    print("=" * 70)
    print(f"Verification Complete: {checks_passed}/{checks_total} checks passed")
    print("=" * 70)
    print()
    
    if checks_passed == checks_total:
        print("SUCCESS! All files are in place!")
        print()
        print("Next steps:")
        print("1. Create .env file: .\\setup_env.ps1 or ./setup_env.sh")
        print("2. Run the application: .\\run_api.ps1 or ./run_api.sh")
        print("3. Open browser: http://localhost:8000/ui/index.html")
        return 0
    elif checks_passed >= checks_total * 0.8:
        print("WARNING: Most files are in place, but some are missing.")
        print("Review the missing items above.")
        return 1
    else:
        print("ERROR: Many files are missing. Please ensure all files are created.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
