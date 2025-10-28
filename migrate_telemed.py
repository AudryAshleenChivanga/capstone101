"""Migration script for telemed_sessions table."""
import sqlite3
import os

DB_PATH = "cdss.db"

print("=== Telemed Sessions Table Migration ===")
print("")

if not os.path.exists(DB_PATH):
    print("[NOTICE] Database will be created when server starts")
    exit(0)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("[1/1] Updating telemed_sessions table...")

# Check if table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='telemed_sessions'")
table_exists = cursor.fetchone()

if not table_exists:
    print("  [NOTICE] telemed_sessions table doesn't exist yet - will be created on server start")
    conn.close()
    exit(0)

# Rename old column if it exists
try:
    cursor.execute("ALTER TABLE telemed_sessions RENAME COLUMN created_by_user_id TO host_id")
    print("  [OK] Renamed created_by_user_id to host_id")
except sqlite3.OperationalError:
    print("  [SKIP] host_id already correct")

# Add new columns
new_columns = [
    ("ended_at", "DATETIME"),
]

for col_name, col_type in new_columns:
    try:
        cursor.execute(f"ALTER TABLE telemed_sessions ADD COLUMN {col_name} {col_type}")
        print(f"  [OK] Added {col_name}")
    except sqlite3.OperationalError:
        print(f"  [SKIP] {col_name} already exists")

# Remove token column if it exists (we use session-based tokens now)
# SQLite doesn't support DROP COLUMN easily, so we'll leave it

conn.commit()
conn.close()

print("")
print("[SUCCESS] Telemed sessions table updated!")
print("")
