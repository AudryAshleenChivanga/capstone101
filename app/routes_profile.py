"""User profile management routes."""
import base64
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User
from app.schemas import UserOut, UserProfileUpdate, SignatureUpload
from app.auth import get_current_user
from app.config import settings
import os

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me", response_model=UserOut)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile."""
    # Add has_signature flag
    user_dict = {
        **{c.name: getattr(current_user, c.name) for c in current_user.__table__.columns},
        'has_signature': bool(current_user.digital_signature)
    }
    return user_dict


@router.put("/me", response_model=UserOut)
def update_my_profile(
    profile_data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update current user's profile."""
    # Update fields
    update_data = profile_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if hasattr(current_user, field):
            setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    user_dict = {
        **{c.name: getattr(current_user, c.name) for c in current_user.__table__.columns},
        'has_signature': bool(current_user.digital_signature)
    }
    return user_dict


@router.post("/signature")
def upload_signature(
    signature: SignatureUpload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload digital signature."""
    # Validate base64 data
    try:
        # Check if it's a data URL
        if signature.signature_data.startswith('data:image'):
            # Valid data URL
            current_user.digital_signature = signature.signature_data
        else:
            # Add data URL prefix
            current_user.digital_signature = f"data:image/png;base64,{signature.signature_data}"
        
        db.commit()
        
        return {
            "status": "success",
            "message": "Signature uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid signature data: {str(e)}"
        )


@router.get("/signature")
def get_signature(current_user: User = Depends(get_current_user)):
    """Get current user's signature."""
    if not current_user.digital_signature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No signature found. Please upload a signature first."
        )
    
    return {
        "signature_data": current_user.digital_signature,
        "has_signature": True
    }


@router.delete("/signature")
def delete_signature(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete digital signature."""
    current_user.digital_signature = None
    db.commit()
    
    return {
        "status": "success",
        "message": "Signature deleted successfully"
    }


@router.post("/photo")
async def upload_profile_photo(
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload profile photo."""
    # Validate file type
    if not photo.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Create uploads directory
    os.makedirs("uploads/profiles", exist_ok=True)
    
    # Save file
    file_ext = photo.filename.split('.')[-1]
    file_path = f"uploads/profiles/{current_user.id}.{file_ext}"
    
    contents = await photo.read()
    with open(file_path, 'wb') as f:
        f.write(contents)
    
    # Update user
    current_user.profile_photo = file_path
    db.commit()
    
    return {
        "status": "success",
        "photo_url": f"/{file_path}"
    }
