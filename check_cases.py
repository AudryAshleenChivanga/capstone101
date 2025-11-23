from app.db import SessionLocal
from app.models import Case

db = SessionLocal()
cases = db.query(Case).all()

print(f"\nTotal cases in database: {len(cases)}\n")

if cases:
    print("Recent cases:")
    for c in cases[:10]:
        print(f"  Case {c.id}: Patient {c.patient_pseudo_id or 'N/A'} - {c.case_type or 'N/A'} - {c.created_at}")
else:
    print("❌ NO CASES FOUND IN DATABASE!")
    print("\nThis is why Case History is empty.")
    print("Create some cases by using the Screening or Staging forms.")

db.close()

