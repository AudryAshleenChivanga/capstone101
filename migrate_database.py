"""Quick database migration script to add new columns."""
import sqlite3
import os

# Path to database
DB_PATH = "cdss.db"

print("=== Database Migration Script ===")
print("")

if not os.path.exists(DB_PATH):
    print("ERROR: Database file not found!")
    print("Just run the app and it will create a new database.")
    exit(1)

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("[1/2] Adding new columns to 'users' table...")

# List of new columns to add
user_columns = [
    ("full_name", "VARCHAR(200)"),
    ("phone", "VARCHAR(50)"),
    ("specialty", "VARCHAR(100)"),
    ("license_number", "VARCHAR(100)"),
    ("institution", "VARCHAR(200)"),
    ("bio", "TEXT"),
    ("profile_photo", "VARCHAR(500)"),
    ("digital_signature", "TEXT"),
]

for col_name, col_type in user_columns:
    try:
        cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
        print(f"  [OK] Added {col_name}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"  [SKIP] {col_name} already exists")
        else:
            print(f"  [ERROR] Error adding {col_name}: {e}")

print("")
print("[2/2] Adding new columns to 'cases' table...")

# List of new columns for cases
case_columns = [
    ("edited_recommendations", "JSON"),
    ("signed_by", "INTEGER"),
    ("signature_data", "TEXT"),
    ("signed_at", "DATETIME"),
    ("is_approved", "INTEGER DEFAULT 0"),
    ("pdf_path", "VARCHAR(500)"),
    ("sent_to_patient", "INTEGER DEFAULT 0"),
    ("sent_at", "DATETIME"),
    ("patient_phone", "VARCHAR(50)"),
    ("patient_email", "VARCHAR(255)"),
    ("patient_name", "VARCHAR(200)"),
]

for col_name, col_type in case_columns:
    try:
        cursor.execute(f"ALTER TABLE cases ADD COLUMN {col_name} {col_type}")
        print(f"  [OK] Added {col_name}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"  [SKIP] {col_name} already exists")
        else:
            print(f"  [ERROR] Error adding {col_name}: {e}")

# Commit changes
conn.commit()
conn.close()

print("")
print("=" * 50)
print("[SUCCESS] Database migration complete!")
print("=" * 50)
print("")
print("Next steps:")
print("  1. The server should now work properly")
print("  2. Try logging in again at http://localhost:8000/ui/index.html")
print("  3. Your existing data is preserved!")
print("")
