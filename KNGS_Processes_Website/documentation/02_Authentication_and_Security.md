# KNGS Email Progress Checker - Authentication & Security Documentation

## Overview

The KNGS Email Progress Checker implements robust authentication and security measures to protect user data and ensure secure communication with Microsoft Graph API. This document outlines the authentication flows, security protocols, and best practices implemented in the system.

## Authentication Architecture

### OAuth 2.0 Device Code Flow

The application uses OAuth 2.0 device code flow for authentication, which is optimal for desktop applications that cannot securely store client secrets.

#### Authentication Process

1. **Device Code Request**
   - Application requests a device code from Azure AD
   - User receives a user-friendly code and verification URL
   - Code is displayed both in console and Electron modal

2. **User Authentication**
   - User navigates to `https://microsoft.com/devicelogin`
   - Enters the provided device code
   - Completes organizational or personal account authentication

3. **Token Exchange**
   - Application polls Azure AD for token availability
   - Upon successful authentication, receives access and refresh tokens
   - Tokens are stored in memory for session duration

4. **Graph API Access**
   - Access token is used for all Microsoft Graph API calls
   - Automatic token refresh when expired
   - Graceful fallback to re-authentication when needed

### Configuration Management

```python
# Azure AD Configuration
config['azure'] = {
    'clientId': 'b9be55dd-85d1-41ab-ab92-e1bb2cafd19c',
    'tenantId': 'common',  # Supports both organizational and personal accounts
    'graphUserScopes': 'User.Read Mail.Read Mail.Send'
}
```

#### Client Registration Requirements

The application requires registration in Azure Active Directory with:
- **Application Type**: Public client
- **Redirect URI**: Not required for device code flow
- **API Permissions**: 
  - Microsoft Graph > User.Read (Delegated)
  - Microsoft Graph > Mail.Read (Delegated)
  - Microsoft Graph > Mail.Send (Delegated)

## Security Implementation

### Token Management

#### Access Token Security
- **Storage**: Tokens stored only in memory, never persisted to disk
- **Lifetime**: Tokens expire after 1 hour by default
- **Refresh**: Automatic refresh using refresh tokens
- **Scope**: Minimal permissions requested (User.Read, Mail.Read, Mail.Send)

#### Session Management
```python
def check_authentication_status():
    """Check if user is already authenticated"""
    global authenticated, last_successful_auth
    
    # Use cached authentication for 30 minutes
    if last_successful_auth and (time.time() - last_successful_auth) < 1800:
        authenticated = True
        return True
    
    # Verify with Microsoft Graph API
    return validate_token_with_graph_api()
```

### API Security

#### CORS Configuration
```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

#### Request Validation
- All API endpoints validate request structure
- Input sanitization for employee names and search queries
- Rate limiting to prevent abuse
- Error handling without exposing sensitive information

### Data Protection

#### In-Transit Security
- **HTTPS**: All Microsoft Graph API communications use HTTPS
- **TLS 1.2+**: Minimum TLS version enforced
- **Certificate Validation**: Strict certificate validation enabled

#### In-Memory Security
- **No Persistence**: Sensitive data not written to disk
- **Memory Cleanup**: Tokens cleared on application exit
- **Secure Logging**: PII redacted from logs

#### Email Data Handling
```python
def sanitize_email_data(email):
    """Sanitize email data before processing"""
    return {
        "subject": email.subject,
        "from": email.from_field.email_address.address if email.from_field else None,
        "receivedDateTime": email.received_date_time.isoformat() if email.received_date_time else None,
        "isRead": email.is_read,
        "hasAttachments": email.has_attachments,
        "body": email.body.content[:500] if email.body else None  # Truncate body content
    }
```

## Authentication Endpoints

### Health Check
```
GET /api/health
```
- **Purpose**: Verify backend service availability
- **Authentication**: None required
- **Response**: JSON status object

### Authentication Status
```
GET /api/auth/status
```
- **Purpose**: Check current authentication state
- **Authentication**: None required
- **Response**: 
  ```json
  {
    "authenticated": true,
    "user": {
      "displayName": "John Doe",
      "email": "john.doe@example.com"
    }
  }
  ```

### Device Code Retrieval
```
GET /api/auth/device-code
```
- **Purpose**: Get current device code for authentication
- **Authentication**: None required
- **Response**:
  ```json
  {
    "deviceCode": "FC87NDD2E",
    "verificationUri": "https://microsoft.com/devicelogin",
    "requested": true
  }
  ```

### User Information
```
GET /api/auth/user
```
- **Purpose**: Retrieve authenticated user details
- **Authentication**: Required
- **Response**: User profile information

## Security Best Practices

### Application Level

1. **Minimal Permissions**
   - Request only necessary Graph API scopes
   - Implement principle of least privilege
   - Regular permission audits

2. **Error Handling**
   - Sanitize error messages
   - Prevent information disclosure
   - Log security events appropriately

3. **Input Validation**
   - Validate all user inputs
   - Sanitize search queries
   - Prevent injection attacks

### Deployment Security

1. **Environment Configuration**
   - Use environment variables for sensitive settings
   - Separate development and production configurations
   - Secure configuration file permissions

2. **Network Security**
   - Restrict outbound connections to required endpoints
   - Implement firewall rules for production deployments
   - Monitor network traffic for anomalies

3. **Update Management**
   - Regular dependency updates
   - Security patch management
   - Vulnerability scanning

## Compliance Considerations

### Data Privacy
- **GDPR**: Minimal data collection and processing
- **CCPA**: User data rights and transparency
- **HIPAA**: If applicable, additional safeguards required

### Audit Requirements
- **Authentication Events**: All login attempts logged
- **Data Access**: Email search activities tracked
- **Error Conditions**: Security-related errors logged
- **Session Management**: Token lifecycle events recorded

## Security Monitoring

### Logging Configuration
```python
# Security event logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('security.log')
    ]
)
```

### Monitored Events
- Authentication attempts (success/failure)
- Token refresh operations
- API rate limiting events
- Unauthorized access attempts
- Configuration changes

## Troubleshooting Security Issues

### Common Authentication Problems

1. **Device Code Expired**
   - **Symptom**: "Device code expired" error
   - **Solution**: Request new device code
   - **Prevention**: Complete authentication within 15 minutes

2. **Insufficient Permissions**
   - **Symptom**: "Forbidden" or "Access denied" errors
   - **Solution**: Review Azure AD app permissions
   - **Prevention**: Regular permission audits

3. **Token Refresh Failures**
   - **Symptom**: Intermittent authentication losses
   - **Solution**: Clear authentication cache and re-authenticate
   - **Prevention**: Implement robust token refresh logic

### Security Incident Response

1. **Immediate Actions**
   - Revoke compromised tokens
   - Reset authentication state
   - Review access logs

2. **Investigation**
   - Analyze authentication logs
   - Check for unusual access patterns
   - Verify API usage patterns

3. **Recovery**
   - Force re-authentication
   - Update security configurations
   - Implement additional monitoring

This authentication and security documentation provides comprehensive guidance for understanding, implementing, and maintaining the security aspects of the KNGS Email Progress Checker. 