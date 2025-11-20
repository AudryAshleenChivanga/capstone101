"""
Create custom users in production - EDIT THIS FILE with your usernames
Run this in Render Shell: python create_custom_users.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db import SessionLocal, create_tables
from app.models import User
from app.auth import get_password_hash

def create_user(username, email, password, role, full_name, specialty="General Practice"):
    """Create a user in production database"""
    db = SessionLocal()
    
    try:
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print(f"[EXISTS] User '{username}' already exists - skipping")
            return False
        
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=get_password_hash(password),
            role=role,
            specialty=specialty,
            institution="H. pylori CDSS",
            is_active=True
        )
        
        db.add(user)
        db.commit()
        
        print(f"[SUCCESS] Created {role}: {username}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()

# ============================================================================
# EDIT THESE WITH YOUR DESIRED USERNAMES AND PASSWORDS
# ============================================================================

users_to_create = [
    {
        "username": "dr_john",           # CHANGE THIS
        "email": "john@hospital.com",     # CHANGE THIS
        "password": "SecurePass123!",     # CHANGE THIS
        "role": "clinician",
        "full_name": "Dr. John Doe",      # CHANGE THIS
        "specialty": "General Medicine"
    },
    {
        "username": "dr_mary",            # CHANGE THIS
        "email": "mary@hospital.com",     # CHANGE THIS
        "password": "SecurePass456!",     # CHANGE THIS
        "role": "specialist",
        "full_name": "Dr. Mary Smith",    # CHANGE THIS
        "specialty": "Gastroenterology"
    }
]

# ============================================================================
# DON'T EDIT BELOW THIS LINE
# ============================================================================

def main():
    print("="*60)
    print("CUSTOM USER CREATION FOR PRODUCTION")
    print("="*60)
    print()
    
    create_tables()
    print("[OK] Database ready\n")
    
    success_count = 0
    for user_data in users_to_create:
        if create_user(**user_data):
            success_count += 1
        print()
    
    print("="*60)
    print(f"Created {success_count} of {len(users_to_create)} users")
    print("="*60)
    print("\nLOGIN CREDENTIALS:")
    for user_data in users_to_create:
        print(f"\n{user_data['role'].upper()}:")
        print(f"  Username: {user_data['username']}")
        print(f"  Password: {user_data['password']}")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()

