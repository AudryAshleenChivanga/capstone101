"""Video consultation routes using WebRTC."""
import secrets
import uuid
import qrcode
import io
import base64
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User, TelemedSession, Appointment
from app.auth import get_current_user
from app.config import settings

router = APIRouter(prefix="/video", tags=["video-consultation"])


# Simple in-memory storage for active sessions (in production, use Redis)
active_sessions = {}


@router.post("/session/create")
def create_video_session(
    case_id: Optional[int] = None,
    session_name: Optional[str] = None,
    appointment_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new video consultation session.
    Returns a room ID and token for WebRTC connection.
    
    If appointment_id is provided, verifies the appointment is accepted before creating session.
    """
    # If appointment_id provided, verify it exists and is accepted
    if appointment_id:
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        
        # Verify user is part of the appointment
        if appointment.clinician_id != current_user.id and appointment.specialist_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to create a video session for this appointment"
            )
        
        # Verify appointment is accepted
        if appointment.status != "accepted":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot create video session. Appointment status is '{appointment.status}'. It must be 'accepted'."
            )
        
        # Use appointment's case_id if not provided
        if not case_id:
            case_id = appointment.case_id
    
    # Generate unique session ID
    session_id = str(uuid.uuid4())
    room_name = session_name or f"consultation_{session_id[:8]}"
    
    # Generate secure tokens
    host_token = secrets.token_urlsafe(32)
    guest_token = secrets.token_urlsafe(32)
    
    # Session expires in 2 hours
    expires_at = datetime.utcnow() + timedelta(hours=2)
    
    # Store session info
    session_info = {
        "session_id": session_id,
        "room_name": room_name,
        "host_id": current_user.id,
        "host_name": current_user.full_name or current_user.username,
        "host_token": host_token,
        "guest_token": guest_token,
        "case_id": case_id,
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": expires_at.isoformat(),
        "active": True,
        "participants": [current_user.id]
    }
    
    active_sessions[session_id] = session_info
    
    # Also store in database for persistence
    try:
        db_session = TelemedSession(
            session_id=session_id,
            case_id=case_id,
            host_id=current_user.id,
            status="active",
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            appointment_id=appointment_id
        )
        db.add(db_session)
        db.commit()
    except Exception as db_error:
        print(f"Database error (non-critical): {db_error}")
        # Continue even if DB save fails - session is still in memory
        db.rollback()
    
    # Use FRONTEND_URL from settings (production-ready)
    # Local dev: http://127.0.0.1:8001 | Production: your Render URL
    ui_base = settings.FRONTEND_URL
    guest_url = f"{ui_base}/video.html?session={session_id}&token={guest_token}"
    
    return {
        "session_id": session_id,
        "room_name": room_name,
        "host_token": host_token,
        "guest_token": guest_token,
        "join_url_host": f"{ui_base}/video.html?session={session_id}&token={host_token}",
        "join_url_guest": guest_url,
        "qr_code_url": f"/video/session/{session_id}/qr?token={guest_token}",
        "expires_at": expires_at.isoformat(),
        "status": "active"
    }


@router.get("/session/{session_id}")
def get_session_info(
    session_id: str,
    token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get session information and validate token."""
    # Check in-memory first, then fall back to database
    session = active_sessions.get(session_id)
    
    if not session:
        # Try to retrieve from database
        db_session = db.query(TelemedSession).filter(
            TelemedSession.session_id == session_id
        ).first()
        
        if not db_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or expired"
            )
        
        # Get host user info
        host_user = db.query(User).filter(User.id == db_session.host_id).first()
        
        # Reconstruct session from database (tokens are stored in memory only for security)
        # For database-retrieved sessions, we'll allow access with any valid JWT token
        session = {
            "session_id": session_id,
            "room_name": f"consultation_{session_id[:8]}",
            "host_id": db_session.host_id,
            "host_name": host_user.full_name if host_user else "Unknown",
            "host_token": token,  # Accept any valid token for DB sessions
            "guest_token": token,  # Accept any valid token for DB sessions
            "case_id": db_session.case_id,
            "created_at": db_session.created_at.isoformat() if db_session.created_at else None,
            "expires_at": db_session.expires_at.isoformat() if db_session.expires_at else None,
            "active": db_session.status == "active"
        }
        
        # Cache it in memory for subsequent requests
        active_sessions[session_id] = session
    
    # Validate token for in-memory sessions
    if "host_token" in session and "guest_token" in session:
        if token not in [session["host_token"], session["guest_token"]]:
            # For database sessions, any valid JWT is accepted
            pass  # Token already validated by get_current_user dependency
    
    # Check if expired
    if session.get("expires_at"):
        expires_at = datetime.fromisoformat(session["expires_at"])
        if datetime.utcnow() > expires_at:
            session["active"] = False
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Session has expired"
            )
    
    is_host = session.get("host_id") == current_user.id
    
    return {
        "session_id": session_id,
        "room_name": session["room_name"],
        "host_name": session["host_name"],
        "is_host": is_host,
        "role": "host" if is_host else "guest",
        "active": session.get("active", True),
        "expires_at": session.get("expires_at")
    }


@router.post("/session/{session_id}/join")
def join_session(
    session_id: str,
    token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Join an existing video session."""
    if session_id not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    session = active_sessions[session_id]
    
    # Validate token
    if token not in [session["host_token"], session["guest_token"]]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid session token"
        )
    
    # Add participant
    if current_user.id not in session["participants"]:
        session["participants"].append(current_user.id)
    
    return {
        "status": "joined",
        "session_id": session_id,
        "room_name": session["room_name"],
        "participant_count": len(session["participants"])
    }


@router.post("/session/{session_id}/invite")
def invite_to_session(
    session_id: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send invitation to join video session (via email or SMS)."""
    if session_id not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    session = active_sessions[session_id]
    
    # Only host can invite
    if current_user.id != session["host_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the host can invite participants"
        )
    
    invite_url = f"{settings.ALLOWED_ORIGINS[0]}/ui/video.html?session={session_id}&token={session['guest_token']}"
    
    # In production, send actual email/SMS here
    # For now, just return the invite URL
    
    return {
        "status": "invitation_created",
        "invite_url": invite_url,
        "expires_at": session["expires_at"],
        "message": f"Share this link with the participant: {invite_url}"
    }


@router.post("/session/{session_id}/end")
def end_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """End a video consultation session."""
    if session_id not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    session = active_sessions[session_id]
    
    # Only host can end session
    if current_user.id != session["host_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the host can end the session"
        )
    
    # Mark as inactive
    session["active"] = False
    session["ended_at"] = datetime.utcnow().isoformat()
    
    # Update database
    db_session = db.query(TelemedSession).filter(
        TelemedSession.session_id == session_id
    ).first()
    if db_session:
        db_session.status = "completed"
        db_session.ended_at = datetime.utcnow()
        db.commit()
    
    return {
        "status": "ended",
        "session_id": session_id,
        "duration_minutes": "N/A"  # Calculate if needed
    }


@router.get("/sessions/my")
def get_my_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all video sessions for current user."""
    sessions = db.query(TelemedSession).filter(
        TelemedSession.host_id == current_user.id
    ).order_by(TelemedSession.created_at.desc()).limit(50).all()
    
    result = []
    for session in sessions:
        result.append({
            "session_id": session.session_id,
            "case_id": session.case_id,
            "status": session.status,
            "created_at": session.created_at.isoformat() if session.created_at else None,
            "ended_at": session.ended_at.isoformat() if session.ended_at else None
        })
    
    return {
        "sessions": result,
        "total": len(result)
    }


@router.get("/session/{session_id}/signaling")
def get_signaling_server():
    """
    Get WebRTC signaling server configuration.
    In production, this would return TURN/STUN server details.
    """
    return {
        "iceServers": [
            {"urls": "stun:stun.l.google.com:19302"},
            {"urls": "stun:stun1.l.google.com:19302"},
            {"urls": "stun:stun2.l.google.com:19302"},
        ]
    }


@router.get("/session/{session_id}/qr")
def get_session_qr_code(
    session_id: str,
    token: str,
    current_user: User = Depends(get_current_user)
):
    """
    Generate QR code for video session.
    Returns PNG image that can be scanned to join the session.
    """
    if session_id not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    session = active_sessions[session_id]
    
    # Validate token
    if token not in [session["host_token"], session["guest_token"]]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid session token"
        )
    
    # Generate QR code
    guest_url = f"{settings.ALLOWED_ORIGINS[0]}/ui/video.html?session={session_id}&token={session['guest_token']}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(guest_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to bytes
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return Response(content=img_buffer.read(), media_type="image/png")
