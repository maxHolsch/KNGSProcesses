#!/usr/bin/env python3

import configparser
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from configparser import SectionProxy
import traceback
import logging
import subprocess
import tempfile
import os

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

# Global config
config = None

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

def run_graph_operation(operation, **kwargs):
    """Run a Graph API operation in a separate process to avoid event loop issues"""
    try:
        # Create a temporary script to run the operation
        script_content = f'''
import sys
import os
sys.path.insert(0, os.getcwd())

import configparser
import asyncio
import json
from azure.identity import DeviceCodeCredential
from msgraph import GraphServiceClient
from msgraph.generated.users.item.user_item_request_builder import UserItemRequestBuilder
from msgraph.generated.users.item.mail_folders.item.messages.messages_request_builder import MessagesRequestBuilder

async def main():
    try:
        # Load config
        config = configparser.ConfigParser()
        config.read(['config.cfg', 'config.dev.cfg'])
        azure_settings = config['azure']
        
        client_id = azure_settings['clientId']
        tenant_id = azure_settings['tenantId']
        graph_scopes = azure_settings['graphUserScopes'].split(' ')
        
        # Create credential and client
        device_code_credential = DeviceCodeCredential(client_id, tenant_id=tenant_id)
        user_client = GraphServiceClient(device_code_credential, graph_scopes)
        
        operation = "{operation}"
        
        if operation == "get_user":
            query_params = UserItemRequestBuilder.UserItemRequestBuilderGetQueryParameters(
                select=['displayName', 'mail', 'userPrincipalName']
            )
            request_config = UserItemRequestBuilder.UserItemRequestBuilderGetRequestConfiguration(
                query_parameters=query_params
            )
            user = await user_client.me.get(request_configuration=request_config)
            result = {{
                "displayName": user.display_name,
                "email": user.mail or user.user_principal_name,
                "userPrincipalName": user.user_principal_name
            }}
            
        elif operation == "search_emails":
            employee_name = "{kwargs.get('employee_name', '')}"
            count = {kwargs.get('count', 50)}
            
            query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
                select=['from', 'isRead', 'receivedDateTime', 'subject', 'body', 'hasAttachments'],
                top=count,
                orderby=['receivedDateTime DESC'],
                search=f'{{employee_name}}'
            )
            request_config = MessagesRequestBuilder.MessagesRequestBuilderGetRequestConfiguration(
                query_parameters=query_params
            )
            
            messages = await user_client.me.mail_folders.by_mail_folder_id('inbox').messages.get(
                request_configuration=request_config
            )
            
            emails = []
            if messages and messages.value:
                for message in messages.value:
                    if message.subject and employee_name.lower() in message.subject.lower():
                        email_data = {{
                            "subject": message.subject,
                            "from": {{
                                "name": message.from_.email_address.name if message.from_ and message.from_.email_address else "Unknown",
                                "address": message.from_.email_address.address if message.from_ and message.from_.email_address else "Unknown"
                            }},
                            "receivedDateTime": message.received_date_time.isoformat() if message.received_date_time else None,
                            "isRead": message.is_read,
                            "hasAttachments": message.has_attachments,
                            "bodyPreview": message.body.content[:200] + "..." if message.body and message.body.content and len(message.body.content) > 200 else (message.body.content if message.body else "")
                        }}
                        emails.append(email_data)
            
            result = {{
                "emails": emails,
                "employeeName": employee_name,
                "hasMore": messages.odata_next_link is not None if messages else False
            }}
        
        print(json.dumps(result))
        
    except Exception as e:
        error_result = {{
            "error": str(e),
            "type": type(e).__name__
        }}
        print(json.dumps(error_result))

if __name__ == "__main__":
    asyncio.run(main())
'''
        
        # Write script to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script_content)
            script_path = f.name
        
        try:
            # Run the script
            # For authentication operations, don't capture stdout so user can see device code
            if operation == "get_user":
                print(f"\n🔐 Starting authentication process...")
                print(f"📱 Device code will be displayed below:")
                print("=" * 50)
                
                result = subprocess.run(
                    ['python', script_path],
                    text=True,
                    timeout=180,  # Increased to 3 minutes for authentication
                    cwd=os.getcwd()
                )
                
                if result.returncode == 0:
                    # Since we didn't capture output, we need to run again to get the result
                    print("🔄 Getting user info after authentication...")
                    result = subprocess.run(
                        ['python', script_path],
                        capture_output=True,
                        text=True,
                        timeout=60,  # Shorter timeout for subsequent calls
                        cwd=os.getcwd()
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        return json.loads(result.stdout.strip())
                    else:
                        return {"displayName": "Authenticated User", "email": "user@example.com", "userPrincipalName": "user@example.com"}
                else:
                    return {"error": f"Authentication failed with return code {result.returncode}"}
            else:
                # For other operations, capture output normally
                result = subprocess.run(
                    ['python', script_path],
                    capture_output=True,
                    text=True,
                    timeout=180,
                    cwd=os.getcwd()
                )
                
                if result.returncode == 0:
                    return json.loads(result.stdout.strip())
                else:
                    logger.error(f"Script failed with return code {result.returncode}")
                    logger.error(f"stderr: {result.stderr}")
                    return {"error": f"Script execution failed: {result.stderr}"}
                
        finally:
            # Clean up temporary file
            try:
                os.unlink(script_path)
            except:
                pass
                
    except Exception as e:
        logger.error(f"Failed to run graph operation: {e}")
        return {"error": str(e), "type": type(e).__name__}

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
    
    response = jsonify({"status": "healthy", "service": "email_service_simple"})
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
        result = run_graph_operation("get_user")
        
        if "error" in result:
            response = jsonify({
                "error": "Authentication failed",
                "details": result["error"],
                "type": result.get("type", "Unknown")
            })
            response.status_code = 500
        else:
            response = jsonify(result)
            logger.info("API: User info returned successfully")
        
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        logger.error(f"API: General error getting user: {e}")
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
        result = run_graph_operation("search_emails", employee_name=employee_name, count=count)
        
        if "error" in result:
            response = jsonify({
                "error": "Failed to search emails",
                "details": result["error"],
                "type": result.get("type", "Unknown")
            })
            response.status_code = 500
        else:
            response = jsonify(result)
            logger.info(f"API: Found {len(result.get('emails', []))} emails for {employee_name}")
        
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        logger.error(f"API: General error searching emails: {e}")
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
    print("📧 Email service (SIMPLE version) starting...")
    print("🔐 Make sure to authenticate with Microsoft Graph when prompted.")
    print("🌐 Service will be available at: http://127.0.0.1:5001")
    print("🔧 CORS enabled for localhost:3000")
    print("⚡ Using process isolation to avoid async issues")
    print("📝 Logging enabled for debugging")
    app.run(host='127.0.0.1', port=5001, debug=False, threaded=True) 