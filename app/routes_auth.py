"""Authentication routes."""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests
import secrets

from app.db import get_db
from app.models import User
from app.schemas import UserCreate, LoginRequest, Token, UserResponse
from app.auth import (
    hash_password,
    authenticate_user,
    create_access_token,
    get_current_user,
    require_role
)
from app.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Register a new user (admin only).
    
    For initial setup, if no users exist, anyone can register the first admin.
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role=user_data.role,
        full_name=user_data.full_name,
        specialty=user_data.specialty,
        institution=user_data.institution,
        license_number=user_data.license_number,
        bio=user_data.bio,
        profile_photo=user_data.profile_photo
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Convert to UserResponse to ensure proper serialization
    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        role=new_user.role,
        full_name=new_user.full_name,
        specialty=new_user.specialty,
        institution=new_user.institution,
        license_number=new_user.license_number,
        bio=new_user.bio,
        profile_photo=new_user.profile_photo,
        is_active=new_user.is_active,
        created_at=new_user.created_at
    )


@router.post("/register/first", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_first_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register the first admin user (no authentication required).
    Only works if no users exist in the database.
    """
    # Check if any users exist
    user_count = db.query(User).count()
    if user_count > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="First user already registered. Use /auth/register with admin privileges."
        )
    
    # Force role to admin for first user
    user_data.role = "admin"
    
    # Check if username already exists (shouldn't happen, but safety check)
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create first admin user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role="admin",
        full_name=user_data.full_name,
        specialty=user_data.specialty,
        institution=user_data.institution,
        license_number=user_data.license_number,
        bio=user_data.bio,
        profile_photo=user_data.profile_photo
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Convert to UserResponse to ensure proper serialization
    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        role=new_user.role,
        full_name=new_user.full_name,
        specialty=new_user.specialty,
        institution=new_user.institution,
        license_number=new_user.license_number,
        bio=new_user.bio,
        profile_photo=new_user.profile_photo,
        is_active=new_user.is_active,
        created_at=new_user.created_at
    )


@router.post("/login", response_model=Token)
def login(user_credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token.
    """
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }


@router.post("/google/login", response_model=Token)
async def google_login(request: Request, db: Session = Depends(get_db)):
    """
    Authenticate user with Google OAuth token.
    """
    try:
        # Get the token from request body
        body = await request.json()
        token = body.get("credential")
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No credential provided"
            )
        
        # Verify the Google token
        if not settings.GOOGLE_CLIENT_ID:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google OAuth not configured. Please set GOOGLE_CLIENT_ID in environment variables."
            )
        
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            settings.GOOGLE_CLIENT_ID
        )
        
        # Get user info from Google
        email = idinfo.get('email')
        name = idinfo.get('name', email.split('@')[0])
        google_id = idinfo.get('sub')
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by Google"
            )
        
        # Check if user exists by email
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Create new user with Google authentication
            # Generate username from email
            username = email.split('@')[0]
            base_username = username
            counter = 1
            
            # Ensure username is unique
            while db.query(User).filter(User.username == username).first():
                username = f"{base_username}{counter}"
                counter += 1
            
            # Create user with a random password (they'll use Google login)
            user = User(
                username=username,
                email=email,
                hashed_password=hash_password(secrets.token_urlsafe(32)),
                role="doctor",  # Default role for new Google users
                full_name=name,
                is_active=True
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Create access token
        access_token = create_access_token(data={"sub": user.username, "role": user.role})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
        }
        
    except ValueError as e:
        # Invalid token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )
