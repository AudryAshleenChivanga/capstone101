"""Appointment scheduling routes for clinician-gastroenterologist consultations."""
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.db import get_db
from app.models import User, Appointment, Case
from app.schemas import (
    AppointmentCreate, 
    AppointmentUpdate, 
    AppointmentResponse, 
    AppointmentOut,
    SpecialistListItem
)
from app.auth import get_current_user

router = APIRouter(prefix="/appointments", tags=["scheduling"])


@router.get("/specialists", response_model=List[SpecialistListItem])
def get_specialists(
    specialty: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of available specialists (gastroenterologists) for appointment booking.
    
    Clinicians can use this to see which specialists they can book appointments with.
    """
    query = db.query(User).filter(
        User.role == "specialist",
        User.is_active == 1
    )
    
    if specialty:
        query = query.filter(User.specialty.ilike(f"%{specialty}%"))
    
    specialists = query.all()
    
    result = []
    for specialist in specialists:
        result.append(SpecialistListItem(
            id=specialist.id,
            username=specialist.username,
            full_name=specialist.full_name,
            specialty=specialist.specialty,
            institution=specialist.institution,
            profile_photo=specialist.profile_photo
        ))
    
    return result


@router.post("/request", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
def create_appointment_request(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new appointment request with a gastroenterologist.
    
    The clinician requests an appointment, and the specialist must accept it
    before they can start a video consultation.
    """
    # Verify specialist exists and is active
    specialist = db.query(User).filter(
        User.id == appointment_data.specialist_id,
        User.role == "specialist",
        User.is_active == 1
    ).first()
    
    if not specialist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specialist not found or inactive"
        )
    
    # Verify case exists if provided
    if appointment_data.case_id:
        case = db.query(Case).filter(
            Case.id == appointment_data.case_id,
            Case.user_id == current_user.id
        ).first()
        
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found or you don't have permission"
            )
    
    # Validate requested date is in the future
    if appointment_data.requested_date < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requested date must be in the future"
        )
    
    # Create appointment
    new_appointment = Appointment(
        clinician_id=current_user.id,
        specialist_id=appointment_data.specialist_id,
        case_id=appointment_data.case_id,
        requested_date=appointment_data.requested_date,
        duration_minutes=appointment_data.duration_minutes,
        reason=appointment_data.reason,
        clinician_notes=appointment_data.clinician_notes,
        status="pending"
    )
    
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    
    # Add names for convenience
    appointment_out = AppointmentOut.from_orm(new_appointment)
    appointment_out.clinician_name = current_user.full_name or current_user.username
    appointment_out.specialist_name = specialist.full_name or specialist.username
    
    return appointment_out


@router.get("/my-requests", response_model=List[AppointmentOut])
def get_my_appointment_requests(
    status_filter: Optional[str] = Query(None, regex="^(pending|accepted|rejected|completed|cancelled)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all appointment requests created by the current clinician.
    """
    query = db.query(Appointment).filter(
        Appointment.clinician_id == current_user.id
    )
    
    if status_filter:
        query = query.filter(Appointment.status == status_filter)
    
    appointments = query.order_by(Appointment.created_at.desc()).all()
    
    result = []
    for appointment in appointments:
        specialist = db.query(User).filter(User.id == appointment.specialist_id).first()
        
        appointment_out = AppointmentOut.from_orm(appointment)
        appointment_out.clinician_name = current_user.full_name or current_user.username
        appointment_out.specialist_name = specialist.full_name if specialist else "Unknown"
        
        result.append(appointment_out)
    
    return result


@router.get("/pending-requests", response_model=List[AppointmentOut])
def get_pending_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all pending appointment requests for the current specialist.
    
    Only specialists can access this endpoint to see who wants to book with them.
    """
    if current_user.role != "specialist":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only specialists can view pending requests"
        )
    
    appointments = db.query(Appointment).filter(
        Appointment.specialist_id == current_user.id,
        Appointment.status == "pending"
    ).order_by(Appointment.created_at.desc()).all()
    
    result = []
    for appointment in appointments:
        clinician = db.query(User).filter(User.id == appointment.clinician_id).first()
        
        appointment_out = AppointmentOut.from_orm(appointment)
        appointment_out.clinician_name = clinician.full_name if clinician else "Unknown"
        appointment_out.specialist_name = current_user.full_name or current_user.username
        
        result.append(appointment_out)
    
    return result


@router.get("/my-appointments", response_model=List[AppointmentOut])
def get_my_appointments(
    status_filter: Optional[str] = Query(None, regex="^(pending|accepted|rejected|completed|cancelled)$"),
    upcoming_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all appointments for the current user (both as clinician and specialist).
    """
    # Get appointments where user is either clinician or specialist
    query = db.query(Appointment).filter(
        or_(
            Appointment.clinician_id == current_user.id,
            Appointment.specialist_id == current_user.id
        )
    )
    
    if status_filter:
        query = query.filter(Appointment.status == status_filter)
    
    if upcoming_only:
        query = query.filter(
            or_(
                Appointment.scheduled_date >= datetime.utcnow(),
                and_(
                    Appointment.scheduled_date.is_(None),
                    Appointment.requested_date >= datetime.utcnow()
                )
            )
        )
    
    appointments = query.order_by(Appointment.created_at.desc()).all()
    
    result = []
    for appointment in appointments:
        clinician = db.query(User).filter(User.id == appointment.clinician_id).first()
        specialist = db.query(User).filter(User.id == appointment.specialist_id).first()
        
        appointment_out = AppointmentOut.from_orm(appointment)
        appointment_out.clinician_name = clinician.full_name if clinician else "Unknown"
        appointment_out.specialist_name = specialist.full_name if specialist else "Unknown"
        
        result.append(appointment_out)
    
    return result


@router.get("/{appointment_id}", response_model=AppointmentOut)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get details of a specific appointment.
    
    User must be either the clinician or specialist for this appointment.
    """
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Verify user has access
    if appointment.clinician_id != current_user.id and appointment.specialist_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this appointment"
        )
    
    # Get names
    clinician = db.query(User).filter(User.id == appointment.clinician_id).first()
    specialist = db.query(User).filter(User.id == appointment.specialist_id).first()
    
    appointment_out = AppointmentOut.from_orm(appointment)
    appointment_out.clinician_name = clinician.full_name if clinician else "Unknown"
    appointment_out.specialist_name = specialist.full_name if specialist else "Unknown"
    
    return appointment_out


@router.put("/{appointment_id}/respond", response_model=AppointmentOut)
def respond_to_appointment(
    appointment_id: int,
    response: AppointmentResponse,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Specialist responds to an appointment request (accept or reject).
    
    Only the specialist assigned to this appointment can respond.
    """
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Verify user is the specialist for this appointment
    if appointment.specialist_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the assigned specialist can respond to this appointment"
        )
    
    # Check if appointment is still pending
    if appointment.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot respond to appointment with status '{appointment.status}'"
        )
    
    # Update appointment
    appointment.status = response.status
    appointment.specialist_notes = response.specialist_notes
    appointment.updated_at = datetime.utcnow()
    
    if response.status == "accepted":
        appointment.accepted_at = datetime.utcnow()
        # Use specialist's proposed time or keep requested time
        appointment.scheduled_date = response.scheduled_date or appointment.requested_date
    else:  # rejected
        appointment.rejected_at = datetime.utcnow()
    
    db.commit()
    db.refresh(appointment)
    
    # Get names
    clinician = db.query(User).filter(User.id == appointment.clinician_id).first()
    
    appointment_out = AppointmentOut.from_orm(appointment)
    appointment_out.clinician_name = clinician.full_name if clinician else "Unknown"
    appointment_out.specialist_name = current_user.full_name or current_user.username
    
    return appointment_out


@router.put("/{appointment_id}/update", response_model=AppointmentOut)
def update_appointment(
    appointment_id: int,
    update_data: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update appointment details (clinician can reschedule or add notes).
    
    Only the requesting clinician can update their appointment.
    """
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Verify user is the clinician for this appointment
    if appointment.clinician_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the requesting clinician can update this appointment"
        )
    
    # Update fields
    if update_data.requested_date:
        if update_data.requested_date < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requested date must be in the future"
            )
        appointment.requested_date = update_data.requested_date
        # Reset to pending if it was accepted
        if appointment.status == "accepted":
            appointment.status = "pending"
    
    if update_data.scheduled_date:
        appointment.scheduled_date = update_data.scheduled_date
    
    if update_data.duration_minutes:
        appointment.duration_minutes = update_data.duration_minutes
    
    if update_data.clinician_notes is not None:
        appointment.clinician_notes = update_data.clinician_notes
    
    appointment.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(appointment)
    
    # Get names
    specialist = db.query(User).filter(User.id == appointment.specialist_id).first()
    
    appointment_out = AppointmentOut.from_orm(appointment)
    appointment_out.clinician_name = current_user.full_name or current_user.username
    appointment_out.specialist_name = specialist.full_name if specialist else "Unknown"
    
    return appointment_out


@router.delete("/{appointment_id}")
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel an appointment.
    
    Both clinician and specialist can cancel their appointments.
    """
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Verify user has access
    if appointment.clinician_id != current_user.id and appointment.specialist_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to cancel this appointment"
        )
    
    # Check if can be cancelled
    if appointment.status in ["completed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel appointment with status '{appointment.status}'"
        )
    
    appointment.status = "cancelled"
    appointment.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "status": "success",
        "message": "Appointment cancelled successfully",
        "appointment_id": appointment_id
    }


@router.post("/{appointment_id}/complete")
def complete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark appointment as completed after video consultation.
    
    Either clinician or specialist can mark as completed.
    """
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Verify user has access
    if appointment.clinician_id != current_user.id and appointment.specialist_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to complete this appointment"
        )
    
    # Check if appointment was accepted
    if appointment.status != "accepted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only accepted appointments can be marked as completed"
        )
    
    appointment.status = "completed"
    appointment.completed_at = datetime.utcnow()
    appointment.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "status": "success",
        "message": "Appointment marked as completed",
        "appointment_id": appointment_id
    }

