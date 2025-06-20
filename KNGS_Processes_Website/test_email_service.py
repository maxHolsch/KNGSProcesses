#!/usr/bin/env python3

import requests
import json
import time

def test_email_service():
    """Test the email service endpoints"""
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Testing Email Service...")
    print("=" * 50)
    
    # Test 1: Health Check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Health check passed")
            print(f"   📊 Response: {response.json()}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Health check failed: {e}")
        print("   💡 Make sure the email service is running: python start_email_service.py")
        return False
    
    # Test 2: Debug Authentication
    print("\n2. Testing debug authentication...")
    try:
        response = requests.get(f"{base_url}/api/debug/auth", timeout=15)
        if response.status_code == 200:
            debug_data = response.json()
            print("   ✅ Debug authentication successful")
            print(f"   👤 User: {debug_data.get('user', {}).get('displayName', 'Unknown')}")
            print(f"   📧 Email: {debug_data.get('user', {}).get('email', 'Unknown')}")
            print(f"   🔑 Token: {debug_data.get('token_preview', 'Unknown')}")
        else:
            print(f"   ⚠️  Debug authentication failed: {response.status_code}")
            debug_data = response.json()
            print(f"   📝 Step: {debug_data.get('step', 'Unknown')}")
            print(f"   📝 Error: {debug_data.get('error', 'Unknown error')}")
            print(f"   📝 Type: {debug_data.get('type', 'Unknown')}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Debug authentication test failed: {e}")

    # Test 3: User Info (requires authentication)
    print("\n3. Testing user authentication...")
    try:
        response = requests.get(f"{base_url}/api/auth/user", timeout=10)
        if response.status_code == 200:
            user_data = response.json()
            print("   ✅ User authentication successful")
            print(f"   👤 User: {user_data.get('displayName', 'Unknown')}")
            print(f"   📧 Email: {user_data.get('email', 'Unknown')}")
        else:
            print(f"   ⚠️  User authentication failed: {response.status_code}")
            print("   💡 This is expected if you haven't authenticated yet")
            error_data = response.json()
            print(f"   📝 Details: {error_data.get('error', 'Unknown error')}")
            print(f"   📝 Type: {error_data.get('type', 'Unknown')}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ User authentication test failed: {e}")
    
    # Test 4: Email Search (requires authentication)
    print("\n4. Testing email search...")
    try:
        test_data = {
            "employeeName": "Test Employee",
            "count": 5
        }
        response = requests.post(
            f"{base_url}/api/emails/search", 
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        if response.status_code == 200:
            email_data = response.json()
            print("   ✅ Email search successful")
            print(f"   📧 Found {len(email_data.get('emails', []))} emails")
        else:
            print(f"   ⚠️  Email search failed: {response.status_code}")
            print("   💡 This is expected if you haven't authenticated yet")
            error_data = response.json()
            print(f"   📝 Details: {error_data.get('error', 'Unknown error')}")
            print(f"   📝 Type: {error_data.get('type', 'Unknown')}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Email search test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("   - If health check passes, the service is running correctly")
    print("   - Debug auth shows detailed authentication status")
    print("   - Authentication failures are normal before first login")
    print("   - Run the email service and authenticate to enable full functionality")
    
    return True

if __name__ == "__main__":
    test_email_service() 