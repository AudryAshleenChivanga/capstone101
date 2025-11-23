"""
Test script for local registration functionality
Run this to test without starting the full server
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all imports work"""
    print("Testing imports...")
    try:
        from app.routes_auth import router
        print("[OK] Auth routes imported successfully")
        
        from app.db import create_tables, get_db
        print("[OK] Database module imported successfully")
        
        from app.models import User
        print("[OK] Models imported successfully")
        
        from app.auth import hash_password
        print("[OK] Auth functions imported successfully")
        
        return True
    except Exception as e:
        print(f"[ERROR] Import error: {e}")
        return False

def test_database():
    """Test database connection"""
    print("\nTesting database...")
    try:
        from app.db import create_tables, SessionLocal
        from app.models import User
        
        # Create tables
        create_tables()
        print("[OK] Database tables created/verified")
        
        # Test query
        db = SessionLocal()
        user_count = db.query(User).count()
        print(f"[OK] Database query successful: {user_count} users found")
        db.close()
        
        return True
    except Exception as e:
        print(f"[ERROR] Database error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_registration_endpoint():
    """Test the registration endpoint logic"""
    print("\nTesting registration endpoint...")
    try:
        from app.routes_auth import register_public_user
        from app.schemas import UserCreate
        from app.db import SessionLocal
        from app.models import User
        
        # Create test user data
        test_user = UserCreate(
            username="testuser_" + str(os.urandom(4).hex()),
            email=f"test_{os.urandom(4).hex()}@example.com",
            password="Test@12345",
            full_name="Test User",
            specialty="General Practice",
            institution="Test Hospital",
            license_number="TEST123",
            role="clinician"
        )
        
        # Call registration function
        db = SessionLocal()
        try:
            result = register_public_user(test_user, db)
            print(f"[OK] Registration successful!")
            print(f"   User ID: {result.id}")
            print(f"   Username: {result.username}")
            print(f"   Email: {result.email}")
            print(f"   Role: {result.role}")
            print(f"   Active: {result.is_active}")
            return True
        finally:
            db.close()
            
    except Exception as e:
        print(f"[ERROR] Registration error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_login():
    """Test login with admin user"""
    print("\nTesting login...")
    try:
        from app.auth import authenticate_user
        from app.db import SessionLocal
        
        db = SessionLocal()
        try:
            # Test with default admin
            user = authenticate_user(db, "admin", "Admin@2024")
            if user:
                print(f"[OK] Login successful!")
                print(f"   Username: {user.username}")
                print(f"   Role: {user.role}")
                return True
            else:
                print("[ERROR] Login failed: Invalid credentials")
                return False
        finally:
            db.close()
            
    except Exception as e:
        print(f"[ERROR] Login error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("H. pylori CDSS - Local Registration Test")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Database", test_database()))
    results.append(("Registration", test_registration_endpoint()))
    results.append(("Login", test_login()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{test_name:20s}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed! Registration is working correctly.")
        print("\nNext steps:")
        print("1. Start the server: python -m uvicorn main:app --reload")
        print("2. Open browser: http://localhost:8000/ui/signup.html")
        print("3. Test the signup form")
    else:
        print("\n[WARNING] Some tests failed. Please review the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
