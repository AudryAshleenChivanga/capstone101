"""
Test script to verify login works with both email and username
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db import SessionLocal
from app.auth import authenticate_user, hash_password
from app.models import User

def test_authentication():
    """Test that login works with both email and username"""
    print("=" * 60)
    print("Testing Login with Email/Username")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Create a test user
        test_email = f"test_{os.urandom(4).hex()}@example.com"
        test_username = f"testuser_{os.urandom(4).hex()}"
        test_password = "Test@12345"
        
        print(f"\n1. Creating test user...")
        print(f"   Email: {test_email}")
        print(f"   Username: {test_username}")
        print(f"   Password: {test_password}")
        
        new_user = User(
            username=test_username,
            email=test_email,
            hashed_password=hash_password(test_password),
            role="clinician",
            full_name="Test User",
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"   [OK] User created with ID: {new_user.id}")
        
        # Test 1: Login with username
        print(f"\n2. Testing login with USERNAME...")
        user = authenticate_user(db, test_username, test_password)
        if user:
            print(f"   [OK] Login successful!")
            print(f"   User ID: {user.id}")
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
        else:
            print(f"   [FAIL] Login with username failed!")
            return False
        
        # Test 2: Login with email
        print(f"\n3. Testing login with EMAIL...")
        user = authenticate_user(db, test_email, test_password)
        if user:
            print(f"   [OK] Login successful!")
            print(f"   User ID: {user.id}")
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
        else:
            print(f"   [FAIL] Login with email failed!")
            return False
        
        # Test 3: Login with wrong password
        print(f"\n4. Testing login with WRONG PASSWORD...")
        user = authenticate_user(db, test_email, "WrongPassword123")
        if user:
            print(f"   [FAIL] Login should have failed with wrong password!")
            return False
        else:
            print(f"   [OK] Login correctly rejected wrong password")
        
        print("\n" + "=" * 60)
        print("[SUCCESS] All authentication tests passed!")
        print("=" * 60)
        print("\nUsers can now login with either:")
        print("  - Their email address")
        print("  - Their username")
        print("\nBoth will work correctly!")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_authentication()
    sys.exit(0 if success else 1)

