#!/usr/bin/env python3

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import configparser
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from configparser import SectionProxy
from azure.identity import DeviceCodeCredential
from msgraph import GraphServiceClient
from msgraph.generated.users.item.user_item_request_builder import UserItemRequestBuilder
from msgraph.generated.users.item.mail_folders.item.messages.messages_request_builder import (
    MessagesRequestBuilder)
from msgraph.generated.models.o_data_errors.o_data_error import ODataError
import traceback
import logging
from azure.core.credentials import AccessToken
from datetime import datetime, timezone
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CachedTokenCredential:
    """Custom credential that caches and reuses tokens"""
    
    def __init__(self, device_code_credential, scopes):
        self.device_code_credential = device_code_credential
        self.scopes = scopes
        self._cached_token = None
        self._token_expiry = None
    
    def get_token(self, *scopes, **kwargs):
        """Get token, using cache if available and not expired"""
        try:
            # Check if we have a valid cached token
            if self._cached_token and self._token_expiry:
                # Add 5 minute buffer before expiry
                buffer_time = 300  # 5 minutes in seconds
                current_time = time.time()
                
                if current_time < (self._token_expiry - buffer_time):
                    logger.info("Using cached token (not expired)")
                    return AccessToken(self._cached_token, int(self._token_expiry))
                else:
                    logger.info("Cached token expired, getting new token")
            
            # Get new token
            logger.info("Getting new token from device code credential")
            scope_str = ' '.join(self.scopes)
            access_token = self.device_code_credential.get_token(scope_str)
            
            # Cache the token
            self._cached_token = access_token.token
            self._token_expiry = access_token.expires_on
            
            logger.info("Token acquired and cached successfully")
            return access_token
            
        except Exception as e:
            logger.error(f"Token acquisition failed: {e}")
            raise

class GraphSync:
    settings: SectionProxy
    device_code_credential: DeviceCodeCredential
    user_client: GraphServiceClient
    cached_credential: CachedTokenCredential

    def __init__(self, config: SectionProxy):
        self.settings = config
        client_id = self.settings['clientId']
        tenant_id = self.settings['tenantId']
        graph_scopes = self.settings['graphUserScopes'].split(' ')

        logger.info(f"Initializing Graph client with client_id: {client_id}, tenant_id: {tenant_id}")
        logger.info(f"Scopes: {graph_scopes}")
        
        self.device_code_credential = DeviceCodeCredential(client_id, tenant_id = tenant_id)
        self.cached_credential = CachedTokenCredential(self.device_code_credential, graph_scopes)
        self.user_client = GraphServiceClient(self.cached_credential, graph_scopes)

    def get_user_token(self):
        try:
            graph_scopes = self.settings['graphUserScopes'].split(' ')
            logger.info(f"Getting token for scopes: {graph_scopes}")
            access_token = self.cached_credential.get_token(' '.join(graph_scopes))
            logger.info("Token acquired successfully")
            return access_token.token
        except Exception as e:
            logger.error(f"Token acquisition failed: {e}")
            raise

    def get_user(self):
        try:
            logger.info("Getting user information...")
            query_params = UserItemRequestBuilder.UserItemRequestBuilderGetQueryParameters(
                select=['displayName', 'mail', 'userPrincipalName']
            )

            request_config = UserItemRequestBuilder.UserItemRequestBuilderGetRequestConfiguration(
                query_parameters=query_params
            )

            # Use synchronous call with proper event loop management
            import asyncio
            import threading
            
            # Check if we're in the main thread and if there's already a loop
            current_thread = threading.current_thread()
            is_main_thread = isinstance(current_thread, threading._MainThread)
            
            try:
                # Try to get the current event loop
                existing_loop = asyncio.get_running_loop()
                logger.info("Found existing event loop, using thread executor")
                
                # Use thread executor to run in a separate thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(self._run_user_request, request_config)
                    user = future.result(timeout=30)
                    logger.info(f"User retrieved: {user.display_name}")
                    return user
                    
            except RuntimeError:
                # No running loop, safe to create new one
                logger.info("No existing event loop, creating new one")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    user = loop.run_until_complete(self.user_client.me.get(request_configuration=request_config))
                    logger.info(f"User retrieved: {user.display_name}")
                    return user
                finally:
                    loop.close()
                    if is_main_thread:
                        asyncio.set_event_loop(None)
                        
        except Exception as e:
            logger.error(f"Get user failed: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def _run_user_request(self, request_config):
        """Helper method to run user request in a separate thread"""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.user_client.me.get(request_configuration=request_config))
        finally:
            loop.close()

    def get_inbox(self, count=25):
        try:
            logger.info(f"Getting inbox with {count} messages...")
            query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
                select=['from', 'isRead', 'receivedDateTime', 'subject', 'body', 'hasAttachments'],
                top=count,
                orderby=['receivedDateTime DESC']
            )
            request_config = MessagesRequestBuilder.MessagesRequestBuilderGetRequestConfiguration(
                query_parameters= query_params
            )

            # Use synchronous call with proper event loop management
            import asyncio
            import threading
            
            current_thread = threading.current_thread()
            is_main_thread = isinstance(current_thread, threading._MainThread)
            
            try:
                existing_loop = asyncio.get_running_loop()
                logger.info("Found existing event loop, using thread executor")
                
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(self._run_inbox_request, request_config)
                    messages = future.result(timeout=30)
                    logger.info(f"Retrieved {len(messages.value) if messages and messages.value else 0} messages")
                    return messages
                    
            except RuntimeError:
                logger.info("No existing event loop, creating new one")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    messages = loop.run_until_complete(
                        self.user_client.me.mail_folders.by_mail_folder_id('inbox').messages.get(
                            request_configuration=request_config)
                    )
                    logger.info(f"Retrieved {len(messages.value) if messages and messages.value else 0} messages")
                    return messages
                finally:
                    loop.close()
                    if is_main_thread:
                        asyncio.set_event_loop(None)
                        
        except Exception as e:
            logger.error(f"Get inbox failed: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            raise

    def _run_inbox_request(self, request_config):
        """Helper method to run inbox request in a separate thread"""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.user_client.me.mail_folders.by_mail_folder_id('inbox').messages.get(
                    request_configuration=request_config)
            )
        finally:
            loop.close()

    def search_emails_by_employee(self, employee_name, count=50):
        """Search for emails that have the employee's name in the subject line"""
        try:
            logger.info(f"Searching emails with '{employee_name}' in subject line...")
            query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
                select=['from', 'isRead', 'receivedDateTime', 'subject', 'body', 'hasAttachments', 'toRecipients', 'ccRecipients'],
                top=count,
                orderby=['receivedDateTime DESC'],
                # Search specifically in subject line for employee name
                search=f'subject:"{employee_name}"'
            )
            request_config = MessagesRequestBuilder.MessagesRequestBuilderGetRequestConfiguration(
                query_parameters= query_params
            )

            # Use synchronous call with proper event loop management
            import asyncio
            import threading
            
            current_thread = threading.current_thread()
            is_main_thread = isinstance(current_thread, threading._MainThread)
            
            try:
                existing_loop = asyncio.get_running_loop()
                logger.info("Found existing event loop, using thread executor")
                
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(self._run_search_request, request_config)
                    messages = future.result(timeout=30)
                    logger.info(f"Found {len(messages.value) if messages and messages.value else 0} emails with '{employee_name}' in subject for {employee_name}")
                    return messages
                    
            except RuntimeError:
                logger.info("No existing event loop, creating new one")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    messages = loop.run_until_complete(
                        self.user_client.me.mail_folders.by_mail_folder_id('inbox').messages.get(
                            request_configuration=request_config)
                    )
                    logger.info(f"Found {len(messages.value) if messages and messages.value else 0} emails with '{employee_name}' in subject for {employee_name}")
                    return messages
                finally:
                    loop.close()
                    if is_main_thread:
                        asyncio.set_event_loop(None)
                        
        except Exception as e:
            logger.error(f"Search emails failed: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            raise

    def _run_search_request(self, request_config):
        """Helper method to run search request in a separate thread"""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.user_client.me.mail_folders.by_mail_folder_id('inbox').messages.get(
                    request_configuration=request_config)
            )
        finally:
            loop.close()

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

# Global graph client
graph_client = None

def init_graph():
    global graph_client
    try:
        logger.info("Initializing Graph client...")
        config = configparser.ConfigParser()
        config.read(['config.cfg', 'config.dev.cfg'])
        
        if 'azure' not in config:
            logger.warning("No azure config found, creating default...")
            # Create default config if it doesn't exist
            config['azure'] = {
                'clientId': 'b9be55dd-85d1-41ab-ab92-e1bb2cafd19c',
                'tenantId': 'common',
                'graphUserScopes': 'User.Read Mail.Read Mail.Send'
            }
            with open('config.cfg', 'w') as configfile:
                config.write(configfile)
        
        azure_settings = config['azure']
        graph_client = GraphSync(azure_settings)
        logger.info("Graph client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Graph client: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
    
    response = jsonify({"status": "healthy", "service": "email_service_sync"})
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
        user = graph_client.get_user()
        response = jsonify({
            "displayName": user.display_name,
            "email": user.mail or user.user_principal_name,
            "userPrincipalName": user.user_principal_name
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        logger.info("API: User info returned successfully")
        return response
    except ODataError as e:
        logger.error(f"API: OData error getting user: {e}")
        error_details = str(e)
        if hasattr(e, 'error') and e.error:
            error_details = f"Code: {e.error.code}, Message: {e.error.message}"
        
        response = jsonify({
            "error": "Authentication failed",
            "details": error_details,
            "type": "ODataError"
        })
        response.status_code = 401
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        logger.error(f"API: General error getting user: {e}")
        logger.error(f"API: Error type: {type(e).__name__}")
        logger.error(f"API: Traceback: {traceback.format_exc()}")
        
        response = jsonify({
            "error": "Failed to get user info",
            "details": str(e),
            "type": type(e).__name__
        })
        response.status_code = 500
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@app.route('/api/emails/recent', methods=['GET', 'OPTIONS'])
def get_recent_emails():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
    
    try:
        count = request.args.get('count', 25, type=int)
        count = min(count, 100)  # Limit to 100 emails max
        
        logger.info(f"API: Getting {count} recent emails...")
        message_page = graph_client.get_inbox(count)
        emails = []
        
        if message_page and message_page.value:
            for message in message_page.value:
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
        
        response = jsonify({
            "emails": emails,
            "hasMore": message_page.odata_next_link is not None if message_page else False
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        logger.info(f"API: Returned {len(emails)} recent emails")
        return response
    
    except ODataError as e:
        logger.error(f"API: OData error getting recent emails: {e}")
        response = jsonify({
            "error": "Failed to fetch emails",
            "details": str(e),
            "type": "ODataError"
        })
        response.status_code = 401
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        logger.error(f"API: General error getting recent emails: {e}")
        response = jsonify({
            "error": "Failed to fetch emails",
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
        message_page = graph_client.search_emails_by_employee(employee_name, count)
        emails = []
        
        if message_page and message_page.value:
            for message in message_page.value:
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
        
        response = jsonify({
            "emails": emails,
            "employeeName": employee_name,
            "hasMore": message_page.odata_next_link is not None if message_page else False
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        logger.info(f"API: Found {len(emails)} emails for {employee_name}")
        return response
    
    except ODataError as e:
        logger.error(f"API: OData error searching emails: {e}")
        response = jsonify({
            "error": "Failed to search emails",
            "details": str(e),
            "type": "ODataError"
        })
        response.status_code = 401
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

@app.route('/api/debug/auth', methods=['GET', 'OPTIONS'])
def debug_auth():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
    
    try:
        logger.info("API: Debug auth - testing token acquisition...")
        
        # Test token acquisition
        try:
            token = graph_client.get_user_token()
            token_preview = token[:50] + "..." if len(token) > 50 else token
            logger.info("API: Debug auth - token acquired successfully")
        except Exception as token_error:
            logger.error(f"API: Debug auth - token acquisition failed: {token_error}")
            response = jsonify({
                "step": "token_acquisition",
                "success": False,
                "error": str(token_error),
                "type": type(token_error).__name__
            })
            response.status_code = 500
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        
        # Test user info
        try:
            user = graph_client.get_user()
            logger.info("API: Debug auth - user info retrieved successfully")
            
            response = jsonify({
                "step": "complete",
                "success": True,
                "token_preview": token_preview,
                "user": {
                    "displayName": user.display_name,
                    "email": user.mail or user.user_principal_name,
                    "userPrincipalName": user.user_principal_name
                }
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
            
        except Exception as user_error:
            logger.error(f"API: Debug auth - user info failed: {user_error}")
            response = jsonify({
                "step": "user_info",
                "success": False,
                "token_preview": token_preview,
                "error": str(user_error),
                "type": type(user_error).__name__
            })
            response.status_code = 500
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
            
    except Exception as e:
        logger.error(f"API: Debug auth - general error: {e}")
        response = jsonify({
            "step": "initialization",
            "success": False,
            "error": str(e),
            "type": type(e).__name__
        })
        response.status_code = 500
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

if __name__ == '__main__':
    init_graph()
    print("📧 Email service (SYNC version) starting...")
    print("🔐 Make sure to authenticate with Microsoft Graph when prompted.")
    print("🌐 Service will be available at: http://127.0.0.1:5000")
    print("🔧 CORS enabled for localhost:3000")
    print("⚡ Using synchronous version to avoid async timeout issues")
    print("📝 Logging enabled for debugging")
    app.run(host='127.0.0.1', port=5000, debug=True, threaded=True) 