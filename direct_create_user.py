"""Direct database user creation - bypasses API"""
import sys
sys.path.insert(0, '.')

from app.db import SessionLocal, create_tables
from app.models import User
from app.auth import hash_password

# Create tables
create_tables()

# Create session
db = SessionLocal()

try:
    # Check if user exists
    existing = db.query(User).filter(User.username == "admin").first()
    
    if existing:
        print("=" * 60)
        print("Admin user already exists!")
        print("=" * 60)
        print()
        print("Try logging in with:")
        print("  Username: admin")
        print("  Password: Admin@2024")
        print()
    else:
        # Create admin user
        admin = User(
            username="admin",
            email="admin@hospital.com",
            hashed_password=hash_password("Admin@2024"),
            role="admin",
            is_active=1
        )
        
        db.add(admin)
        db.commit()
        
        print("=" * 60)
        print("SUCCESS! Admin account created!")
        print("=" * 60)
        print()
        print("Your Login Credentials:")
        print("  Username: admin")
        print("  Email:    admin@hospital.com")
        print("  Password: Admin@2024")
        print("  Role:     Administrator")
        print()
        print("Login at: http://localhost:8000/ui/index.html")
        print()
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
