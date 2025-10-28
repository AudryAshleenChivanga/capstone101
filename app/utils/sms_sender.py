"""Real SMS sending using Twilio."""
from typing import Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from app.config import settings


class SMSSender:
    """Handler for sending SMS messages via Twilio."""
    
    def __init__(self):
        """Initialize Twilio client."""
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.phone_number = settings.TWILIO_PHONE_NUMBER
        
        # Check if Twilio is configured
        self.is_configured = all([self.account_sid, self.auth_token, self.phone_number])
        
        if self.is_configured:
            try:
                self.client = Client(self.account_sid, self.auth_token)
            except Exception as e:
                print(f"Warning: Twilio client initialization failed: {e}")
                self.is_configured = False
                self.client = None
        else:
            self.client = None
    
    def send_sms(
        self,
        to_number: str,
        message: str,
        pdf_url: Optional[str] = None
    ) -> dict:
        """
        Send an SMS message.
        
        Args:
            to_number: Recipient phone number (E.164 format recommended)
            message: Message text
            pdf_url: Optional URL to PDF report
            
        Returns:
            Dictionary with status and message SID or error
        """
        if not self.is_configured:
            return {
                "status": "error",
                "message": "Twilio not configured. Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER in .env",
                "simulated": True
            }
        
        try:
            # Format phone number
            if not to_number.startswith('+'):
                # Assume US number if no country code
                to_number = f'+1{to_number.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")}'
            
            # Append PDF link if provided
            full_message = message
            if pdf_url:
                full_message += f"\n\nView your report: {pdf_url}"
            
            # Send SMS
            message_obj = self.client.messages.create(
                body=full_message,
                from_=self.phone_number,
                to=to_number
            )
            
            return {
                "status": "success",
                "message_sid": message_obj.sid,
                "to": to_number,
                "sent_at": message_obj.date_created.isoformat() if message_obj.date_created else None
            }
            
        except TwilioRestException as e:
            return {
                "status": "error",
                "error_code": e.code,
                "error_message": e.msg,
                "to": to_number
            }
        except Exception as e:
            return {
                "status": "error",
                "error_message": str(e),
                "to": to_number
            }
    
    def send_recommendation_sms(
        self,
        to_number: str,
        patient_name: str,
        clinician_name: str,
        pdf_url: Optional[str] = None
    ) -> dict:
        """
        Send a patient-friendly SMS about their H. pylori assessment.
        
        Args:
            to_number: Patient's phone number
            patient_name: Patient's name
            clinician_name: Clinician's name
            pdf_url: URL to full PDF report
            
        Returns:
            Dictionary with send status
        """
        message = (
            f"Hello {patient_name},\n\n"
            f"Your H. pylori assessment results from {clinician_name} are ready. "
            f"Please review the recommendations and follow up as directed."
        )
        
        if pdf_url:
            message += f"\n\nSecure Report: {pdf_url}"
        
        message += "\n\nIf you have questions, please contact your healthcare provider."
        
        return self.send_sms(to_number, message, pdf_url=None)  # PDF already in message
    
    def send_consultation_invite(
        self,
        to_number: str,
        session_url: str,
        clinician_name: str
    ) -> dict:
        """
        Send SMS invitation for video consultation.
        
        Args:
            to_number: Recipient phone number
            session_url: Video consultation URL
            clinician_name: Clinician's name
            
        Returns:
            Dictionary with send status
        """
        message = (
            f"You're invited to a video consultation with {clinician_name}.\n\n"
            f"Join here: {session_url}\n\n"
            f"Please join at your scheduled time."
        )
        
        return self.send_sms(to_number, message)


# Global SMS sender instance
sms_sender = SMSSender()
