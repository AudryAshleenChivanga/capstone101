#!/usr/bin/env python3
"""
Update Dr. Sarah's profile photo to be consistent across all sections.
"""

from app.db import SessionLocal
from app.models import User

# Professional female doctor photo
PROFILE_PHOTO_URL = "https://randomuser.me/api/portraits/women/44.jpg"

db = SessionLocal()

# Find Dr. Sarah
dr_sarah = db.query(User).filter(User.username == "dr_sarah").first()

if dr_sarah:
    dr_sarah.profile_photo = PROFILE_PHOTO_URL
    db.commit()
    
    print("\n" + "="*60)
    print("  DR. SARAH PROFILE UPDATED")
    print("="*60)
    print(f"✅ Profile photo updated!")
    print(f"   Username: {dr_sarah.username}")
    print(f"   Name: {dr_sarah.full_name}")
    print(f"   Photo URL: {PROFILE_PHOTO_URL}")
    print()
    print("📸 Dr. Sarah's profile photo will now be consistent across:")
    print("   - Specialist listing (Book Appointment)")
    print("   - Appointment cards")
    print("   - Video consultation sidebar")
    print("="*60 + "\n")
else:
    print("❌ Dr. Sarah not found in database!")

db.close()

