#!/usr/bin/env python3
"""
Update existing specialists with proper information.
"""

import requests

API_BASE = "http://localhost:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Admin@2024"

# Specialists to update with their new information
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
    
    # Login as admin
    print("[*] Authenticating as admin...")
    try:
        login_response = requests.post(
            f"{API_BASE}/auth/login",
            json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
            timeout=5
        )
        
        if login_response.status_code != 200:
            print("[X] Authentication failed!")
            return
        
        token = login_response.json()["access_token"]
        print("[+] Authentication successful!\n")
        
    except Exception as e:
        print(f"[X] Error: {e}")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Get all specialists
    print("[*] Fetching specialists...")
    specialists_response = requests.get(
        f"{API_BASE}/appointments/specialists",
        headers=headers
    )
    
    specialists = specialists_response.json()
    print(f"[+] Found {len(specialists)} specialists\n")
    
    # Update each specialist using SQL direct update
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    
    # Connect to database
    engine = create_engine('sqlite:///./capstone_cdss.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    updated_count = 0
    
    for specialist in specialists:
        username = specialist['username']
        if username in UPDATES:
            update_data = UPDATES[username]
            
            print(f"[*] Updating {username}...")
            print(f"   Full Name: {update_data['full_name']}")
            print(f"   Specialty: {update_data['specialty']}")
            print(f"   Institution: {update_data['institution']}")
            
            try:
                # Update using SQL
                query = text("""
                    UPDATE users 
                    SET full_name = :full_name,
                        specialty = :specialty,
                        institution = :institution
                    WHERE username = :username
                """)
                
                session.execute(query, {
                    'full_name': update_data['full_name'],
                    'specialty': update_data['specialty'],
                    'institution': update_data['institution'],
                    'username': username
                })
                session.commit()
                
                print(f"[+] Successfully updated!\n")
                updated_count += 1
                
            except Exception as e:
                print(f"[X] Failed: {e}\n")
                session.rollback()
    
    session.close()
    
    # Summary
    print("="*60)
    print("  UPDATE COMPLETE")
    print("="*60)
    print(f"\n[+] Successfully updated: {updated_count} specialists")
    
    if updated_count > 0:
        print("\n[!] Specialists now have proper information!")
        print("\n[>] Test it:")
        print("   1. Go to http://localhost:8000/ui/dashboard_new.html")
        print("   2. Login as admin")
        print("   3. Click 'Video Consult' in sidebar")
        print("   4. You should see specialist cards with names and info!")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()

