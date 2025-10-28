"""Email sending functionality."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.config import settings


class EmailSender:
    """Handler for sending email notifications."""
    
    def __init__(self):
        """Initialize email configuration."""
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        self.from_name = settings.FROM_NAME
        
        # Check if email is configured
        self.is_configured = all([
            self.smtp_host,
            self.smtp_port,
            self.smtp_user,
            self.smtp_password,
            self.from_email
        ])
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> dict:
        """
        Send an email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
            
        Returns:
            Dictionary with status
        """
        if not self.is_configured:
            return {
                "status": "error",
                "message": "Email not configured. Set SMTP settings in .env",
                "simulated": True
            }
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Attach plain text
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Attach HTML if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return {
                "status": "success",
                "to": to_email,
                "subject": subject
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error_message": str(e),
                "to": to_email
            }
    
    def send_recommendations_email(
        self,
        to_email: str,
        patient_name: str,
        clinician_name: str,
        recommendations: list,
        case_id: int
    ) -> dict:
        """
        Send H. pylori recommendations via email.
        
        Args:
            to_email: Patient's email
            patient_name: Patient's name
            clinician_name: Clinician's name
            recommendations: List of recommendations
            case_id: Case ID for reference
            
        Returns:
            Dictionary with send status
        """
        subject = "Your H. pylori Assessment Results"
        
        # Plain text version
        recs_text = "\n\n".join(f"{i+1}. {rec}" for i, rec in enumerate(recommendations))
        body = f"""Hello {patient_name},

Your H. pylori assessment results from {clinician_name} are ready.

RECOMMENDATIONS:

{recs_text}

Please follow these recommendations carefully and contact your healthcare provider if you have any questions.

Case Reference: #{case_id}

Best regards,
H. pylori CDSS Team
"""
        
        # HTML version (prettier)
        recs_html = "".join(f"<li style='margin: 10px 0;'>{rec}</li>" for rec in recommendations)
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }}
        .recommendations {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        ul {{ padding-left: 20px; }}
        .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        .case-ref {{ background: #e3f2fd; padding: 10px; border-radius: 5px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2 style="margin: 0;">🏥 H. pylori CDSS</h2>
            <p style="margin: 5px 0 0 0;">Your Assessment Results</p>
        </div>
        <div class="content">
            <p>Hello <strong>{patient_name}</strong>,</p>
            
            <p>Your H. pylori assessment results from <strong>{clinician_name}</strong> are ready.</p>
            
            <div class="recommendations">
                <h3 style="color: #667eea; margin-top: 0;">📋 Recommendations:</h3>
                <ul>
                    {recs_html}
                </ul>
            </div>
            
            <p>Please follow these recommendations carefully and contact your healthcare provider if you have any questions.</p>
            
            <div class="case-ref">
                <strong>Case Reference:</strong> #{case_id}
            </div>
            
            <p style="margin-top: 30px;">Best regards,<br>
            <strong>H. pylori CDSS Team</strong></p>
        </div>
        <div class="footer">
            <p>This is an automated message from the H. pylori Clinical Decision Support System.</p>
        </div>
    </div>
</body>
</html>
"""
        
        return self.send_email(to_email, subject, body, html_body)


# Global email sender instance
email_sender = EmailSender()

