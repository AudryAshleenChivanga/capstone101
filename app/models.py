"""SQLAlchemy database models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from app.db import Base


class Patient(Base):
    """Centralized Patient model for managing patient records."""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), unique=True, index=True, nullable=False)  # HP-2025-XXXX format
    
    # Patient demographics
    full_name = Column(String(200), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    age = Column(Integer, nullable=True)
    sex = Column(String(10), nullable=True)
    residence = Column(String(200), nullable=True)
    
    # Contact information
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    
    # Medical information
    blood_type = Column(String(10), nullable=True)
    allergies = Column(Text, nullable=True)
    medical_history = Column(JSON, nullable=True)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Integer, default=1)
    notes = Column(Text, nullable=True)
    
    # Relationships
    cases = relationship("Case", back_populates="patient")
    creator = relationship("User", foreign_keys=[created_by])
    
    # Index for faster searches
    __table_args__ = (
        Index('idx_patient_search', 'patient_id', 'full_name', 'phone'),
    )


class User(Base):
    """User model with role-based access control."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="clinician")  # clinician, specialist, admin
    
    # Profile fields
    full_name = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    specialty = Column(String(100), nullable=True)
    license_number = Column(String(100), nullable=True)
    institution = Column(String(200), nullable=True)
    bio = Column(Text, nullable=True)
    profile_photo = Column(String(500), nullable=True)
    digital_signature = Column(Text, nullable=True)  # Base64 signature image
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Integer, default=1)
    
    # Relationships
    cases = relationship("Case", back_populates="user", foreign_keys="Case.user_id")


class Case(Base):
    """Case history storing each CDSS recommendation with multi-stage workflow support."""
    __tablename__ = "cases"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    patient_db_id = Column(Integer, ForeignKey("patients.id"), nullable=True)  # Link to Patient table
    
    # Input data (stored as JSON)
    input_data = Column(JSON, nullable=False)
    case_type = Column(String(50), nullable=True, index=True)  # screening, staging, consultation
    
    # Multi-Stage Workflow Support
    workflow_stage = Column(String(50), nullable=True, index=True)  # stage1_symptom, stage2_lab, stage3_ric
    stage1_assessment = Column(JSON, nullable=True)  # Symptom-based assessment results
    stage2_lab_results = Column(JSON, nullable=True)  # Lab test results (antibody, serology)
    stage3_ric_values = Column(JSON, nullable=True)  # RIC staging values
    
    # Predictions
    screen_prob = Column(Float, nullable=True)
    stage_pred = Column(String(50), nullable=True)  # low, moderate, high
    symptom_risk_level = Column(String(50), nullable=True)  # For Stage 1
    lab_recommendation = Column(Text, nullable=True)  # Recommended lab tests from Stage 1
    
    # Recommendations (stored as JSON list)
    recommendations = Column(JSON, nullable=True)  # Original AI recommendations
    edited_recommendations = Column(JSON, nullable=True)  # Clinician-edited version
    
    # Signature and approval
    signed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    signature_data = Column(Text, nullable=True)  # Base64 signature image
    signed_at = Column(DateTime, nullable=True)
    is_approved = Column(Integer, default=0)
    
    # PDF and delivery
    pdf_path = Column(String(500), nullable=True)
    sent_to_patient = Column(Integer, default=0)
    sent_at = Column(DateTime, nullable=True)
    patient_phone = Column(String(50), nullable=True)
    patient_email = Column(String(255), nullable=True)
    
    # Metadata
    patient_pseudo_id = Column(String(100), nullable=True, index=True)  # Optional anonymized ID
    patient_name = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="cases", foreign_keys="[Case.user_id]")
    patient = relationship("Patient", back_populates="cases")


class TelemedSession(Base):
    """Telemedicine session tracking."""
    __tablename__ = "telemed_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    host_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Session host
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=True)
    token = Column(String(255), nullable=True)  # Legacy column - optional
    status = Column(String(50), default="active")  # active, completed, expired
    created_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)


class Appointment(Base):
    """Appointment scheduling for clinician-gastroenterologist consultations."""
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    clinician_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Requesting clinician
    specialist_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Gastroenterologist
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=True)
    
    # Scheduling details
    requested_date = Column(DateTime, nullable=False)  # Preferred appointment date/time
    scheduled_date = Column(DateTime, nullable=True)  # Actual scheduled date (may be different)
    duration_minutes = Column(Integer, default=30)
    
    # Status: pending, accepted, rejected, completed, cancelled
    status = Column(String(50), default="pending", nullable=False)
    
    # Notes and reason
    reason = Column(Text, nullable=True)  # Reason for consultation
    clinician_notes = Column(Text, nullable=True)
    specialist_notes = Column(Text, nullable=True)  # Specialist can add notes when accepting/rejecting
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    accepted_at = Column(DateTime, nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)


class Prescription(Base):
    """Prescription and treatment recommendations for patients."""
    __tablename__ = "prescriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    prescribed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Prescription details
    medications = Column(JSON, nullable=False)  # List of {name, dosage, frequency, duration}
    diagnosis = Column(Text, nullable=False)
    recommendations = Column(Text, nullable=True)  # Clinical recommendations
    lifestyle_advice = Column(Text, nullable=True)
    follow_up_days = Column(Integer, nullable=True)  # Days until follow-up
    
    # Stage-specific treatment protocols
    stage = Column(String(50), nullable=True)  # Stage 1 (symptom), Stage 2 (lab), Stage 3 (RIC)
    protocol_type = Column(String(100), nullable=True)  # eradication, maintenance, palliative
    
    # Lab tests ordered
    lab_tests_ordered = Column(JSON, nullable=True)  # List of tests to be performed
    
    # Status tracking
    status = Column(String(50), default="pending")  # pending, dispensed, completed, cancelled
    dispensed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = Column(Text, nullable=True)
    
    # Relationships
    patient = relationship("Patient")
    case = relationship("Case")
    prescriber = relationship("User")


class ModelTraining(Base):
    """Track model training and retraining history."""
    __tablename__ = "model_training"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False, index=True)  # screening, staging, symptom_assessment
    model_version = Column(String(50), nullable=False)
    model_type = Column(String(50), nullable=False)  # classification, regression, etc.
    
    # Training details
    training_start = Column(DateTime, nullable=False)
    training_end = Column(DateTime, nullable=True)
    status = Column(String(50), default="training")  # training, completed, failed, active
    
    # Dataset information
    dataset_size = Column(Integer, nullable=True)
    training_samples = Column(Integer, nullable=True)
    validation_samples = Column(Integer, nullable=True)
    test_samples = Column(Integer, nullable=True)
    
    # Performance metrics
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    auc_roc = Column(Float, nullable=True)
    other_metrics = Column(JSON, nullable=True)  # Additional metrics
    
    # Model files
    model_path = Column(String(500), nullable=True)
    config_data = Column(JSON, nullable=True)  # Hyperparameters, features used, etc.
    
    # Deployment
    is_production = Column(Integer, default=0)  # Is this the active production model?
    deployed_at = Column(DateTime, nullable=True)
    replaced_at = Column(DateTime, nullable=True)  # When replaced by newer version
    
    # Tracking
    trained_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    
    # Relationships
    trainer = relationship("User")
