"""
Verify the statistics fix will count cases correctly.
"""
from app.db import SessionLocal
from app.models import Case

db = SessionLocal()

try:
    cases = db.query(Case).all()
    
    # NEW LOGIC (with fallback to case_type)
    screening_cases = sum(1 for c in cases if (
        c.input_data.get('task') == "screening" or 
        c.case_type in ["screening", "symptom_assessment", "lab_screening"]
    ))
    
    staging_cases = sum(1 for c in cases if (
        c.input_data.get('task') == "staging" or 
        c.case_type in ["staging", "resistance_staging"]
    ))
    
    print("\n" + "="*60)
    print("STATISTICS WITH NEW LOGIC (Backend Fix)")
    print("="*60)
    print(f"Total Cases: {len(cases)}")
    print(f"Screening Cases: {screening_cases}")
    print(f"Staging Cases: {staging_cases}")
    print("="*60)
    
    print("\nBREAKDOWN:")
    print("-" * 60)
    
    # Count by case_type
    symptom = sum(1 for c in cases if c.case_type == "symptom_assessment")
    lab = sum(1 for c in cases if c.case_type == "lab_screening")
    resistance = sum(1 for c in cases if c.case_type == "resistance_staging")
    screening_direct = sum(1 for c in cases if c.case_type == "screening")
    staging_direct = sum(1 for c in cases if c.case_type == "staging")
    
    print(f"  symptom_assessment: {symptom}")
    print(f"  lab_screening: {lab}")
    print(f"  resistance_staging: {resistance}")
    print(f"  screening (direct): {screening_direct}")
    print(f"  staging (direct): {staging_direct}")
    print()
    print(f"SCREENING total = symptom_assessment + lab_screening + screening")
    print(f"                = {symptom} + {lab} + {screening_direct}")
    print(f"                = {screening_cases}")
    print()
    print(f"STAGING total = resistance_staging + staging")
    print(f"              = {resistance} + {staging_direct}")
    print(f"              = {staging_cases}")
    print("="*60)
    
finally:
    db.close()

