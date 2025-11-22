"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# User schemas
class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    role: str = "clinician"


class UserCreate(UserBase):
    password: str
    specialty: Optional[str] = None
    institution: Optional[str] = None
    license_number: Optional[str] = None
    bio: Optional[str] = None
    profile_photo: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserOut(UserResponse):
    """Extended user response with profile information."""
    phone: Optional[str] = None
    specialty: Optional[str] = None
    license_number: Optional[str] = None
    institution: Optional[str] = None
    bio: Optional[str] = None
    profile_photo: Optional[str] = None
    digital_signature: Optional[str] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class LoginRequest(BaseModel):
    username: str
    password: str


# Case schemas
class CaseCreate(BaseModel):
    input_data: Dict[str, Any]
    task: str = "screening"


class CaseResponse(BaseModel):
    id: int
    user_id: int
    input_data: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None
    screen_prob: Optional[float] = None
    stage_pred: Optional[str] = None
    patient_name: Optional[str] = None
    patient_phone: Optional[str] = None
    task: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Recommendation schemas
class RecommendationRequest(BaseModel):
    # Screening fields
    age: Optional[int] = None
    sex: Optional[str] = None
    residence: Optional[str] = None
    stool_ag: Optional[int] = None
    hemoglobin: Optional[float] = None
    
    # Staging fields
    mic_clari: Optional[float] = None
    mut_A2143G: Optional[int] = None
    mut_A2144G: Optional[int] = None
    
    # Patient identification (optional)
    patient_pseudo_id: Optional[str] = None
    patient_name: Optional[str] = None
    patient_phone: Optional[str] = None
    patient_email: Optional[str] = None
    
    # Task type
    task: str = "screening"


class RecommendationResponse(BaseModel):
    screen_prob: Optional[float] = None
    stage_pred: Optional[str] = None
    recommendations: List[str]
    input_data: Optional[Dict[str, Any]] = None
    case_id: Optional[int] = None


# SMS schemas
class SMSRequest(BaseModel):
    phone_number: str
    message: str


class SMSResponse(BaseModel):
    success: bool
    message_sid: Optional[str] = None
    error: Optional[str] = None


# Video consultation schemas
class VideoSessionCreate(BaseModel):
    patient_name: str
    session_type: str = "consultation"


class VideoSessionResponse(BaseModel):
    session_id: str
    room_name: str
    token: str
    expires_at: datetime


# Document schemas
class DocumentCreate(BaseModel):
    case_id: int
    patient_name: str
    patient_phone: str


class DocumentUpdate(BaseModel):
    content: str


class DocumentSign(BaseModel):
    signature_data: str  # Base64 encoded signature image


class DocumentEdit(BaseModel):
    recommendations: List[str]  # Edited recommendations list


class DocumentResponse(BaseModel):
    id: int
    case_id: int
    patient_name: str
    patient_phone: str
    content: str
    status: str
    signature_data: Optional[str] = None
    created_at: datetime
    signed_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Admin user management
class AdminUserCreate(BaseModel):
    """Admin schema for creating users."""
    username: str
    email: str
    password: str
    role: str = Field(..., regex="^(clinician|specialist|admin)$")
    full_name: Optional[str] = None
    specialty: Optional[str] = None
    institution: Optional[str] = None


class AdminUserUpdate(BaseModel):
    """Admin schema for updating any user."""
    email: Optional[str] = None
    role: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    specialty: Optional[str] = None
    license_number: Optional[str] = None
    institution: Optional[str] = None
    is_active: Optional[int] = None


# Appointment scheduling schemas
class AppointmentCreate(BaseModel):
    """Create appointment request."""
    specialist_id: int
    case_id: Optional[int] = None
    requested_date: datetime
    duration_minutes: int = Field(default=30, ge=15, le=120)
    reason: Optional[str] = None
    clinician_notes: Optional[str] = None


class AppointmentUpdate(BaseModel):
    """Update appointment (reschedule, add notes)."""
    requested_date: Optional[datetime] = None
    scheduled_date: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(default=None, ge=15, le=120)
    clinician_notes: Optional[str] = None


class AppointmentResponse(BaseModel):
    """Specialist response to appointment request."""
    status: str = Field(..., regex="^(accepted|rejected)$")
    scheduled_date: Optional[datetime] = None  # Can propose different time
    specialist_notes: Optional[str] = None


class AppointmentOut(BaseModel):
    """Appointment output schema."""
    id: int
    clinician_id: int
    specialist_id: int
    case_id: Optional[int]
    requested_date: datetime
    scheduled_date: Optional[datetime]
    duration_minutes: int
    status: str
    reason: Optional[str]
    clinician_notes: Optional[str]
    specialist_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    accepted_at: Optional[datetime]
    rejected_at: Optional[datetime]
    
    # Additional fields for convenience
    clinician_name: Optional[str] = None
    specialist_name: Optional[str] = None
    
    class Config:
        orm_mode = True


class SpecialistAvailability(BaseModel):
    """Get specialist's available time slots."""
    specialist_id: int
    date: datetime
    available_slots: List[str] = []


class SpecialistListItem(BaseModel):
    """Specialist list item for appointment booking."""
    id: int
    username: str
    full_name: Optional[str]
    specialty: Optional[str]
    institution: Optional[str]
    profile_photo: Optional[str]
    
    class Config:
        orm_mode = True


# Profile management schemas
class UserProfileUpdate(BaseModel):
    """Update user profile information."""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    specialty: Optional[str] = None
    license_number: Optional[str] = None
    institution: Optional[str] = None
    bio: Optional[str] = None


class SignatureUpload(BaseModel):
    """Upload digital signature."""
    signature_data: str  # Base64 encoded signature image


# Chat/Conversation schemas
class MessageCreate(BaseModel):
    """Create a new message."""
    conversation_id: Optional[int] = None  # If None, creates new conversation
    receiver_id: Optional[int] = None  # User ID to message (for new conversations)
    patient_id: Optional[int] = None  # Patient ID to message (for new conversations)
    content: str = Field(..., min_length=1, max_length=5000)
    message_type: str = "text"
    case_id: Optional[int] = None  # Related case ID


class MessageResponse(BaseModel):
    """Message response."""
    id: int
    conversation_id: int
    sender_id: int
    sender_name: Optional[str] = None
    sender_role: Optional[str] = None
    content: str
    message_type: str
    attachment_url: Optional[str] = None
    is_read: bool
    read_at: Optional[datetime] = None
    is_edited: bool
    edited_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    """Create a new conversation."""
    receiver_id: Optional[int] = None  # User to start conversation with
    patient_id: Optional[int] = None  # Patient to start conversation with
    case_id: Optional[int] = None
    appointment_id: Optional[int] = None
    title: Optional[str] = None
    initial_message: str = Field(..., min_length=1, max_length=5000)


class ConversationResponse(BaseModel):
    """Conversation response."""
    id: int
    user1_id: int
    user2_id: Optional[int] = None
    patient_id: Optional[int] = None
    case_id: Optional[int] = None
    appointment_id: Optional[int] = None
    conversation_type: str
    status: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_message_at: datetime
    
    # Additional fields for frontend
    other_participant_name: Optional[str] = None
    other_participant_role: Optional[str] = None
    other_participant_photo: Optional[str] = None
    unread_count: int = 0
    last_message: Optional[str] = None
    last_message_sender: Optional[str] = None

    class Config:
        from_attributes = True


class ConversationWithMessages(ConversationResponse):
    """Conversation with messages list."""
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True


class MarkAsRead(BaseModel):
    """Mark messages as read."""
    message_ids: List[int]