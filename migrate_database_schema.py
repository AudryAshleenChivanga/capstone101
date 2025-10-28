"""
Database Migration Script - Add Patient Management System
This script migrates the existing database to include the new Patient table and updated Case table.
"""
import sqlite3
from datetime import datetime

DB_PATH = "cdss.db"

def migrate_database():
    """Migrate the database schema to add new Patient table and update Cases table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("[*] Starting database migration...")
    
    try:
        # Step 1: Create the new patients table
        print("[1/5] Creating patients table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id VARCHAR(50) UNIQUE NOT NULL,
                full_name VARCHAR(200),
                date_of_birth DATETIME,
                age INTEGER,
                sex VARCHAR(10),
                residence VARCHAR(200),
                phone VARCHAR(50),
                email VARCHAR(255),
                blood_type VARCHAR(10),
                allergies TEXT,
                medical_history TEXT,
                created_by INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                notes TEXT,
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        """)
        print("    ✓ Patients table created")
        
        # Step 2: Check if patient_db_id column exists in cases table
        print("[2/5] Checking cases table schema...")
        cursor.execute("PRAGMA table_info(cases)")
        columns = [col[1] for col in cursor.fetchall()]
        
        needs_migration = 'patient_db_id' not in columns or 'case_type' not in columns
        
        if needs_migration:
            print("[3/5] Migrating cases table...")
            
            # Create a new cases table with updated schema
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cases_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    patient_db_id INTEGER,
                    input_data TEXT NOT NULL,
                    case_type VARCHAR(50),
                    screen_prob FLOAT,
                    stage_pred VARCHAR(50),
                    recommendations TEXT,
                    edited_recommendations TEXT,
                    signed_by INTEGER,
                    signature_data TEXT,
                    signed_at DATETIME,
                    is_approved INTEGER DEFAULT 0,
                    pdf_path VARCHAR(500),
                    sent_to_patient INTEGER DEFAULT 0,
                    sent_at DATETIME,
                    patient_phone VARCHAR(50),
                    patient_email VARCHAR(255),
                    patient_pseudo_id VARCHAR(100),
                    patient_name VARCHAR(200),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (patient_db_id) REFERENCES patients(id),
                    FOREIGN KEY (signed_by) REFERENCES users(id)
                )
            """)
            
            # Copy data from old table to new table
            cursor.execute("""
                INSERT INTO cases_new (
                    id, user_id, input_data, screen_prob, stage_pred,
                    recommendations, edited_recommendations, signed_by,
                    signature_data, signed_at, is_approved, pdf_path,
                    sent_to_patient, sent_at, patient_phone, patient_email,
                    patient_pseudo_id, patient_name, created_at, notes
                )
                SELECT 
                    id, user_id, input_data, screen_prob, stage_pred,
                    recommendations, edited_recommendations, signed_by,
                    signature_data, signed_at, is_approved, pdf_path,
                    sent_to_patient, sent_at, patient_phone, patient_email,
                    patient_pseudo_id, patient_name, created_at, notes
                FROM cases
            """)
            
            # Drop old table and rename new one
            cursor.execute("DROP TABLE cases")
            cursor.execute("ALTER TABLE cases_new RENAME TO cases")
            print("    ✓ Cases table migrated successfully")
        else:
            print("[3/5] Cases table already up to date")
        
        # Step 4: Create indexes for better performance
        print("[4/5] Creating indexes for better performance...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cases_patient_id ON cases(patient_pseudo_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cases_created_at ON cases(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cases_type ON cases(case_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_patients_patient_id ON patients(patient_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_search ON patients(patient_id, full_name, phone)")
        print("    ✓ Indexes created")
        
        # Step 5: Migrate existing cases to create patient records
        print("[5/5] Creating patient records from existing cases...")
        cursor.execute("""
            SELECT DISTINCT patient_pseudo_id, patient_name, patient_phone, patient_email, user_id
            FROM cases 
            WHERE patient_pseudo_id IS NOT NULL AND patient_pseudo_id != ''
        """)
        
        existing_cases = cursor.fetchall()
        migrated_count = 0
        
        for case_data in existing_cases:
            patient_pseudo_id, patient_name, patient_phone, patient_email, user_id = case_data
            
            # Check if patient already exists
            cursor.execute("SELECT id FROM patients WHERE patient_id = ?", (patient_pseudo_id,))
            existing_patient = cursor.fetchone()
            
            if not existing_patient:
                # Create patient record
                cursor.execute("""
                    INSERT INTO patients (patient_id, full_name, phone, email, created_by, is_active)
                    VALUES (?, ?, ?, ?, ?, 1)
                """, (patient_pseudo_id, patient_name, patient_phone, patient_email, user_id))
                
                patient_id = cursor.lastrowid
                
                # Update cases with patient_db_id
                cursor.execute("""
                    UPDATE cases 
                    SET patient_db_id = ?
                    WHERE patient_pseudo_id = ?
                """, (patient_id, patient_pseudo_id))
                
                migrated_count += 1
        
        print(f"    ✓ Created {migrated_count} patient records from existing cases")
        
        # Commit all changes
        conn.commit()
        print("\n✅ Database migration completed successfully!")
        print(f"   - Patients table: Created")
        print(f"   - Cases table: Updated with new columns")
        print(f"   - Indexes: Created for performance")
        print(f"   - Data: Migrated {migrated_count} patient records")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("="*60)
    print("H. pylori CDSS - Database Migration Script")
    print("="*60)
    migrate_database()
    print("\n✅ You can now restart your application!")
    print("="*60)

