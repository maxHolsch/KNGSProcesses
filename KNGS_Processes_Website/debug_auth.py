#!/usr/bin/env python3

import configparser
import asyncio
from azure.identity import DeviceCodeCredential
from msgraph import GraphServiceClient
from msgraph.generated.users.item.user_item_request_builder import UserItemRequestBuilder
from msgraph.generated.models.o_data_errors.o_data_error import ODataError

def debug_authentication():
    """Debug the authentication process step by step"""
    print("🔍 Authentication Debug Tool")
    print("=" * 50)
    
    # Step 1: Load configuration
    print("1. Loading configuration...")
    try:
        config = configparser.ConfigParser()
        config.read(['config.cfg', 'config.dev.cfg'])
        
        if 'azure' not in config:
            print("   ❌ No azure section found in config")
            return False
            
        azure_settings = config['azure']
        client_id = azure_settings['clientId']
        tenant_id = azure_settings['tenantId']
        graph_scopes = azure_settings['graphUserScopes'].split(' ')
        
        print(f"   ✅ Client ID: {client_id}")
        print(f"   ✅ Tenant ID: {tenant_id}")
        print(f"   ✅ Scopes: {graph_scopes}")
        
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
        return False
    
    # Step 2: Create credentials
    print("\n2. Creating device code credential...")
    try:
        device_code_credential = DeviceCodeCredential(client_id, tenant_id=tenant_id)
        print("   ✅ Device code credential created")
    except Exception as e:
        print(f"   ❌ Credential creation error: {e}")
        return False
    
    # Step 3: Test token acquisition
    print("\n3. Testing token acquisition...")
    try:
        print("   🔐 Attempting to get access token...")
        access_token = device_code_credential.get_token(' '.join(graph_scopes))
        print(f"   ✅ Token acquired successfully")
        print(f"   📝 Token expires at: {access_token.expires_on}")
        print(f"   📝 Token preview: {access_token.token[:50]}...")
    except Exception as e:
        print(f"   ❌ Token acquisition error: {e}")
        print("   💡 You may need to authenticate again")
        return False
    
    # Step 4: Create Graph client
    print("\n4. Creating Graph service client...")
    try:
        user_client = GraphServiceClient(device_code_credential, graph_scopes)
        print("   ✅ Graph service client created")
    except Exception as e:
        print(f"   ❌ Graph client creation error: {e}")
        return False
    
    # Step 5: Test user info retrieval
    print("\n5. Testing user info retrieval...")
    try:
        query_params = UserItemRequestBuilder.UserItemRequestBuilderGetQueryParameters(
            select=['displayName', 'mail', 'userPrincipalName']
        )
        request_config = UserItemRequestBuilder.UserItemRequestBuilderGetRequestConfiguration(
            query_parameters=query_params
        )
        
        print("   🔄 Making Graph API call...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            user = loop.run_until_complete(user_client.me.get(request_configuration=request_config))
            print("   ✅ User info retrieved successfully")
            print(f"   👤 Display Name: {user.display_name}")
            print(f"   📧 Email: {user.mail or user.user_principal_name}")
            print(f"   🆔 User Principal Name: {user.user_principal_name}")
        finally:
            loop.close()
            
    except ODataError as e:
        print(f"   ❌ Graph API OData error: {e}")
        if hasattr(e, 'error') and e.error:
            print(f"   📝 Error code: {e.error.code}")
            print(f"   📝 Error message: {e.error.message}")
        return False
    except Exception as e:
        print(f"   ❌ Graph API error: {e}")
        print(f"   📝 Error type: {type(e).__name__}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Authentication debug completed successfully!")
    print("   The authentication is working properly.")
    print("   If the Flask service still fails, there may be an issue with the service setup.")
    
    return True

if __name__ == "__main__":
    try:
        debug_authentication()
    except KeyboardInterrupt:
        print("\n👋 Debug interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print(f"📝 Error type: {type(e).__name__}") 