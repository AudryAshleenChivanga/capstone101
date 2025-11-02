"""Admin panel routes for user and system management."""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db import get_db
from app.models import User, Case, TelemedSession, Appointment
from app.schemas import AdminUserCreate, AdminUserUpdate, UserOut
from app.auth import get_current_user, require_role

router = APIRouter(prefix="/admin", tags=["administration"])


@router.get("/stats")
def get_system_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Get system-wide statistics (admin only).
    
    Returns user counts, case counts, and performance metrics.
    """
    # User statistics
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == 1).count()
    
    # Case statistics
    total_cases = db.query(Case).count()
    
    # Cases this month
    from datetime import timedelta
    first_day_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    cases_this_month = db.query(Case).filter(
        Case.created_at >= first_day_of_month
    ).count()
    
    # High risk cases
    high_risk_cases = db.query(Case).filter(
        Case.screen_prob > 0.7
    ).count()
    
    # Video consultations
    total_sessions = db.query(TelemedSession).count()
    active_sessions = db.query(TelemedSession).filter(
        TelemedSession.status == "active"
    ).count()
    
    # Appointments
    total_appointments = db.query(Appointment).count()
    pending_appointments = db.query(Appointment).filter(
        Appointment.status == "pending"
    ).count()
    
    # Calculate average screening probability
    avg_screen_prob = db.query(func.avg(Case.screen_prob)).filter(
        Case.screen_prob.isnot(None)
    ).scalar() or 0
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": total_users - active_users,
        "total_cases": total_cases,
        "cases_this_month": cases_this_month,
        "high_risk_cases": high_risk_cases,
        "total_sessions": total_sessions,
        "active_sessions": active_sessions,
        "total_appointments": total_appointments,
        "pending_appointments": pending_appointments,
        "average_screening_probability": round(avg_screen_prob, 3),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/users", response_model=List[UserOut])
def list_all_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    List all users in the system (admin only).
    
    Supports filtering by role and active status.
    """
    query = db.query(User)
    
    # Apply filters
    if role:
        query = query.filter(User.role == role)
    
    if is_active is not None:
        query = query.filter(User.is_active == (1 if is_active else 0))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    users = query.order_by(User.created_at.desc()).offset(offset).limit(page_size).all()
    
    return users


@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: AdminUserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Create a new user (admin only).
    
    Can create clinicians, specialists, or other admins.
    """
    from app.auth import get_password_hash
    
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
        full_name=user_data.full_name,
        specialty=user_data.specialty or "Gastroenterology",
        institution=user_data.institution if hasattr(user_data, 'institution') else "Medical Center",
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.get("/users/{user_id}", response_model=UserOut)
def get_user_details(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Get detailed information about a specific user (admin only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    user_data: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Update user information (admin only).
    
    Can update role, active status, and other profile fields.
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    update_data = user_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Delete a user from the system (admin only).
    
    Cannot delete self or if user has associated cases.
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check for associated cases
    case_count = db.query(Case).filter(Case.user_id == user_id).count()
    
    if case_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete user with {case_count} associated cases. Deactivate instead."
        )
    
    db.delete(user)
    db.commit()
    
    return {
        "message": "User deleted successfully",
        "user_id": user_id
    }


@router.post("/users/{user_id}/activate")
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Activate a deactivated user (admin only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = 1
    user.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "User activated successfully",
        "user_id": user_id
    }


@router.post("/users/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Deactivate a user without deleting (admin only).
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = 0
    user.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "User deactivated successfully",
        "user_id": user_id
    }


@router.get("/cases/statistics")
def get_case_statistics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Get detailed case statistics (admin only).
    
    Optionally filter by date range.
    """
    query = db.query(Case)
    
    # Apply date filters if provided
    if start_date:
        query = query.filter(Case.created_at >= start_date)
    if end_date:
        query = query.filter(Case.created_at <= end_date)
    
    total_cases = query.count()
    
    # Get screening vs staging counts
    screening_cases = query.filter(
        Case.input_data['task'].astext == 'screening'
    ).count()
    
    staging_cases = query.filter(
        Case.input_data['task'].astext == 'staging'
    ).count()
    
    # Risk level distribution
    low_risk = query.filter(Case.screen_prob < 0.4).count()
    moderate_risk = query.filter(
        Case.screen_prob >= 0.4,
        Case.screen_prob < 0.7
    ).count()
    high_risk = query.filter(Case.screen_prob >= 0.7).count()
    
    # Signed documents
    signed_cases = query.filter(Case.signed_at.isnot(None)).count()
    sent_cases = query.filter(Case.sent_to_patient == 1).count()
    
    return {
        "total_cases": total_cases,
        "screening_cases": screening_cases,
        "staging_cases": staging_cases,
        "risk_distribution": {
            "low": low_risk,
            "moderate": moderate_risk,
            "high": high_risk
        },
        "document_workflow": {
            "signed_cases": signed_cases,
            "sent_to_patients": sent_cases
        },
        "date_range": {
            "start": start_date or "all time",
            "end": end_date or "present"
        }
    }


@router.get("/appointments/statistics")
def get_appointment_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Get appointment system statistics (admin only).
    """
    total = db.query(Appointment).count()
    pending = db.query(Appointment).filter(Appointment.status == "pending").count()
    accepted = db.query(Appointment).filter(Appointment.status == "accepted").count()
    rejected = db.query(Appointment).filter(Appointment.status == "rejected").count()
    completed = db.query(Appointment).filter(Appointment.status == "completed").count()
    cancelled = db.query(Appointment).filter(Appointment.status == "cancelled").count()
    
    return {
        "total_appointments": total,
        "pending": pending,
        "accepted": accepted,
        "rejected": rejected,
        "completed": completed,
        "cancelled": cancelled,
        "acceptance_rate": round((accepted / total * 100) if total > 0 else 0, 1),
        "completion_rate": round((completed / accepted * 100) if accepted > 0 else 0, 1)
    }


@router.get("/audit/recent-activity")
def get_recent_activity(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Get recent system activity for audit purposes (admin only).
    
    Returns recent cases, appointments, and sessions.
    """
    # Recent cases
    recent_cases = db.query(Case).order_by(Case.created_at.desc()).limit(limit).all()
    
    # Recent appointments
    recent_appointments = db.query(Appointment).order_by(
        Appointment.created_at.desc()
    ).limit(limit).all()
    
    # Recent video sessions
    recent_sessions = db.query(TelemedSession).order_by(
        TelemedSession.created_at.desc()
    ).limit(limit).all()
    
    return {
        "recent_cases": [
            {
                "id": case.id,
                "user_id": case.user_id,
                "task": case.input_data.get('task') if case.input_data else None,
                "screen_prob": case.screen_prob,
                "created_at": case.created_at.isoformat() if case.created_at else None
            }
            for case in recent_cases
        ],
        "recent_appointments": [
            {
                "id": apt.id,
                "clinician_id": apt.clinician_id,
                "specialist_id": apt.specialist_id,
                "status": apt.status,
                "created_at": apt.created_at.isoformat() if apt.created_at else None
            }
            for apt in recent_appointments
        ],
        "recent_sessions": [
            {
                "id": sess.id,
                "session_id": sess.session_id,
                "host_id": sess.host_id,
                "status": sess.status,
                "created_at": sess.created_at.isoformat() if sess.created_at else None
            }
            for sess in recent_sessions
        ]
    }
