"""
Prescription Management Routes for H. pylori CDSS
Handles creation, viewing, updating, and tracking of prescriptions
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Dict

from app.db import get_db
from app.models import Prescription, Patient, Case, User
from app.routes_auth import get_current_user

router = APIRouter(prefix="/prescriptions", tags=["prescriptions"])


# Pydantic models for request/response
class MedicationItem(BaseModel):
    name: str
    dosage: str
    frequency: str
    duration: str
    

class PrescriptionCreate(BaseModel):
    patient_id: str  # HP-2025-XXXX format
    case_id: int
    diagnosis: str
    medications: List[Dict] = Field(..., description="List of medication dictionaries")
    recommendations: Optional[str] = None
    lifestyle_advice: Optional[str] = None
    follow_up_days: Optional[int] = None
    stage: Optional[str] = None
    protocol_type: Optional[str] = None
    lab_tests_ordered: Optional[List[str]] = None
    notes: Optional[str] = None


class PrescriptionUpdate(BaseModel):
    medications: Optional[List[Dict]] = None
    diagnosis: Optional[str] = None
    recommendations: Optional[str] = None
    lifestyle_advice: Optional[str] = None
    follow_up_days: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class PrescriptionResponse(BaseModel):
    id: int
    patient_id: str
    patient_name: str
    case_id: int
    prescribed_by: str
    prescriber_id: int
    diagnosis: str
    medications: List[Dict]
    recommendations: Optional[str]
    lifestyle_advice: Optional[str]
    follow_up_days: Optional[int]
    stage: Optional[str]
    protocol_type: Optional[str]
    lab_tests_ordered: Optional[List]
    status: str
    created_at: str
    updated_at: str
    dispensed_at: Optional[str]
    completed_at: Optional[str]
    notes: Optional[str]


@router.post("/", response_model=Dict)
def create_prescription(
    prescription_data: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new prescription for a patient.
    
    - **patient_id**: Patient ID (HP-2025-XXXX)
    - **case_id**: Associated case ID
    - **diagnosis**: Clinical diagnosis
    - **medications**: List of medications with dosage, frequency, duration
    - **recommendations**: Clinical recommendations
    - **lifestyle_advice**: Lifestyle modification advice
    - **follow_up_days**: Days until follow-up appointment
    - **stage**: Treatment stage (stage1_symptom, stage2_lab, stage3_ric)
    - **protocol_type**: eradication, maintenance, palliative
    - **lab_tests_ordered**: List of lab tests to be performed
    """
    # Get patient
    patient = db.query(Patient).filter(Patient.patient_id == prescription_data.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get case
    case = db.query(Case).filter(Case.id == prescription_data.case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Check authorization (only prescriber or admin)
    if current_user.role not in ["admin", "clinician", "specialist"]:
        raise HTTPException(status_code=403, detail="Not authorized to create prescriptions")
    
    # Create prescription
    new_prescription = Prescription(
        patient_id=patient.id,
        case_id=case.id,
        prescribed_by=current_user.id,
        diagnosis=prescription_data.diagnosis,
        medications=prescription_data.medications,
        recommendations=prescription_data.recommendations,
        lifestyle_advice=prescription_data.lifestyle_advice,
        follow_up_days=prescription_data.follow_up_days,
        stage=prescription_data.stage,
        protocol_type=prescription_data.protocol_type,
        lab_tests_ordered=prescription_data.lab_tests_ordered,
        notes=prescription_data.notes
    )
    
    db.add(new_prescription)
    db.commit()
    db.refresh(new_prescription)
    
    return {
        "success": True,
        "message": "Prescription created successfully",
        "prescription_id": new_prescription.id,
        "patient_id": patient.patient_id,
        "status": new_prescription.status
    }


@router.get("/{prescription_id}", response_model=PrescriptionResponse)
def get_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific prescription by ID."""
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    # Check authorization
    patient = db.query(Patient).filter(Patient.id == prescription.patient_id).first()
    if current_user.role not in ["admin"] and prescription.prescribed_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this prescription")
    
    # Get prescriber details
    prescriber = db.query(User).filter(User.id == prescription.prescribed_by).first()
    
    return PrescriptionResponse(
        id=prescription.id,
        patient_id=patient.patient_id,
        patient_name=patient.full_name or "Unknown",
        case_id=prescription.case_id,
        prescribed_by=prescriber.full_name if prescriber else "Unknown",
        prescriber_id=prescriber.id if prescriber else 0,
        diagnosis=prescription.diagnosis,
        medications=prescription.medications or [],
        recommendations=prescription.recommendations,
        lifestyle_advice=prescription.lifestyle_advice,
        follow_up_days=prescription.follow_up_days,
        stage=prescription.stage,
        protocol_type=prescription.protocol_type,
        lab_tests_ordered=prescription.lab_tests_ordered,
        status=prescription.status,
        created_at=prescription.created_at.isoformat() if prescription.created_at else None,
        updated_at=prescription.updated_at.isoformat() if prescription.updated_at else None,
        dispensed_at=prescription.dispensed_at.isoformat() if prescription.dispensed_at else None,
        completed_at=prescription.completed_at.isoformat() if prescription.completed_at else None,
        notes=prescription.notes
    )


@router.get("/patient/{patient_id}")
def get_patient_prescriptions(
    patient_id: str,
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all prescriptions for a specific patient."""
    # Get patient
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Build query
    query = db.query(Prescription).filter(Prescription.patient_id == patient.id)
    
    if status:
        query = query.filter(Prescription.status == status)
    
    prescriptions = query.order_by(Prescription.created_at.desc()).all()
    
    # Format response
    results = []
    for rx in prescriptions:
        prescriber = db.query(User).filter(User.id == rx.prescribed_by).first()
        results.append({
            "id": rx.id,
            "case_id": rx.case_id,
            "prescribed_by": prescriber.full_name if prescriber else "Unknown",
            "diagnosis": rx.diagnosis,
            "medications_count": len(rx.medications) if rx.medications else 0,
            "status": rx.status,
            "protocol_type": rx.protocol_type,
            "stage": rx.stage,
            "created_at": rx.created_at.isoformat() if rx.created_at else None,
            "follow_up_days": rx.follow_up_days
        })
    
    return {
        "patient_id": patient_id,
        "patient_name": patient.full_name,
        "prescriptions": results,
        "total": len(results)
    }


@router.put("/{prescription_id}")
def update_prescription(
    prescription_id: int,
    update_data: PrescriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing prescription."""
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    # Check authorization (only prescriber or admin)
    if current_user.role != "admin" and prescription.prescribed_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this prescription")
    
    # Update fields
    if update_data.medications is not None:
        prescription.medications = update_data.medications
    if update_data.diagnosis is not None:
        prescription.diagnosis = update_data.diagnosis
    if update_data.recommendations is not None:
        prescription.recommendations = update_data.recommendations
    if update_data.lifestyle_advice is not None:
        prescription.lifestyle_advice = update_data.lifestyle_advice
    if update_data.follow_up_days is not None:
        prescription.follow_up_days = update_data.follow_up_days
    if update_data.status is not None:
        prescription.status = update_data.status
        if update_data.status == "dispensed" and not prescription.dispensed_at:
            prescription.dispensed_at = datetime.utcnow()
        elif update_data.status == "completed" and not prescription.completed_at:
            prescription.completed_at = datetime.utcnow()
    if update_data.notes is not None:
        prescription.notes = update_data.notes
    
    prescription.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "success": True,
        "message": "Prescription updated successfully",
        "prescription_id": prescription.id
    }


@router.delete("/{prescription_id}")
def delete_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a prescription (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only administrators can delete prescriptions")
    
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    db.delete(prescription)
    db.commit()
    
    return {
        "success": True,
        "message": "Prescription deleted successfully"
    }


@router.get("/case/{case_id}")
def get_case_prescription(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get prescription associated with a specific case."""
    prescription = db.query(Prescription).filter(Prescription.case_id == case_id).first()
    
    if not prescription:
        return {
            "has_prescription": False,
            "message": "No prescription found for this case"
        }
    
    patient = db.query(Patient).filter(Patient.id == prescription.patient_id).first()
    prescriber = db.query(User).filter(User.id == prescription.prescribed_by).first()
    
    return {
        "has_prescription": True,
        "prescription": {
            "id": prescription.id,
            "patient_id": patient.patient_id if patient else None,
            "patient_name": patient.full_name if patient else "Unknown",
            "prescribed_by": prescriber.full_name if prescriber else "Unknown",
            "diagnosis": prescription.diagnosis,
            "medications": prescription.medications,
            "recommendations": prescription.recommendations,
            "lifestyle_advice": prescription.lifestyle_advice,
            "status": prescription.status,
            "created_at": prescription.created_at.isoformat() if prescription.created_at else None
        }
    }


@router.post("/{prescription_id}/print")
def generate_prescription_pdf(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a printable PDF version of the prescription."""
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    # TODO: Implement PDF generation
    # For now, return prescription data formatted for printing
    
    patient = db.query(Patient).filter(Patient.id == prescription.patient_id).first()
    prescriber = db.query(User).filter(User.id == prescription.prescribed_by).first()
    
    return {
        "success": True,
        "message": "Prescription ready for printing",
        "print_data": {
            "prescription_id": prescription.id,
            "date": prescription.created_at.strftime("%Y-%m-%d") if prescription.created_at else "",
            "patient": {
                "id": patient.patient_id if patient else "",
                "name": patient.full_name if patient else "",
                "age": patient.age if patient else "",
                "sex": patient.sex if patient else ""
            },
            "prescriber": {
                "name": prescriber.full_name if prescriber else "",
                "license": prescriber.license_number if prescriber else "",
                "institution": prescriber.institution if prescriber else ""
            },
            "diagnosis": prescription.diagnosis,
            "medications": prescription.medications,
            "recommendations": prescription.recommendations,
            "lifestyle_advice": prescription.lifestyle_advice,
            "follow_up": f"Follow-up in {prescription.follow_up_days} days" if prescription.follow_up_days else "As needed"
        }
    }

