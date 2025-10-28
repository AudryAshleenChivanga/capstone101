"""Patient management routes."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.db import get_db
from app.models import User, Patient, Case
from app.auth import get_current_user
from app.utils.patient_utils import generate_patient_id, search_patients, get_or_create_patient
from pydantic import BaseModel


# Schemas
class PatientCreate(BaseModel):
    """Schema for creating a new patient."""
    full_name: str
    age: Optional[int] = None
    sex: Optional[str] = None
    residence: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    notes: Optional[str] = None


class PatientUpdate(BaseModel):
    """Schema for updating patient information."""
    full_name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    residence: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[int] = None


class PatientOut(BaseModel):
    """Schema for patient output."""
    id: int
    patient_id: str
    full_name: Optional[str]
    age: Optional[int]
    sex: Optional[str]
    residence: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    blood_type: Optional[str]
    created_at: datetime
    updated_at: datetime
    total_cases: Optional[int] = 0
    last_visit: Optional[datetime] = None
    
    class Config:
        from_attributes = True


router = APIRouter(prefix="/api/patients", tags=["patients"])


@router.post("/", response_model=PatientOut)
def create_patient(
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new patient with auto-generated Patient ID.
    """
    try:
        # Generate unique patient ID
        patient_id = generate_patient_id(db)
        
        # Create patient
        new_patient = Patient(
            patient_id=patient_id,
            full_name=patient_data.full_name,
            age=patient_data.age,
            sex=patient_data.sex,
            residence=patient_data.residence,
            phone=patient_data.phone,
            email=patient_data.email,
            blood_type=patient_data.blood_type,
            allergies=patient_data.allergies,
            notes=patient_data.notes,
            created_by=current_user.id,
            is_active=1
        )
        
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
        
        # Get case count
        case_count = db.query(Case).filter(Case.patient_db_id == new_patient.id).count()
        
        # Build response
        patient_out = PatientOut(
            id=new_patient.id,
            patient_id=new_patient.patient_id,
            full_name=new_patient.full_name,
            age=new_patient.age,
            sex=new_patient.sex,
            residence=new_patient.residence,
            phone=new_patient.phone,
            email=new_patient.email,
            blood_type=new_patient.blood_type,
            created_at=new_patient.created_at,
            updated_at=new_patient.updated_at,
            total_cases=case_count,
            last_visit=None
        )
        
        return patient_out
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating patient: {str(e)}"
        )


@router.get("/search")
def search_patient(
    patient_id: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    phone: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search for patients by ID, name, or phone.
    """
    patients = search_patients(
        db=db,
        patient_id=patient_id,
        name=name,
        phone=phone
    )
    
    results = []
    for patient in patients:
        # Get case statistics
        case_count = db.query(Case).filter(Case.patient_db_id == patient.id).count()
        last_case = (
            db.query(Case)
            .filter(Case.patient_db_id == patient.id)
            .order_by(Case.created_at.desc())
            .first()
        )
        
        results.append({
            "id": patient.id,
            "patient_id": patient.patient_id,
            "full_name": patient.full_name,
            "age": patient.age,
            "sex": patient.sex,
            "residence": patient.residence,
            "phone": patient.phone,
            "email": patient.email,
            "total_cases": case_count,
            "last_visit": last_case.created_at if last_case else None,
            "created_at": patient.created_at
        })
    
    return {
        "total": len(results),
        "patients": results
    }


@router.get("/{patient_id}")
def get_patient_detail(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed patient information including case history.
    """
    patient = db.query(Patient).filter(
        Patient.patient_id == patient_id,
        Patient.is_active == 1
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Get all cases for this patient
    cases = (
        db.query(Case)
        .filter(Case.patient_db_id == patient.id)
        .order_by(Case.created_at.desc())
        .all()
    )
    
    case_history = []
    for case in cases:
        case_history.append({
            "id": case.id,
            "case_type": case.case_type or case.input_data.get('task', 'screening'),
            "screen_prob": case.screen_prob,
            "stage_pred": case.stage_pred,
            "created_at": case.created_at.isoformat(),
            "clinician_id": case.user_id
        })
    
    return {
        "id": patient.id,
        "patient_id": patient.patient_id,
        "full_name": patient.full_name,
        "age": patient.age,
        "sex": patient.sex,
        "residence": patient.residence,
        "phone": patient.phone,
        "email": patient.email,
        "blood_type": patient.blood_type,
        "allergies": patient.allergies,
        "notes": patient.notes,
        "created_at": patient.created_at.isoformat(),
        "updated_at": patient.updated_at.isoformat(),
        "total_cases": len(cases),
        "case_history": case_history
    }


@router.put("/{patient_id}")
def update_patient(
    patient_id: str,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update patient information.
    """
    patient = db.query(Patient).filter(
        Patient.patient_id == patient_id,
        Patient.is_active == 1
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Update fields if provided
    update_data = patient_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)
    
    patient.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(patient)
    
    return {
        "message": "Patient updated successfully",
        "patient_id": patient.patient_id
    }


@router.delete("/{patient_id}")
def delete_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Soft delete a patient (admin only).
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete patients"
        )
    
    patient = db.query(Patient).filter(
        Patient.patient_id == patient_id
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Soft delete
    patient.is_active = 0
    patient.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "Patient deleted successfully",
        "patient_id": patient_id
    }


@router.get("/")
def list_patients(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all patients with pagination and search.
    """
    query = db.query(Patient).filter(Patient.is_active == 1)
    
    # Search filter
    if search:
        query = query.filter(
            (Patient.patient_id.ilike(f"%{search}%")) |
            (Patient.full_name.ilike(f"%{search}%")) |
            (Patient.phone.ilike(f"%{search}%"))
        )
    
    # Get total count
    total = query.count()
    
    # Pagination
    offset = (page - 1) * page_size
    patients = query.order_by(Patient.created_at.desc()).offset(offset).limit(page_size).all()
    
    # Build response
    results = []
    for patient in patients:
        case_count = db.query(Case).filter(Case.patient_db_id == patient.id).count()
        last_case = (
            db.query(Case)
            .filter(Case.patient_db_id == patient.id)
            .order_by(Case.created_at.desc())
            .first()
        )
        
        results.append({
            "id": patient.id,
            "patient_id": patient.patient_id,
            "full_name": patient.full_name,
            "age": patient.age,
            "sex": patient.sex,
            "phone": patient.phone,
            "total_cases": case_count,
            "last_visit": last_case.created_at.isoformat() if last_case else None,
            "created_at": patient.created_at.isoformat()
        })
    
    return {
        "patients": results,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }

