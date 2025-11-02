"""
Test script for Capsule Endoscopy RL Backend API
"""
import requests
import json
import time

# API Base URL
BASE_URL = "http://localhost:8000"

def test_capsule_endoscopy_api():
    """Test all capsule endoscopy endpoints"""
    
    print("=" * 60)
    print("TESTING CAPSULE ENDOSCOPY API")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1. Testing Backend Health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        assert response.status_code == 200, "Health check failed"
        print("   ✅ Backend is healthy")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 2: Capsule Endoscopy Endpoint Exists
    print("\n2. Testing Capsule Endoscopy Endpoint...")
    try:
        payload = {
            "scenario": "mixed",
            "num_episodes": 5
        }
        response = requests.post(
            f"{BASE_URL}/biopsy/capsule-endoscopy",
            json=payload
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Endpoint works!")
            print(f"   Response keys: {list(data.keys())}")
            
            # Check for expected fields
            required_fields = ['total_steps', 'total_detections', 'training_log', 'detections', 'images', 'agent_stats']
            missing_fields = [f for f in required_fields if f not in data]
            
            if missing_fields:
                print(f"   ⚠️  Missing fields: {missing_fields}")
            else:
                print(f"   ✅ All required fields present")
                
            # Show some results
            print(f"\n   Results Summary:")
            print(f"   - Total Steps: {data.get('total_steps', 0)}")
            print(f"   - Total Detections: {data.get('total_detections', 0)}")
            print(f"   - Training Episodes: {len(data.get('training_log', []))}")
            print(f"   - Images Captured: {len(data.get('images', []))}")
            print(f"   - Detections Made: {len(data.get('detections', []))}")
            
            # Show first detection if available
            if data.get('detections'):
                print(f"\n   First Detection:")
                first_detection = data['detections'][0]
                print(f"   - Type: {first_detection.get('pathology_type')}")
                print(f"   - Confidence: {first_detection.get('confidence', 0):.2%}")
                print(f"   - Position: {first_detection.get('position')}")
                
            # Show agent stats
            if data.get('agent_stats'):
                stats = data['agent_stats']
                print(f"\n   Agent Stats:")
                print(f"   - Total Samples: {stats.get('total_samples', 0)}")
                print(f"   - Epsilon: {stats.get('epsilon', 0):.3f}")
                print(f"   - Average Reward: {stats.get('avg_reward', 0):.4f}")
                
        else:
            print(f"   ❌ Endpoint returned {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request Error: {e}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Test Different Scenarios
    print("\n3. Testing Different Pathology Scenarios...")
    scenarios = ['healthy', 'h_pylori', 'peptic_ulcer', 'gastric_cancer', 'tumor', 'mixed']
    
    for scenario in scenarios:
        try:
            print(f"\n   Testing scenario: {scenario}")
            response = requests.post(
                f"{BASE_URL}/biopsy/capsule-endoscopy",
                json={"scenario": scenario, "num_episodes": 3}
            )
            
            if response.status_code == 200:
                data = response.json()
                detections = len(data.get('detections', []))
                images = len(data.get('images', []))
                print(f"   ✅ {scenario}: {detections} detections, {images} images")
            else:
                print(f"   ❌ {scenario}: Status {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {scenario}: Error - {e}")
    
    # Test 4: Performance Test (Quick)
    print("\n4. Testing API Response Time...")
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/biopsy/capsule-endoscopy",
            json={"scenario": "mixed", "num_episodes": 5}
        )
        elapsed = time.time() - start_time
        
        print(f"   Response time: {elapsed:.2f} seconds")
        if elapsed < 5:
            print(f"   ✅ Good performance")
        elif elapsed < 10:
            print(f"   ⚠️  Moderate performance")
        else:
            print(f"   ⚠️  Slow performance")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    print("Make sure your server is running on http://localhost:8000")
    print("Press Enter to start testing...")
    input()
    
    test_capsule_endoscopy_api()
    
    print("\n\nPress Enter to exit...")
    input()

