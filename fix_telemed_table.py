"""Fix telemed_sessions table to add appointment_id column."""
from app.db import SessionLocal, engine
from sqlalchemy import inspect, text

def fix_telemed_table():
    db = SessionLocal()
    try:
        inspector = inspect(engine)
        columns = [c['name'] for c in inspector.get_columns('telemed_sessions')]
        
        print(f"Current columns in telemed_sessions: {columns}")
        
        if 'appointment_id' not in columns:
            print("Adding appointment_id column...")
            db.execute(text('ALTER TABLE telemed_sessions ADD COLUMN appointment_id INTEGER REFERENCES appointments(id)'))
            db.commit()
            print("SUCCESS: Added appointment_id column")
        else:
            print("SUCCESS: appointment_id column already exists")
            
    except Exception as e:
        print(f"ERROR: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_telemed_table()

