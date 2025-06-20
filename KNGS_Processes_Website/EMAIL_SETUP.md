# Email Integration Setup Guide

## Overview

Your Electron app now includes Microsoft Graph API integration to fetch and display emails related to employees. When you click "Check Progress" for an employee, the app will:

1. Show the employee's Excel records
2. Search for emails containing the employee's name
3. Display recent emails with status indicators (read/unread, attachments, etc.)

## Prerequisites

- Python 3.8 or higher
- Microsoft 365 account with email access
- Admin consent for the Azure app registration (if in an organization)

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Azure App Registration

The app is pre-configured with a public client ID, but you may want to create your own:

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to Azure Active Directory > App registrations
3. Create a new registration with these settings:
   - Name: "Excel Email Checker"
   - Supported account types: Accounts in any organizational directory and personal Microsoft accounts
   - Redirect URI: Leave blank (we'll use device code flow)
4. Note the Application (client) ID and Directory (tenant) ID
5. Update `config.cfg` with your values if needed

### 3. Set Permissions

Your app needs these Microsoft Graph permissions:
- `User.Read` - To read user profile
- `Mail.Read` - To read emails
- `Mail.Send` - (Optional) For sending emails

These permissions are already configured in the provided client ID.

### 4. Start the Email Service

Before using the email features in your Electron app, start the email service:

```bash
python start_email_service.py
```

**Important**: The first time you run this, you'll need to authenticate:
1. The service will display a device code and URL
2. Open the URL in your browser
3. Enter the device code
4. Sign in with your Microsoft 365 account
5. Grant the requested permissions

### 5. Start Your Electron App

In a separate terminal window:

```bash
npm start
```

## How It Works

### Authentication Flow

1. **Device Code Authentication**: When the email service starts, it uses Microsoft's device code flow for authentication
2. **Token Management**: The service handles token refresh automatically
3. **Secure Communication**: Your Electron app communicates with the email service via local HTTP API

### Email Search

When you select an employee and click "Check Progress":

1. The app searches emails containing the employee's name
2. Results are sorted by date (newest first)
3. Shows email subject, sender, date, read status, and preview
4. Highlights unread emails and those with attachments

### Service Status

The app includes a service status indicator:
- 🟢 **Online**: Email service is running and accessible
- 🔴 **Offline**: Email service is not running or not accessible

## API Endpoints

The email service provides these endpoints:

- `GET /api/health` - Service health check
- `GET /api/auth/user` - Get current authenticated user info
- `GET /api/emails/recent?count=25` - Get recent emails
- `POST /api/emails/search` - Search emails by employee name

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Restart the email service: `python start_email_service.py`
   - Re-authenticate when prompted
   - Check your Microsoft 365 account status

2. **Service Offline**
   - Ensure the email service is running
   - Check if port 5000 is available
   - Look for error messages in the Python console

3. **No Emails Found**
   - Employee names must match exactly as they appear in emails
   - Check if the employee actually has related emails
   - Verify email search permissions

4. **CORS Errors**
   - The service includes CORS headers, but if you modify the code, ensure CORS is properly configured

### Debug Mode

To run the email service in debug mode:

```bash
python email_service.py
```

This will show detailed logging and auto-restart on code changes.

## Security Considerations

- The email service runs locally on port 5000
- Authentication tokens are managed by the Azure Identity library
- No email data is stored permanently by the app
- Communication between Electron and Python service is local-only

## Customization

### Modifying Search Criteria

Edit the `search_emails_by_employee` function in `email_service.py` to change how emails are searched:

```python
# Current: searches for employee name in subject and body
search=f'"{employee_name}"'

# Example: search only in subject
search=f'subject:"{employee_name}"'

# Example: search in from field
search=f'from:"{employee_name}"'
```

### Changing UI

The email display is handled in `src/components/EmployeeSelector.js`. You can modify:
- Email card styling
- Information displayed
- Sorting and filtering options

## Support

If you encounter issues:

1. Check the Python console for error messages
2. Check the Electron DevTools console (F12)
3. Verify your Microsoft 365 account has proper permissions
4. Ensure all dependencies are installed correctly

The email integration adds powerful functionality to help you track employee progress through both Excel records and related email communications. 