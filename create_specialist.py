"""Create a test specialist (gastroenterologist) user for teleconsultation testing."""
from app.db import SessionLocal
from app.models import User
from app.auth import get_password_hash

def create_specialist():
    db = SessionLocal()
    try:
        # Check if specialist already exists
        existing = db.query(User).filter(User.username == 'dr_gastro').first()
        if existing:
            print("Specialist 'dr_gastro' already exists!")
            print(f"Username: {existing.username}")
            print(f"Email: {existing.email}")
            print(f"Role: {existing.role}")
            print(f"Specialty: {existing.specialty}")
            return
        
        # Create new specialist
        specialist = User(
            username='dr_gastro',
            email='gastro@hospital.com',
            hashed_password=get_password_hash('Gastro123!'),
            role='specialist',
            full_name='Dr. Sarah Johnson',
            specialty='Gastroenterology',
            institution='City General Hospital',
            phone='+1234567890',
            bio='Board-certified gastroenterologist with 15 years experience in H. pylori management',
            is_active=1
        )
        
        db.add(specialist)
        db.commit()
        db.refresh(specialist)
        
        print("=" * 50)
        print("SUCCESS: Specialist User Created!")
        print("=" * 50)
        print(f"\nUsername: {specialist.username}")
        print(f"Password: Gastro123!")
        print(f"Email: {specialist.email}")
        print(f"Role: {specialist.role}")
        print(f"Specialty: {specialist.specialty}")
        print(f"Institution: {specialist.institution}")
        print(f"\nYou can now login and test teleconsultation booking!")
        print("=" * 50)
        
    except Exception as e:
        print(f"ERROR: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_specialist()

