"""Configuration management from environment variables."""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()


class Settings:
    """Application settings loaded from environment."""
    
    # Model paths
    SCREEN_MODEL_PATH: str = os.getenv("SCREEN_MODEL_PATH", "models/screening_hp_pos_calibrated.joblib")
    STAGE_MODEL_PATH: Optional[str] = os.getenv("STAGE_MODEL_PATH", "models/staging_3class.joblib")
    
    # Thresholds
    SCREEN_THRESH: float = float(os.getenv("SCREEN_THRESH", "0.60"))
    
    # JWT settings
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change_me_insecure_default")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # CORS
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "http://127.0.0.1:5500,http://localhost:8000,http://localhost:8001,http://127.0.0.1:8001").split(",")
    
    # Frontend URL (for video consultation links)
    # In production (Render), this should be set to your Render URL
    # In local dev, defaults to 127.0.0.1:8001
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://127.0.0.1:8001")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./cdss.db")
    
    # Security
    BCRYPT_ROUNDS: int = 12
    
    # Twilio Configuration
    TWILIO_ACCOUNT_SID: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER: Optional[str] = os.getenv("TWILIO_PHONE_NUMBER")
    
    # Email Configuration
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    FROM_EMAIL: Optional[str] = os.getenv("FROM_EMAIL", os.getenv("SMTP_USER"))
    FROM_NAME: str = os.getenv("FROM_NAME", "H. pylori CDSS")
    
    # File Storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    SIGNATURES_DIR: str = os.getenv("SIGNATURES_DIR", "uploads/signatures")
    PDF_DIR: str = os.getenv("PDF_DIR", "uploads/pdfs")
    
    # Google OAuth Configuration
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
    
    def validate(self) -> None:
        """Validate critical settings."""
        if self.JWT_SECRET == "change_me_insecure_default":
            print("WARNING: Using default JWT_SECRET. Please set JWT_SECRET in .env for production!")
        
        screen_path = Path(self.SCREEN_MODEL_PATH)
        if not screen_path.exists():
            raise FileNotFoundError(f"Screening model not found at {self.SCREEN_MODEL_PATH}")


settings = Settings()
