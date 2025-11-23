"""
Quick test script for Video Consultation endpoints
Run with: python test_video_endpoints.py
"""
import requests
import json

API_BASE = "http://127.0.0.1:8000"

def test_health():
    """Test if server is running"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        print("[OK] Server Health:", response.json())
        return True
    except Exception as e:
        print(f"[ERROR] Server not running: {e}")
        print("\nStart server with: python -m uvicorn main:app --reload")
        return False

def test_specialists_endpoint(token):
    """Test getting specialists list"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE}/appointments/specialists", headers=headers)
        
        if response.status_code == 200:
            specialists = response.json()
            print(f"[OK] Specialists Endpoint: Found {len(specialists)} specialists")
            if specialists:
                print(f"   First specialist: {specialists[0].get('username', 'N/A')}")
            return True
        else:
            print(f"[WARN] Specialists Endpoint: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Specialists Endpoint Error: {e}")
        return False

def test_video_routes():
    """Test if video routes are registered"""
    try:
        response = requests.get(f"{API_BASE}/docs")
        if response.status_code == 200:
            print("[OK] API Docs Available: http://127.0.0.1:8000/docs")
            print("   Check /video/* endpoints in Swagger UI")
            return True
        else:
            print("[WARN] Could not access API docs")
            return False
    except Exception as e:
        print(f"[ERROR] API Docs Error: {e}")
        return False

def print_test_instructions():
    """Print manual testing instructions"""
    print("\n" + "="*70)
    print("[MANUAL TESTING STEPS]")
    print("="*70)
    print("""
1. OPEN TWO BROWSERS:
   Browser 1: http://127.0.0.1:8000/ui/login.html
   Browser 2: http://127.0.0.1:8000/ui/login.html (Incognito/Private)

2. LOGIN:
   Browser 1: Any user (will be clinician)
   Browser 2: User with 'specialist' role

3. BOOK APPOINTMENT:
   Browser 1 -> Click "Video Consult" in sidebar
             -> Click "Book Consultation" on a specialist card
             -> Fill date, time, reason
             -> Click "Send Request"

4. ACCEPT APPOINTMENT:
   Browser 2 -> Click "Video Consult" in sidebar
             -> Click "Pending Requests" tab (specialists only)
             -> Click "Accept" on the request

5. START VIDEO CALL:
   Either Browser -> Go to "Upcoming Sessions" tab
                  -> Click "Start Video Call"
                  -> Allow camera/microphone permissions
                  -> Wait for other user to join

6. JOIN AS SECOND USER:
   Other Browser -> "Upcoming Sessions" -> "Join Call"
                OR use the guest URL from first user

7. TEST VIDEO/AUDIO:
   - See both video streams
   - Hear audio from both sides
   - Test mute/unmute
   - Test camera on/off
   - End call

EXPECTED RESULTS:
=================
[OK] Appointment workflow completes
[OK] Video session created
[OK] Both users can join
[OK] WebRTC connection established
[OK] Video and audio work bidirectionally
[OK] Controls functional (mute, camera, end call)

TROUBLESHOOTING:
================
- If "No specialists found" -> Create a user with role='specialist' in admin panel
- If "Cannot create session" -> Make sure appointment is "accepted" status
- If camera not working -> Check browser permissions (chrome://settings/content)
- If no video stream -> Check firewall, try different browser

API DOCUMENTATION:
==================
Full API docs: http://127.0.0.1:8000/docs
Video routes: Look for /video/* and /appointments/*

DETAILED GUIDE:
===============
See: VIDEO_CONSULTATION_TEST_GUIDE.md
""")

if __name__ == "__main__":
    print("[VIDEO CONSULTATION] - ENDPOINT TESTER\n")
    
    # Test 1: Server health
    if not test_health():
        exit(1)
    
    print()
    
    # Test 2: Video routes registration
    test_video_routes()
    
    print()
    
    # Print instructions for manual testing
    print("[NOTE] Full video testing requires manual steps (two users)")
    print("    Run with a token to test specialist endpoint:")
    print("    Example: python test_video_endpoints.py YOUR_TOKEN_HERE\n")
    
    import sys
    if len(sys.argv) > 1:
        token = sys.argv[1]
        print(f"Testing with provided token...\n")
        test_specialists_endpoint(token)
    else:
        print("Skipping authenticated endpoint tests (no token provided)")
    
    # Print manual test instructions
    print_test_instructions()

