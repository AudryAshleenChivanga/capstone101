#!/usr/bin/env python3
"""Simple script to update specialists directly using app models."""

import sys
sys.path.append('.')

from app.db import SessionLocal
from app.models import User

# Specialists to update
UPDATES = {
    "dr.martinez": {
        "full_name": "Dr. Sarah Martinez",
        "specialty": "Gastroenterology",
        "institution": "City Medical Center"
    },
    "dr.chen": {
        "full_name": "Dr. James Chen",
        "specialty": "Gastroenterology & Hepatology",
        "institution": "Metropolitan Hospital"
    },
    "dr.rodriguez": {
        "full_name": "Dr. Emily Rodriguez",
        "specialty": "Gastroenterology",
        "institution": "University Medical Center"
    }
}

def main():
    print("\n" + "="*60)
    print("  UPDATING SPECIALIST INFORMATION")
    print("="*60 + "\n")
    
    db = SessionLocal()
    
    try:
        updated_count = 0
        
        for username, update_data in UPDATES.items():
            print(f"[*] Updating {username}...")
            
            # Find user
            user = db.query(User).filter(User.username == username).first()
            
            if user:
                user.full_name = update_data['full_name']
                user.specialty = update_data['specialty']
                user.institution = update_data['institution']
                
                print(f"   Full Name: {update_data['full_name']}")
                print(f"   Specialty: {update_data['specialty']}")
                print(f"   Institution: {update_data['institution']}")
                print(f"[+] Successfully updated!\n")
                
                updated_count += 1
            else:
                print(f"[X] User not found!\n")
        
        db.commit()
        
        print("="*60)
        print("  UPDATE COMPLETE")
        print("="*60)
        print(f"\n[+] Successfully updated: {updated_count} specialists")
        print("\n[!] Specialists now have proper information!")
        print("\n[>] Test it:")
        print("   Go to: http://localhost:8000/ui/dashboard_new.html")
        print("   Login as admin")
        print("   Click 'Video Consult' -> 'Book Appointment'")
        print("   You should see beautiful specialist cards!")
        print("\n" + "="*60 + "\n")
        
    except Exception as e:
        print(f"[X] Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()

