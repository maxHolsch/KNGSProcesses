#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_service_sync import GraphSync, init_graph
import configparser

def test_flask_auth():
    """Test authentication using the same setup as the Flask service"""
    print("🧪 Testing Flask Service Authentication...")
    print("=" * 50)
    
    try:
        # Step 1: Initialize exactly like the Flask service does
        print("1. Initializing Graph client (Flask service style)...")
        config = configparser.ConfigParser()
        config.read(['config.cfg', 'config.dev.cfg'])
        
        if 'azure' not in config:
            print("   ❌ No azure section found in config")
            return False
            
        azure_settings = config['azure']
        print(f"   ✅ Client ID: {azure_settings['clientId']}")
        print(f"   ✅ Tenant ID: {azure_settings['tenantId']}")
        print(f"   ✅ Scopes: {azure_settings['graphUserScopes']}")
        
        # Step 2: Create GraphSync instance
        print("\n2. Creating GraphSync instance...")
        graph_client = GraphSync(azure_settings)
        print("   ✅ GraphSync instance created")
        
        # Step 3: Test token acquisition
        print("\n3. Testing token acquisition...")
        try:
            token = graph_client.get_user_token()
            print("   ✅ Token acquired successfully")
            print(f"   📝 Token preview: {token[:50]}...")
        except Exception as e:
            print(f"   ❌ Token acquisition failed: {e}")
            return False
        
        # Step 4: Test user info retrieval
        print("\n4. Testing user info retrieval...")
        try:
            user = graph_client.get_user()
            print("   ✅ User info retrieved successfully")
            print(f"   👤 Display Name: {user.display_name}")
            print(f"   📧 Email: {user.mail or user.user_principal_name}")
        except Exception as e:
            print(f"   ❌ User info retrieval failed: {e}")
            print(f"   📝 Error type: {type(e).__name__}")
            return False
        
        # Step 5: Test email search
        print("\n5. Testing email search...")
        try:
            messages = graph_client.search_emails_by_employee("test", 5)
            email_count = len(messages.value) if messages and messages.value else 0
            print(f"   ✅ Email search completed successfully")
            print(f"   📧 Found {email_count} emails for 'test'")
        except Exception as e:
            print(f"   ❌ Email search failed: {e}")
            print(f"   📝 Error type: {type(e).__name__}")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 Flask service authentication test completed successfully!")
        print("   The authentication should work in the Flask service now.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print(f"📝 Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    try:
        test_flask_auth()
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print(f"📝 Error type: {type(e).__name__}") 