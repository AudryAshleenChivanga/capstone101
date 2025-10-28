"""
Direct admin user creation script - adds admin to database on startup
"""
import sys
import os

# Add the app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User
from app.auth import get_password_hash

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cdss.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Create session
db = SessionLocal()

try:
    # Check if admin exists
    admin = db.query(User).filter(User.username == "admin").first()
    
    if admin:
        print("ℹ️  Admin user already exists - updating password...")
        admin.hashed_password = get_password_hash("Admin@2024")
        db.commit()
        print("✅ Admin password updated successfully!")
    else:
        print("🔧 Creating admin user...")
        admin_user = User(
            username="admin",
            email="admin@hpylori.com",
            full_name="Administrator",
            hashed_password=get_password_hash("Admin@2024"),
            role="admin",
            specialty="Gastroenterology",
            institution="H. pylori CDSS Hospital",
            license_number="ADMIN001",
            bio="System Administrator",
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        print("✅ Admin user created successfully!")
    
    print("👤 Username: admin")
    print("🔑 Password: Admin@2024")
    print("🚀 Ready to login!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
    sys.exit(1)
finally:
    db.close()

