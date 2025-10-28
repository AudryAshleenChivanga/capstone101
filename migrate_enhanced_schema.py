"""
Database Migration Script for Enhanced H. pylori CDSS
Adds: Prescription, ModelTraining tables and updates Case table for multi-stage workflow
"""

import sqlite3
from datetime import datetime

def migrate_database():
    """Migrate the database to include new tables and columns."""
    
    db_path = "cdss.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("H. pylori CDSS - Enhanced Schema Migration")
    print("=" * 60)
    print(f"[*] Starting migration at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Step 1: Add new columns to cases table
        print("\n[1/3] Updating cases table with multi-stage workflow support...")
        
        new_case_columns = [
            ("workflow_stage", "VARCHAR(50)"),
            ("stage1_assessment", "TEXT"),  # JSON
            ("stage2_lab_results", "TEXT"),  # JSON
            ("stage3_ric_values", "TEXT"),  # JSON
            ("symptom_risk_level", "VARCHAR(50)"),
            ("lab_recommendation", "TEXT"),
        ]
        
        for col_name, col_type in new_case_columns:
            try:
                cursor.execute(f"ALTER TABLE cases ADD COLUMN {col_name} {col_type}")
                print(f"    ✓ Added column: {col_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column" in str(e).lower():
                    print(f"    ⊙ Column already exists: {col_name}")
                else:
                    print(f"    ✗ Error adding {col_name}: {e}")
        
        # Create index on workflow_stage
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_case_workflow_stage ON cases(workflow_stage)")
            print("    ✓ Created index on workflow_stage")
        except Exception as e:
            print(f"    ⊙ Index creation info: {e}")
        
        # Step 2: Create prescriptions table
        print("\n[2/3] Creating prescriptions table...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prescriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                case_id INTEGER NOT NULL,
                prescribed_by INTEGER NOT NULL,
                medications TEXT NOT NULL,
                diagnosis TEXT NOT NULL,
                recommendations TEXT,
                lifestyle_advice TEXT,
                follow_up_days INTEGER,
                stage VARCHAR(50),
                protocol_type VARCHAR(100),
                lab_tests_ordered TEXT,
                status VARCHAR(50) DEFAULT 'pending',
                dispensed_at DATETIME,
                completed_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients (id),
                FOREIGN KEY (case_id) REFERENCES cases (id),
                FOREIGN KEY (prescribed_by) REFERENCES users (id)
            )
        """)
        print("    ✓ Prescriptions table created")
        
        # Create indexes for prescriptions
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prescription_patient ON prescriptions(patient_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prescription_case ON prescriptions(case_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prescription_status ON prescriptions(status)")
        print("    ✓ Created indexes on prescriptions table")
        
        # Step 3: Create model_training table
        print("\n[3/3] Creating model_training table...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_training (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name VARCHAR(100) NOT NULL,
                model_version VARCHAR(50) NOT NULL,
                model_type VARCHAR(50) NOT NULL,
                training_start DATETIME NOT NULL,
                training_end DATETIME,
                status VARCHAR(50) DEFAULT 'training',
                dataset_size INTEGER,
                training_samples INTEGER,
                validation_samples INTEGER,
                test_samples INTEGER,
                accuracy REAL,
                precision REAL,
                recall REAL,
                f1_score REAL,
                auc_roc REAL,
                other_metrics TEXT,
                model_path VARCHAR(500),
                config_data TEXT,
                is_production INTEGER DEFAULT 0,
                deployed_at DATETIME,
                replaced_at DATETIME,
                trained_by INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (trained_by) REFERENCES users (id)
            )
        """)
        print("    ✓ Model training table created")
        
        # Create indexes for model_training
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_model_name ON model_training(model_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_model_production ON model_training(is_production)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_model_status ON model_training(status)")
        print("    ✓ Created indexes on model_training table")
        
        # Commit all changes
        conn.commit()
        
        # Summary
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
        print("\nNew capabilities:")
        print("  • Multi-stage workflow (Symptom → Lab → RIC)")
        print("  • Prescription management system")
        print("  • Model training and retraining tracking")
        print("\nYou can now:")
        print("  1. Create prescriptions for patients")
        print("  2. Track cases through multiple assessment stages")
        print("  3. Monitor and retrain ML models")
        print("\nRestart your application to apply changes!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()

