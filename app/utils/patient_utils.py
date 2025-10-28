"""Utility functions for patient management."""
import random
import string
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Patient


def generate_patient_id(db: Session) -> str:
    """
    Generate a unique patient ID in format: HP-YYYY-XXXX
    Where:
    - HP = H. pylori
    - YYYY = Current year
    - XXXX = 4-digit sequential/random number
    """
    year = datetime.now().year
    
    # Try to find the last patient ID for this year
    prefix = f"HP-{year}-"
    last_patient = (
        db.query(Patient)
        .filter(Patient.patient_id.like(f"{prefix}%"))
        .order_by(Patient.patient_id.desc())
        .first()
    )
    
    if last_patient and last_patient.patient_id:
        try:
            # Extract the number part and increment
            last_number = int(last_patient.patient_id.split('-')[-1])
            new_number = last_number + 1
        except (ValueError, IndexError):
            # If parsing fails, start from 1
            new_number = 1
    else:
        # First patient of the year
        new_number = 1
    
    # Format with leading zeros (4 digits)
    patient_id = f"{prefix}{new_number:04d}"
    
    # Ensure uniqueness (in case of race conditions)
    while db.query(Patient).filter(Patient.patient_id == patient_id).first():
        new_number += 1
        patient_id = f"{prefix}{new_number:04d}"
    
    return patient_id


def search_patients(
    db: Session,
    patient_id: str = None,
    name: str = None,
    phone: str = None,
    email: str = None
) -> list:
    """
    Search for patients by various criteria.
    Returns a list of matching patients.
    """
    query = db.query(Patient).filter(Patient.is_active == 1)
    
    if patient_id:
        query = query.filter(Patient.patient_id.ilike(f"%{patient_id}%"))
    
    if name:
        query = query.filter(Patient.full_name.ilike(f"%{name}%"))
    
    if phone:
        query = query.filter(Patient.phone.ilike(f"%{phone}%"))
    
    if email:
        query = query.filter(Patient.email.ilike(f"%{email}%"))
    
    return query.order_by(Patient.created_at.desc()).all()


def get_or_create_patient(
    db: Session,
    patient_id: str = None,
    full_name: str = None,
    age: int = None,
    sex: str = None,
    residence: str = None,
    phone: str = None,
    email: str = None,
    created_by: int = None
) -> Patient:
    """
    Get existing patient by ID or create a new one.
    This ensures no duplicate patients are created.
    """
    # If patient_id provided, try to find existing patient
    if patient_id:
        existing = db.query(Patient).filter(
            Patient.patient_id == patient_id,
            Patient.is_active == 1
        ).first()
        
        if existing:
            # Update patient info if provided
            if full_name:
                existing.full_name = full_name
            if age:
                existing.age = age
            if sex:
                existing.sex = sex
            if residence:
                existing.residence = residence
            if phone:
                existing.phone = phone
            if email:
                existing.email = email
            
            existing.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return existing
    
    # Create new patient with auto-generated ID
    new_patient_id = generate_patient_id(db)
    
    new_patient = Patient(
        patient_id=new_patient_id,
        full_name=full_name,
        age=age,
        sex=sex,
        residence=residence,
        phone=phone,
        email=email,
        created_by=created_by,
        is_active=1
    )
    
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    
    return new_patient

