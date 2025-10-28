"""Document management and signature workflow endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
import json
from datetime import datetime

from app.db import get_db
from app.auth import get_current_user
from app.models import User, Case
from app.schemas import DocumentSign, DocumentEdit
from app.utils.sms_sender import SMSSender
from app.utils.email_sender import EmailSender

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/{case_id}/prepare")
async def prepare_case_document(
    case_id: int,
    patient_name: str = Query(...),
    patient_email: str = Query(...),
    patient_phone: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Prepare a case for document editing and signing.
    Requires patient name and email. Phone is optional.
    """
    # Get the case
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # Check authorization
    if current_user.role != "admin" and case.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this case"
        )
    
    # Update case with patient info for document
    case.patient_name = patient_name
    case.patient_email = patient_email
    case.patient_phone = patient_phone
    
    # Generate editable recommendations if not already present
    if not case.edited_recommendations:
        case.edited_recommendations = case.recommendations
    
    db.commit()
    
    # Debug logging
    print(f"[PREPARE] Case #{case_id} updated:")
    print(f"  - Patient Name: {case.patient_name}")
    print(f"  - Patient Email: {case.patient_email}")
    print(f"  - Patient Phone: {case.patient_phone}")
    
    # Generate document content
    document_content = generate_document_content(case, current_user)
    
    return {
        "case_id": case.id,
        "content": document_content,
        "recommendations": case.edited_recommendations,
        "patient_name": case.patient_name,
        "patient_phone": case.patient_phone,
        "status": "ready_for_edit",
        "message": "Document prepared for editing"
    }


@router.put("/{case_id}/edit")
async def edit_case_recommendations(
    case_id: int,
    recommendations: List[str] = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Edit case recommendations before signing.
    Expects JSON: {"recommendations": ["rec1", "rec2", ...]}
    """
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # Check authorization
    if current_user.role != "admin" and case.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to edit this case"
        )
    
    # Can only edit unsigned cases
    if case.signed_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot edit signed cases"
        )
    
    # Update recommendations
    case.edited_recommendations = recommendations
    
    db.commit()
    
    # Generate updated document content
    document_content = generate_document_content(case, current_user)
    
    return {
        "message": "Recommendations updated successfully",
        "content": document_content,
        "recommendations": case.edited_recommendations
    }


@router.post("/{case_id}/sign")
async def sign_case_document(
    case_id: int,
    signature_data: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Sign the case document with digital signature.
    Expects JSON: {"signature_data": "data:image/png;base64,..."}
    """
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # Check authorization
    if current_user.role != "admin" and case.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to sign this case"
        )
    
    # Update case with signature
    case.signature_data = signature_data
    case.signed_by = current_user.id
    case.signed_at = datetime.utcnow()
    case.is_approved = 1
    
    db.commit()
    
    return {
        "message": "Case document signed successfully",
        "case_id": case_id,
        "signed_at": case.signed_at,
        "signed_by": current_user.full_name or current_user.username
    }


@router.post("/{case_id}/send-notification")
async def send_case_notification(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send case recommendations to patient via EMAIL and SMS.
    Email is primary (always works), SMS is backup (may fail for international numbers).
    """
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # Check authorization
    if current_user.role != "admin" and case.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to send SMS for this case"
        )
    
    # Must be signed before sending
    if not case.signed_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Case must be signed before sending SMS"
        )
    
    # Debug logging
    print(f"[SEND-NOTIFICATION] Case #{case_id} patient info:")
    print(f"  - Patient Name: {case.patient_name}")
    print(f"  - Patient Email: {case.patient_email}")
    print(f"  - Patient Phone: {case.patient_phone}")
    
    # Verify patient info (email OR phone required)
    if not case.patient_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient name is required. Please go back to Step 1 and enter patient information."
        )
    
    if not case.patient_email and not case.patient_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient email or phone number is required. Please go back to Step 1 and enter patient email address."
        )
    
    # Get recommendations to send
    recommendations = case.edited_recommendations or case.recommendations
    if not recommendations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No recommendations available to send"
        )
    
    # Clean recommendations - remove emojis and non-ASCII characters for SMS
    def clean_for_sms(text):
        """Remove emojis and non-ASCII characters that can't be sent via SMS."""
        if not isinstance(text, str):
            text = str(text)
        # Remove common emoji patterns
        import re
        # Remove emojis
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            u"\U0001F7E0-\U0001F7EB"  # colored circles
            "]+", flags=re.UNICODE)
        text = emoji_pattern.sub('', text)
        # Keep only ASCII printable characters
        text = ''.join(char for char in text if ord(char) < 128 or char == '\n')
        # Clean up extra whitespace
        text = ' '.join(text.split())
        return text.strip()
    
    # Get clinician name
    clinician_name = current_user.full_name or current_user.username
    
    # Track delivery results
    email_result = None
    sms_result = None
    
    # Send Email (PRIMARY METHOD)
    if case.patient_email:
        email_sender = EmailSender()
        email_result = email_sender.send_recommendations_email(
            to_email=case.patient_email,
            patient_name=case.patient_name,
            clinician_name=clinician_name,
            recommendations=recommendations,
            case_id=case_id
        )
    
    # Send SMS (BACKUP METHOD)
    if case.patient_phone:
        # Clean recommendations for SMS (remove emojis)
        cleaned_recs = [clean_for_sms(rec) for rec in recommendations]
        recs_text = "\\n\\n".join(f"{i+1}. {rec}" for i, rec in enumerate(cleaned_recs))
        message = f"""Hello {case.patient_name},

Your H. pylori results from {clinician_name}:

{recs_text}

Check your email for full details.

Best regards,
H. pylori CDSS Team"""
        
        sms_sender = SMSSender()
        sms_result = sms_sender.send_sms(
            to_number=case.patient_phone,
            message=message
        )
    
    # Update case
    case.sms_sent = True
    case.sms_sent_at = datetime.utcnow()
    db.commit()
    
    # Determine overall status
    email_success = email_result and email_result.get("status") == "success"
    sms_success = sms_result and (sms_result.get("status") == "success" or sms_result.get("simulated") == True)
    
    # Build response
    response = {
        "message": "Notification sent",
        "patient_name": case.patient_name,
        "sent_at": case.sms_sent_at,
        "delivery": {
            "email": {
                "attempted": case.patient_email is not None,
                "success": email_success,
                "to": case.patient_email,
                "error": email_result.get("error_message") if email_result and not email_success else None
            },
            "sms": {
                "attempted": case.patient_phone is not None,
                "success": sms_success,
                "to": case.patient_phone,
                "simulated": sms_result.get("simulated", False) if sms_result else False,
                "error": sms_result.get("error_message") if sms_result and not sms_success else None
            }
        }
    }
    
    # If both failed, return error
    if not email_success and not sms_success and not sms_result.get("simulated"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send notifications. Email: {email_result.get('error_message') if email_result else 'Not attempted'}. SMS: {sms_result.get('error_message') if sms_result else 'Not attempted'}"
        )
    
    return response


# Helper function
def generate_document_content(case: Case, user: User) -> str:
    """Generate formatted document content for a case."""
    recommendations = case.edited_recommendations or case.recommendations
    recs_formatted = "\\n".join(f"  • {rec}" for rec in recommendations)
    
    return f"""
H. PYLORI CLINICAL DECISION SUPPORT SYSTEM
CASE REPORT

Case ID: {case.id}
Date: {case.created_at.strftime('%Y-%m-%d %H:%M')}
Clinician: {user.full_name or user.username}

PATIENT INFORMATION:
Name: {case.patient_name or 'N/A'}
Phone: {case.patient_phone or 'N/A'}
ID: {case.patient_pseudo_id or 'N/A'}

ASSESSMENT TASK:
{case.input_data.get('task', 'N/A') if case.input_data else 'N/A'}

RECOMMENDATIONS:
{recs_formatted}

SIGNATURE:
{'[Signed]' if case.signed_at else '[Unsigned]'}
{f'Signed by: {user.full_name or user.username}' if case.signed_at else ''}
{f'Signed at: {case.signed_at.strftime("%Y-%m-%d %H:%M")}' if case.signed_at else ''}

---
Generated by H. pylori CDSS v1.0
"""
