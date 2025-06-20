#!/usr/bin/env python3

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import asyncio
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
import threading
from functools import wraps
import concurrent.futures

class Graph:
    settings: SectionProxy
    device_code_credential: DeviceCodeCredential
    user_client: GraphServiceClient

    def __init__(self, config: SectionProxy):
        self.settings = config
        client_id = self.settings['clientId']
        tenant_id = self.settings['tenantId']
        graph_scopes = self.settings['graphUserScopes'].split(' ')

        self.device_code_credential = DeviceCodeCredential(client_id, tenant_id = tenant_id)
        self.user_client = GraphServiceClient(self.device_code_credential, graph_scopes)

    async def get_user_token(self):
        graph_scopes = self.settings['graphUserScopes']
        access_token = self.device_code_credential.get_token(graph_scopes)
        return access_token.token

    async def get_user(self):
        query_params = UserItemRequestBuilder.UserItemRequestBuilderGetQueryParameters(
            select=['displayName', 'mail', 'userPrincipalName']
        )

        request_config = UserItemRequestBuilder.UserItemRequestBuilderGetRequestConfiguration(
            query_parameters=query_params
        )

        user = await self.user_client.me.get(request_configuration=request_config)
        return user

    async def get_inbox(self, count=25):
        query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
            select=['from', 'isRead', 'receivedDateTime', 'subject', 'body', 'hasAttachments'],
            top=count,
            orderby=['receivedDateTime DESC']
        )
        request_config = MessagesRequestBuilder.MessagesRequestBuilderGetRequestConfiguration(
            query_parameters= query_params
        )

        messages = await self.user_client.me.mail_folders.by_mail_folder_id('inbox').messages.get(
                request_configuration=request_config)
        return messages

    async def search_emails_by_employee(self, employee_name, count=50):
        """Search for emails that have the employee's name in the subject line"""
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

        messages = await self.user_client.me.mail_folders.by_mail_folder_id('inbox').messages.get(
                request_configuration=request_config)
        return messages

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

# Global graph client and thread pool
graph_client = None
executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

def init_graph():
    global graph_client
    config = configparser.ConfigParser()
    config.read(['config.cfg', 'config.dev.cfg'])
    
    if 'azure' not in config:
        # Create default config if it doesn't exist
        config['azure'] = {
            'clientId': 'b9be55dd-85d1-41ab-ab92-e1bb2cafd19c',
            'tenantId': 'common',
            'graphUserScopes': 'User.Read Mail.Read Mail.Send'
        }
        with open('config.cfg', 'w') as configfile:
            config.write(configfile)
    
    azure_settings = config['azure']
    graph_client = Graph(azure_settings)

def run_async_in_thread(coro):
    """Run an async coroutine in a separate thread with its own event loop"""
    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    future = executor.submit(run_in_thread)
    return future.result(timeout=30)  # 30 second timeout

def async_route(f):
    """Decorator to handle async functions in Flask"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            coro = f(*args, **kwargs)
            return run_async_in_thread(coro)
        except concurrent.futures.TimeoutError:
            response = jsonify({"error": "Request timeout", "details": "The operation took too long to complete"})
            response.status_code = 504
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        except Exception as e:
            response = jsonify({"error": "Internal server error", "details": str(e)})
            response.status_code = 500
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
    return wrapper

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
    
    response = jsonify({"status": "healthy", "service": "email_service"})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/auth/user', methods=['GET', 'OPTIONS'])
@async_route
async def get_current_user():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
    
    try:
        user = await graph_client.get_user()
        response = jsonify({
            "displayName": user.display_name,
            "email": user.mail or user.user_principal_name,
            "userPrincipalName": user.user_principal_name
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except ODataError as e:
        response = jsonify({
            "error": "Authentication failed",
            "details": str(e)
        })
        response.status_code = 401
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        response = jsonify({
            "error": "Failed to get user info",
            "details": str(e)
        })
        response.status_code = 500
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@app.route('/api/emails/recent', methods=['GET', 'OPTIONS'])
@async_route
async def get_recent_emails():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response
    
    try:
        count = request.args.get('count', 25, type=int)
        count = min(count, 100)  # Limit to 100 emails max
        
        message_page = await graph_client.get_inbox(count)
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
        return response
    
    except ODataError as e:
        response = jsonify({
            "error": "Failed to fetch emails",
            "details": str(e)
        })
        response.status_code = 401
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        response = jsonify({
            "error": "Failed to fetch emails",
            "details": str(e)
        })
        response.status_code = 500
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@app.route('/api/emails/search', methods=['POST', 'OPTIONS'])
@async_route
async def search_emails():
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
        
        message_page = await graph_client.search_emails_by_employee(employee_name, count)
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
        return response
    
    except ODataError as e:
        response = jsonify({
            "error": "Failed to search emails",
            "details": str(e)
        })
        response.status_code = 401
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        response = jsonify({
            "error": "Failed to search emails",
            "details": str(e)
        })
        response.status_code = 500
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

if __name__ == '__main__':
    init_graph()
    print("📧 Email service starting...")
    print("🔐 Make sure to authenticate with Microsoft Graph when prompted.")
    print("🌐 Service will be available at: http://127.0.0.1:5000")
    print("🔧 CORS enabled for localhost:3000")
    app.run(host='127.0.0.1', port=5000, debug=True, threaded=True) 