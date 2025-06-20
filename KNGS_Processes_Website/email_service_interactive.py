#!/usr/bin/env python3

import configparser
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
import traceback
import logging
import asyncio
import threading
from azure.identity import DeviceCodeCredential
from msgraph import GraphServiceClient
from msgraph.generated.users.item.user_item_request_builder import UserItemRequestBuilder
from msgraph.generated.users.item.mail_folders.item.messages.messages_request_builder import MessagesRequestBuilder
import time
import concurrent.futures

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app setup
app = Flask(__name__)

# Configure CORS with specific settings
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Global variables
config = None
device_code_credential = None
user_client = None
authenticated = False
current_device_code = None
device_code_url = None
last_successful_auth = None

def device_code_callback(verification_uri, user_code, expires_in):
    """Callback function to capture device code information"""
    global current_device_code, device_code_url
    current_device_code = user_code
    device_code_url = verification_uri
    
    print(f"\n🔐 DEVICE CODE AUTHENTICATION REQUIRED")
    print(f"📱 Please go to: {verification_uri}")
    print(f"🔑 Enter this code: {user_code}")
    print(f"⏰ Code expires in {expires_in} seconds")
    print(f"💡 The code is also available in the Electron app modal")
    
    logger.info(f"Device code generated: {user_code}")
    logger.info(f"Verification URI: {verification_uri}")

def init_config():
    global config
    try:
        logger.info("Loading configuration...")
        config = configparser.ConfigParser()
        config.read(['config.cfg', 'config.dev.cfg'])
        
        if 'azure' not in config:
            logger.warning("No azure config found, creating default...")
            config['azure'] = {
                'clientId': 'b9be55dd-85d1-41ab-ab92-e1bb2cafd19c',
                'tenantId': 'common',
                'graphUserScopes': 'User.Read Mail.Read Mail.Send'
            }
            with open('config.cfg', 'w') as configfile:
                config.write(configfile)
        
        logger.info("Configuration loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise

def init_graph_client():
    global device_code_credential, user_client, authenticated
    try:
        azure_settings = config['azure']
        client_id = azure_settings['clientId']
        tenant_id = azure_settings['tenantId']
        graph_scopes = azure_settings['graphUserScopes'].split(' ')
        
        print("\n🔐 Initializing Microsoft Graph authentication...")
        print("📱 Device code authentication will be shown when needed")
        
        # Create device code credential with callback
        device_code_credential = DeviceCodeCredential(
            client_id, 
            tenant_id=tenant_id,
            prompt_callback=device_code_callback
        )
        user_client = GraphServiceClient(device_code_credential, graph_scopes)
        
        logger.info("Graph client initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Graph client: {e}")
        return False

def check_authentication_status():
    """Check if user is already authenticated by trying a simple API call"""
    global authenticated, last_successful_auth
    try:
        # If we authenticated recently (within 30 minutes), assume still valid
        if last_successful_auth and (time.time() - last_successful_auth) < 1800:
            logger.info("Using recent authentication (within 30 minutes)")
            authenticated = True
            return True
            
        # Try a simple API call to check if we're authenticated
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Quick test call
            query_params = UserItemRequestBuilder.UserItemRequestBuilderGetQueryParameters(
                select=['displayName']
            )
            request_config = UserItemRequestBuilder.UserItemRequestBuilderGetRequestConfiguration(
                query_parameters=query_params
            )
            user = loop.run_until_complete(user_client.me.get(request_configuration=request_config))
            
            if user and user.display_name:
                authenticated = True
                last_successful_auth = time.time()
                logger.info(f"Already authenticated as: {user.display_name}")
                return True
        except Exception as e:
            logger.info(f"Not authenticated yet: {e}")
            authenticated = False
            return False
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Error checking authentication: {e}")
        authenticated = False
        return False

async def get_user_async():
    """Get user information asynchronously"""
    global authenticated, last_successful_auth
    
    query_params = UserItemRequestBuilder.UserItemRequestBuilderGetQueryParameters(
        select=['displayName', 'mail', 'userPrincipalName']
    )
    request_config = UserItemRequestBuilder.UserItemRequestBuilderGetRequestConfiguration(
        query_parameters=query_params
    )
    user = await user_client.me.get(request_configuration=request_config)
    
    # Mark as successfully authenticated
    authenticated = True
    last_successful_auth = time.time()
    
    return {
        "displayName": user.display_name,
        "email": user.mail or user.user_principal_name,
        "userPrincipalName": user.user_principal_name
    }

async def search_emails_async(employee_name, count=50):
    """Search for emails asynchronously"""
    global authenticated, last_successful_auth
    
    try:
        logger.info(f"Starting email search for: {employee_name}")
        
        query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
            select=['from', 'isRead', 'receivedDateTime', 'subject', 'body', 'hasAttachments'],
            top=count,
            orderby=['receivedDateTime DESC'],
            search=f'{employee_name}'  # Simplified search - just search for the name
        )
        request_config = MessagesRequestBuilder.MessagesRequestBuilderGetRequestConfiguration(
            query_parameters=query_params
        )
        
        logger.info("Making Graph API request for messages...")
        messages = await user_client.me.mail_folders.by_mail_folder_id('inbox').messages.get(
            request_configuration=request_config
        )
        
        # Mark as successfully authenticated
        authenticated = True
        last_successful_auth = time.time()
        logger.info(f"Graph API request successful, processing {len(messages.value) if messages and messages.value else 0} messages")
        
        emails = []
        if messages and messages.value:
            for message in messages.value:
                # Filter results to only include emails where the employee name appears in the subject
                if message.subject and employee_name.lower() in message.subject.lower():
                    email_data = {
                        "subject": message.subject,
                        "from": {
                            "name": message.from_.email_address.name if message.from_ and message.from_.email_address else "Unknown",
                            "address": message.from_.email_address.address if message.from_ and message.from_.email_address else "Unknown"
                        },
                        "receivedDateTime": message.received_date_time.isoformat() if message.received_date_time else None,
                        "isRead": message.is_read,
                        "hasAttachments": message.has_attachments,
                        "bodyPreview": message.body.content[:200] + "..." if message.body and message.body.content and len(message.body.content) > 200 else (message.body.content if message.body else "")
                    }
                    emails.append(email_data)
        
        logger.info(f"Email search completed: found {len(emails)} matching emails")
        return {
            "emails": emails,
            "employeeName": employee_name,
            "hasMore": messages.odata_next_link is not None if messages else False
        }
        
    except Exception as e:
        logger.error(f"Error in search_emails_async: {type(e).__name__}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

def run_in_thread(coro):
    """Run an async coroutine in a separate thread with its own event loop"""
    def run_in_new_loop():
        # Always create a fresh event loop for each operation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(coro)
            return result
        except Exception as e:
            logger.error(f"Error in async operation: {e}")
            raise
        finally:
            # Clean up the loop properly
            try:
                # Cancel any remaining tasks
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
                
                # Wait for tasks to complete cancellation
                if pending:
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                
                # Close the loop
                loop.close()
            except Exception as cleanup_error:
                logger.warning(f"Error during loop cleanup: {cleanup_error}")
    
    # Use a thread pool to run the async operation
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(run_in_new_loop)
        try:
            return future.result(timeout=180)
        except concurrent.futures.TimeoutError:
            logger.error("Operation timed out after 180 seconds")
            raise Exception("Operation timed out - please try again")
        except Exception as e:
            logger.error(f"Thread execution failed: {e}")
            raise

@app.route('/api/auth/status', methods=['GET', 'OPTIONS'])
def get_auth_status():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
    
    try:
        global authenticated, last_successful_auth
        
        # Check current authentication status
        is_authenticated = check_authentication_status()
        
        response_data = {
            "authenticated": is_authenticated,
            "lastAuthTime": last_successful_auth,
            "needsAuth": not is_authenticated
        }
        
        response = jsonify(response_data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        logger.info(f"Auth status check: authenticated={is_authenticated}")
        return response
        
    except Exception as e:
        logger.error(f"API: Error checking auth status: {e}")
        response = jsonify({
            "authenticated": False,
            "lastAuthTime": None,
            "needsAuth": True,
            "error": str(e)
        })
        response.status_code = 500
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@app.route('/api/auth/device-code', methods=['GET', 'OPTIONS'])
def get_device_code():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
    
    try:
        global current_device_code, device_code_url
        
        response_data = {
            "deviceCode": current_device_code,
            "deviceCodeUrl": device_code_url or "https://microsoft.com/devicelogin",
            "hasActiveCode": current_device_code is not None
        }
        
        response = jsonify(response_data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        logger.info(f"Device code requested: {current_device_code is not None}")
        return response
        
    except Exception as e:
        logger.error(f"API: Error getting device code: {e}")
        response = jsonify({
            "error": "Failed to get device code info",
            "details": str(e),
            "deviceCode": None,
            "deviceCodeUrl": "https://microsoft.com/devicelogin",
            "hasActiveCode": False
        })
        response.status_code = 500
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
    
    response = jsonify({"status": "healthy", "service": "email_service_interactive"})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/auth/user', methods=['GET', 'OPTIONS'])
def get_current_user():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
    
    try:
        logger.info("API: Getting current user...")
        print("\n🔐 Authenticating with Microsoft Graph...")
        print("📱 Please check the terminal for device code instructions")
        
        result = run_in_thread(get_user_async())
        
        response = jsonify(result)
        response.headers.add('Access-Control-Allow-Origin', '*')
        logger.info("API: User info returned successfully")
        return response
        
    except Exception as e:
        logger.error(f"API: Error getting user: {e}")
        response = jsonify({
            "error": "Failed to get user info",
            "details": str(e),
            "type": type(e).__name__
        })
        response.status_code = 500
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@app.route('/api/emails/search', methods=['POST', 'OPTIONS'])
def search_emails():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
    
    try:
        data = request.get_json()
        employee_name = data.get('employeeName', '')
        count = data.get('count', 50)
        count = min(count, 100)  # Limit to 100 emails max
        
        if not employee_name:
            response = jsonify({"error": "Employee name is required"})
            response.status_code = 400
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        
        logger.info(f"API: Searching emails for employee: {employee_name}")
        result = run_in_thread(search_emails_async(employee_name, count))
        
        response = jsonify(result)
        response.headers.add('Access-Control-Allow-Origin', '*')
        logger.info(f"API: Found {len(result.get('emails', []))} emails for {employee_name}")
        return response
        
    except Exception as e:
        logger.error(f"API: Error searching emails: {e}")
        response = jsonify({
            "error": "Failed to search emails",
            "details": str(e),
            "type": type(e).__name__
        })
        response.status_code = 500
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

if __name__ == '__main__':
    init_config()
    if init_graph_client():
        print("📧 Email service (INTERACTIVE version) starting...")
        print("🔐 Device code authentication will be shown in this terminal")
        print("🌐 Service will be available at: http://127.0.0.1:5002")
        print("🔧 CORS enabled for localhost:3000")
        print("⚡ Using thread isolation for async operations")
        print("📝 Logging enabled for debugging")
        app.run(host='127.0.0.1', port=5002, debug=False, threaded=True)
    else:
        print("❌ Failed to initialize Graph client") 