#!/usr/bin/env python3

import requests
import json
import time

def test_service_auth():
    print("🧪 Testing Flask Service Authentication")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5000"
    
    try:
        # Test 1: Health check
        print("1. Testing health check...")
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            print("   ✅ Health check passed")
            print(f"   📝 Response: {response.json()}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return
        
        # Test 2: User authentication (will require device code)
        print("\n2. Testing user authentication...")
        print("   ⚠️  This will require you to authenticate via device code")
        response = requests.get(f"{base_url}/api/auth/user")
        
        if response.status_code == 200:
            user_data = response.json()
            print("   ✅ User authentication successful")
            print(f"   👤 User: {user_data.get('displayName')}")
            print(f"   📧 Email: {user_data.get('email')}")
        else:
            print(f"   ❌ User authentication failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            return
        
        # Test 3: User authentication again (should use cached token)
        print("\n3. Testing user authentication again (should use cache)...")
        response = requests.get(f"{base_url}/api/auth/user")
        
        if response.status_code == 200:
            user_data = response.json()
            print("   ✅ Second user authentication successful (cached)")
            print(f"   👤 User: {user_data.get('displayName')}")
        else:
            print(f"   ❌ Second user authentication failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            return
        
        # Test 4: Email search
        print("\n4. Testing email search...")
        search_data = {
            "employeeName": "test",
            "count": 5
        }
        response = requests.post(
            f"{base_url}/api/emails/search",
            json=search_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            email_data = response.json()
            email_count = len(email_data.get('emails', []))
            print(f"   ✅ Email search successful")
            print(f"   📧 Found {email_count} emails with 'test' in subject")
        else:
            print(f"   ❌ Email search failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
        
        print("\n🎉 All service tests completed!")
        print("✅ Flask service authentication is working properly")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask service")
        print("   Make sure the service is running: python email_service_sync.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_service_auth() 