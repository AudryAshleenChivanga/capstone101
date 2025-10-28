"""
Database migration script to add the appointments table.
Run this script to update the database schema with the new appointment scheduling functionality.
"""
import sys
from sqlalchemy import create_engine, inspect, text
from app.config import settings
from app.db import Base
from app.models import User, Case, TelemedSession, Appointment

def migrate_database():
    """Add appointments table to existing database."""
    print("[*] Starting database migration for appointment scheduling...")
    
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        inspector = inspect(engine)
        
        # Check if appointments table already exists
        if 'appointments' in inspector.get_table_names():
            print("[OK] Appointments table already exists. No migration needed.")
            return
        
        print("[*] Creating appointments table...")
        
        # Create only the new tables
        Appointment.__table__.create(engine, checkfirst=True)
        
        # Also update telemed_sessions table to add appointment_id column if it doesn't exist
        existing_columns = [col['name'] for col in inspector.get_columns('telemed_sessions')]
        if 'appointment_id' not in existing_columns:
            print("[*] Adding appointment_id column to telemed_sessions table...")
            with engine.connect() as conn:
                conn.execute(text('ALTER TABLE telemed_sessions ADD COLUMN appointment_id INTEGER'))
                conn.commit()
            print("[OK] Added appointment_id column to telemed_sessions")
        
        print("[OK] Database migration completed successfully!")
        print("\n[INFO] New table created:")
        print("   - appointments (for scheduling consultations)")
        print("\n[SUCCESS] You can now use the appointment scheduling feature!")
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate_database()

