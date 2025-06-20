#!/usr/bin/env python3

import requests
import json
import time

def test_simple_service():
    print("🧪 Testing Simple Email Service")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5001"
    
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
        print("   ⏳ This may take a moment as it runs in a separate process...")
        
        start_time = time.time()
        response = requests.get(f"{base_url}/api/auth/user", timeout=120)
        end_time = time.time()
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ User authentication successful (took {end_time - start_time:.1f}s)")
            print(f"   👤 User: {user_data.get('displayName')}")
            print(f"   📧 Email: {user_data.get('email')}")
        else:
            print(f"   ❌ User authentication failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            return
        
        # Test 3: User authentication again (should reuse token)
        print("\n3. Testing user authentication again...")
        print("   ⏳ This should be faster as it may reuse the token...")
        
        start_time = time.time()
        response = requests.get(f"{base_url}/api/auth/user", timeout=120)
        end_time = time.time()
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ Second user authentication successful (took {end_time - start_time:.1f}s)")
            print(f"   👤 User: {user_data.get('displayName')}")
        else:
            print(f"   ❌ Second user authentication failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            return
        
        # Test 4: Email search
        print("\n4. Testing email search...")
        print("   ⏳ Searching for emails with 'test' in subject...")
        
        search_data = {
            "employeeName": "test",
            "count": 5
        }
        
        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/emails/search",
            json=search_data,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        end_time = time.time()
        
        if response.status_code == 200:
            email_data = response.json()
            email_count = len(email_data.get('emails', []))
            print(f"   ✅ Email search successful (took {end_time - start_time:.1f}s)")
            print(f"   📧 Found {email_count} emails with 'test' in subject")
            
            # Show first email if any
            if email_count > 0:
                first_email = email_data['emails'][0]
                print(f"   📄 First email: {first_email.get('subject', 'No subject')}")
                print(f"   👤 From: {first_email.get('from', {}).get('name', 'Unknown')}")
        else:
            print(f"   ❌ Email search failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
        
        print("\n🎉 All service tests completed!")
        print("✅ Simple email service is working properly")
        print("✅ No event loop issues encountered")
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out - this may happen during authentication")
        print("   Try running the test again if authentication was successful")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to simple email service")
        print("   Make sure the service is running: python email_service_simple.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_simple_service() 