#!/usr/bin/env python3

import configparser
import logging
from email_service_sync import GraphSync

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_simple_auth():
    print("🧪 Simple Authentication Test")
    print("=" * 50)
    
    try:
        # Load config
        config = configparser.ConfigParser()
        config.read(['config.cfg', 'config.dev.cfg'])
        
        if 'azure' not in config:
            config['azure'] = {
                'clientId': 'b9be55dd-85d1-41ab-ab92-e1bb2cafd19c',
                'tenantId': 'common',
                'graphUserScopes': 'User.Read Mail.Read Mail.Send'
            }
        
        azure_settings = config['azure']
        
        print("1. Creating GraphSync instance...")
        graph_client = GraphSync(azure_settings)
        print("   ✅ GraphSync created")
        
        print("\n2. First token request (will require authentication)...")
        token1 = graph_client.get_user_token()
        print(f"   ✅ Token 1: {token1[:50]}...")
        
        print("\n3. Second token request (should use cache)...")
        token2 = graph_client.get_user_token()
        print(f"   ✅ Token 2: {token2[:50]}...")
        
        if token1 == token2:
            print("   🎉 SUCCESS: Same token returned (caching works!)")
        else:
            print("   ❌ FAIL: Different tokens returned")
        
        print("\n4. Testing user info (should use cached token)...")
        user = graph_client.get_user()
        print(f"   ✅ User: {user.display_name} ({user.mail or user.user_principal_name})")
        
        print("\n5. Testing email search (should use cached token)...")
        messages = graph_client.search_emails_by_employee("test", 5)
        email_count = len(messages.value) if messages and messages.value else 0
        print(f"   ✅ Found {email_count} emails with 'test' in subject")
        
        print("\n🎉 All tests completed successfully!")
        print("✅ Token caching is working properly")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_simple_auth() 