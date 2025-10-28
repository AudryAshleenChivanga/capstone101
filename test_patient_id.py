"""Quick script to test if Patient IDs are being generated."""
from app.db import SessionLocal
from app.models import Case, Patient

db = SessionLocal()

# Get the most recent case
case = db.query(Case).order_by(Case.id.desc()).first()

if case:
    print(f"✅ Case Found!")
    print(f"   Case ID: {case.id}")
    print(f"   Patient DB ID: {case.patient_db_id}")
    print(f"   Patient Pseudo ID (old field): {case.patient_pseudo_id}")
    print(f"   Patient Name (old field): {case.patient_name}")
    
    # Get the linked patient
    if case.patient_db_id:
        patient = db.query(Patient).filter(Patient.id == case.patient_db_id).first()
        if patient:
            print(f"\n✅ Linked Patient Found!")
            print(f"   Patient ID: {patient.patient_id}")
            print(f"   Full Name: {patient.full_name}")
            print(f"   Age: {patient.age}")
            print(f"   Sex: {patient.sex}")
        else:
            print("\n❌ No patient found with that ID")
    else:
        print("\n❌ Case not linked to any patient")
else:
    print("❌ No cases in database")

db.close()

