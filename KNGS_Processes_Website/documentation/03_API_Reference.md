# KNGS Email Progress Checker - API Reference

## Overview

The KNGS Email Progress Checker provides a RESTful API backend built with Python Flask that handles authentication, email search, and data processing. This document serves as a comprehensive reference for all API endpoints, request/response formats, and integration patterns.

## Base Configuration

### Server Information
- **Base URL**: `http://127.0.0.1:5002`
- **Protocol**: HTTP (development), HTTPS (production)
- **Content-Type**: `application/json`
- **CORS**: Enabled for `http://localhost:3000` and `http://127.0.0.1:3000`

### Global Headers
```http
Content-Type: application/json
Accept: application/json
```

## Authentication Endpoints

### Health Check

#### `GET /api/health`

**Description**: Verify backend service availability and status.

**Request**:
```http
GET /api/health HTTP/1.1
Host: 127.0.0.1:5002
```

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-20T19:42:00Z",
  "service": "KNGS Email Progress Checker"
}
```

**Status Codes**:
- `200 OK`: Service is healthy and operational
- `500 Internal Server Error`: Service is experiencing issues

---

### Authentication Status

#### `GET /api/auth/status`

**Description**: Check current authentication state and user information.

**Request**:
```http
GET /api/auth/status HTTP/1.1
Host: 127.0.0.1:5002
```

**Response (Authenticated)**:
```json
{
  "authenticated": true,
  "user": {
    "displayName": "John Doe",
    "email": "john.doe@example.com",
    "userPrincipalName": "john.doe@example.com"
  },
  "lastAuthenticated": "2025-01-20T19:30:00Z"
}
```

**Response (Not Authenticated)**:
```json
{
  "authenticated": false,
  "user": null,
  "message": "Authentication required"
}
```

**Status Codes**:
- `200 OK`: Status retrieved successfully
- `500 Internal Server Error`: Authentication check failed

---

### Device Code Retrieval

#### `GET /api/auth/device-code`

**Description**: Retrieve the current device code for OAuth authentication.

**Request**:
```http
GET /api/auth/device-code HTTP/1.1
Host: 127.0.0.1:5002
```

**Response (Device Code Available)**:
```json
{
  "deviceCode": "FC87NDD2E",
  "verificationUri": "https://microsoft.com/devicelogin",
  "requested": true,
  "expiresIn": 900,
  "interval": 5
}
```

**Response (No Device Code)**:
```json
{
  "deviceCode": null,
  "verificationUri": null,
  "requested": false,
  "message": "Device code not yet requested"
}
```

**Status Codes**:
- `200 OK`: Device code information retrieved
- `400 Bad Request`: Device code request failed
- `500 Internal Server Error`: Authentication service error

---

### User Information

#### `GET /api/auth/user`

**Description**: Retrieve detailed information about the authenticated user.

**Request**:
```http
GET /api/auth/user HTTP/1.1
Host: 127.0.0.1:5002
```

**Response (Success)**:
```json
{
  "displayName": "John Doe",
  "email": "john.doe@example.com",
  "userPrincipalName": "john.doe@example.com",
  "id": "12345678-1234-1234-1234-123456789012"
}
```

**Response (Not Authenticated)**:
```json
{
  "error": "Authentication required",
  "message": "Please authenticate with Microsoft Graph first",
  "authenticated": false
}
```

**Status Codes**:
- `200 OK`: User information retrieved successfully
- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Failed to retrieve user information

## Email Search Endpoints

### Email Search

#### `POST /api/emails/search`

**Description**: Search for emails related to a specific employee using Microsoft Graph API.

**Request**:
```http
POST /api/emails/search HTTP/1.1
Host: 127.0.0.1:5002
Content-Type: application/json

{
  "employeeName": "John Smith",
  "count": 50
}
```

**Request Body Parameters**:
- `employeeName` (string, required): Name of the employee to search for
- `count` (integer, optional): Maximum number of emails to return (default: 50, max: 100)

**Response (Success)**:
```json
{
  "emails": [
    {
      "subject": "Project Update - John Smith",
      "from": {
        "name": "Jane Manager",
        "email": "jane.manager@example.com"
      },
      "receivedDateTime": "2025-01-20T15:30:00Z",
      "isRead": true,
      "hasAttachments": false,
      "body": "Brief preview of email content...",
      "importance": "normal"
    },
    {
      "subject": "Weekly Report - John Smith Team",
      "from": {
        "name": "HR System",
        "email": "hr@example.com"
      },
      "receivedDateTime": "2025-01-19T09:15:00Z",
      "isRead": false,
      "hasAttachments": true,
      "body": "Another email preview...",
      "importance": "high"
    }
  ],
  "totalCount": 25,
  "searchQuery": "John Smith",
  "timestamp": "2025-01-20T19:42:00Z"
}
```

**Response (Not Authenticated)**:
```json
{
  "error": "Authentication required",
  "message": "Please authenticate with Microsoft Graph first",
  "authenticated": false
}
```

**Response (Search Error)**:
```json
{
  "error": "Search failed",
  "message": "Failed to search emails in Microsoft Graph",
  "details": "Specific error details here"
}
```

**Status Codes**:
- `200 OK`: Search completed successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Search operation failed

## Error Handling

### Standard Error Response Format

All API endpoints return errors in a consistent format:

```json
{
  "error": "Error Type",
  "message": "Human-readable error message",
  "details": "Additional technical details (optional)",
  "timestamp": "2025-01-20T19:42:00Z",
  "endpoint": "/api/emails/search"
}
```

### Common Error Types

#### Authentication Errors
```json
{
  "error": "AuthenticationRequired",
  "message": "Microsoft Graph authentication required",
  "authenticated": false
}
```

#### Rate Limiting Errors
```json
{
  "error": "RateLimitExceeded",
  "message": "Microsoft Graph API rate limit exceeded",
  "retryAfter": 60
}
```

#### Validation Errors
```json
{
  "error": "ValidationError",
  "message": "Invalid request parameters",
  "details": {
    "employeeName": "Field is required",
    "count": "Must be between 1 and 100"
  }
}
```

## Request/Response Examples

### Complete Authentication Flow

1. **Check Authentication Status**:
```bash
curl -X GET http://127.0.0.1:5002/api/auth/status
```

2. **Get Device Code (if not authenticated)**:
```bash
curl -X GET http://127.0.0.1:5002/api/auth/device-code
```

3. **Complete Authentication** (user action required)

4. **Verify Authentication**:
```bash
curl -X GET http://127.0.0.1:5002/api/auth/user
```

5. **Search Emails**:
```bash
curl -X POST http://127.0.0.1:5002/api/emails/search \
  -H "Content-Type: application/json" \
  -d '{"employeeName": "John Smith", "count": 25}'
```

### Batch Email Search

For searching multiple employees, make sequential requests:

```javascript
const employees = ["John Smith", "Jane Doe", "Bob Johnson"];
const searchResults = [];

for (const employee of employees) {
  const response = await fetch('/api/emails/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      employeeName: employee,
      count: 50
    })
  });
  
  const result = await response.json();
  searchResults.push({
    employee: employee,
    emails: result.emails,
    count: result.totalCount
  });
}
```

## Rate Limiting

### Microsoft Graph API Limits
- **Requests per second**: 10,000 per application
- **Requests per minute**: 600,000 per application
- **Concurrent requests**: 5 per user

### Application Rate Limiting
- **Email searches**: 60 requests per minute per user
- **Authentication checks**: 120 requests per minute per user
- **Device code requests**: 10 requests per minute per user

### Rate Limit Headers
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1642694400
```

## SDK Integration Examples

### Python Integration
```python
import requests
import json

class KNGSEmailClient:
    def __init__(self, base_url="http://127.0.0.1:5002"):
        self.base_url = base_url
        
    def check_health(self):
        response = requests.get(f"{self.base_url}/api/health")
        return response.json()
    
    def search_emails(self, employee_name, count=50):
        payload = {
            "employeeName": employee_name,
            "count": count
        }
        response = requests.post(
            f"{self.base_url}/api/emails/search",
            json=payload
        )
        return response.json()
    
    def get_auth_status(self):
        response = requests.get(f"{self.base_url}/api/auth/status")
        return response.json()
```

### JavaScript Integration
```javascript
class KNGSEmailClient {
  constructor(baseUrl = 'http://127.0.0.1:5002') {
    this.baseUrl = baseUrl;
  }
  
  async checkHealth() {
    const response = await fetch(`${this.baseUrl}/api/health`);
    return response.json();
  }
  
  async searchEmails(employeeName, count = 50) {
    const response = await fetch(`${this.baseUrl}/api/emails/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        employeeName: employeeName,
        count: count
      })
    });
    return response.json();
  }
  
  async getAuthStatus() {
    const response = await fetch(`${this.baseUrl}/api/auth/status`);
    return response.json();
  }
}
```

## Debugging and Monitoring

### Request Logging
All API requests are logged with the following format:
```
INFO:werkzeug:127.0.0.1 - - [20/Jan/2025 21:42:12] "POST /api/emails/search HTTP/1.1" 200 -
```

### Performance Monitoring
Key metrics tracked:
- Request response times
- Authentication success/failure rates
- Microsoft Graph API response times
- Error rates by endpoint

### Health Monitoring
Regular health checks should monitor:
- Backend service availability (`/api/health`)
- Authentication service status
- Microsoft Graph API connectivity
- Database connection status (if applicable)

This API reference provides comprehensive information for integrating with and using the KNGS Email Progress Checker backend services. 