"""SMS notification routes (stub implementation)."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User
from app.schemas import SMSRequest, SMSResponse
from app.auth import get_current_user
import re

router = APIRouter(prefix="/notify", tags=["notifications"])


def sanitize_phone_for_logging(phone: str) -> str:
    """Redact phone number for logging (show only last 4 digits)."""
    if len(phone) > 4:
        return "*" * (len(phone) - 4) + phone[-4:]
    return "****"


@router.post("/patient", status_code=status.HTTP_202_ACCEPTED)
def send_patient_notification(
    notification: SMSRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send SMS notification to patient (stub provider).
    
    This is a simulated endpoint that logs the message without actually sending it.
    In production, integrate with Twilio, AWS SNS, or similar SMS gateway.
    """
    # Sanitize phone number for logging
    sanitized_phone = sanitize_phone_for_logging(notification.phone_number)
    
    # Redact any raw probabilities from message (privacy/regulatory compliance)
    message_to_send = notification.message
    
    # Log the simulated SMS (in production, replace with actual SMS provider)
    print(f"[SMS STUB] To: {sanitized_phone}")
    print(f"[SMS STUB] Message: {message_to_send}")
    print(f"[SMS STUB] Sent by user: {current_user.username}")
    if notification.case_id:
        print(f"[SMS STUB] Related case ID: {notification.case_id}")
    
    # Simulate success response
    return {
        "status": "accepted",
        "message": "Notification queued for delivery",
        "recipient": sanitized_phone,
        "provider": "stub",
        "note": "This is a simulated SMS endpoint. No actual message was sent."
    }
