"""
Create users directly in production database (Render PostgreSQL)
Run this script in Render Shell or locally pointing to production DB
"""
import os
import sys

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db import SessionLocal, create_tables
from app.models import User
from app.auth import get_password_hash

def create_user(username, email, password, role, full_name=None, specialty=None, institution=None):
    """Create a user in the database"""
    db = SessionLocal()
    
    try:
        # Check if user exists
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print(f"[WARNING] User '{username}' already exists!")
            return False
        
        # Create user
        user = User(
            username=username,
            email=email,
            full_name=full_name or username.title(),
            hashed_password=get_password_hash(password),
            role=role,
            specialty=specialty or "General Practice",
            institution=institution or "H. pylori CDSS",
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"[SUCCESS] Created {role}: {username}")
        print(f"  Email: {email}")
        print(f"  Full Name: {user.full_name}")
        print(f"  Role: {role}")
        print()
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to create user '{username}': {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

def main():
    print("="*60)
    print("PRODUCTION USER CREATION SCRIPT")
    print("="*60)
    print()
    
    # Ensure tables exist
    print("Ensuring database tables exist...")
    create_tables()
    print("[OK] Database ready")
    print()
    
    # Create admin
    print("Creating Admin user...")
    create_user(
        username="admin",
        email="admin@hpylori.com",
        password="Admin@2024",
        role="admin",
        full_name="System Administrator",
        specialty="Administration",
        institution="H. pylori CDSS"
    )
    
    # Create clinician
    print("Creating Clinician user...")
    create_user(
        username="clinician",
        email="clinician@hpylori.com",
        password="Clinician@2024",
        role="clinician",
        full_name="Dr. Clinical Staff",
        specialty="General Practice",
        institution="District Hospital"
    )
    
    # Create specialist
    print("Creating Specialist user...")
    create_user(
        username="specialist",
        email="specialist@hpylori.com",
        password="Specialist@2024",
        role="specialist",
        full_name="Dr. Gastro Specialist",
        specialty="Gastroenterology",
        institution="Referral Hospital"
    )
    
    print("="*60)
    print("SUMMARY - PRODUCTION CREDENTIALS")
    print("="*60)
    print()
    print("1. ADMIN:")
    print("   Username: admin")
    print("   Password: Admin@2024")
    print("   Role: admin")
    print()
    print("2. CLINICIAN:")
    print("   Username: clinician")
    print("   Password: Clinician@2024")
    print("   Role: clinician")
    print()
    print("3. SPECIALIST:")
    print("   Username: specialist")
    print("   Password: Specialist@2024")
    print("   Role: specialist")
    print()
    print("="*60)
    print("Access your deployment at:")
    print("https://h-pylori-cdss.onrender.com/")
    print("="*60)

if __name__ == "__main__":
    main()

