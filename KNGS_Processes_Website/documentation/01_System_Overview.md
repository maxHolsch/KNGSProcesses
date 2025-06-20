# KNGS Email Progress Checker - System Overview
Disclaimer: Documentation and code creation was assisted using claude 4 sonnet. This is intended as a prototype, do not deploy this system to production enviroments without review

## Executive Summary

The KNGS Email Progress Checker is a comprehensive desktop application designed to streamline employee progress tracking by integrating Excel spreadsheet data with Microsoft Graph API email search capabilities. This tool enables organizations to efficiently monitor employee progress through automated email analysis and data visualization.

## Core Functionality

### Primary Features
- **Excel Data Processing**: Import and analyze employee progress data from Excel spreadsheets
- **Microsoft Graph Integration**: Secure OAuth 2.0 authentication with device code flow
- **Email Search & Analysis**: Search employee-related emails using Microsoft Graph API
- **Cross-Platform Desktop Application**: Built with Electron for Windows, macOS, and Linux compatibility
- **Real-Time Progress Tracking**: Live updates and interactive data visualization

### Key Components

1. **Frontend (Electron + React)**
   - Modern, responsive user interface
   - Excel file upload and processing
   - Employee selection and filtering
   - Real-time progress visualization

2. **Backend (Python Flask)**
   - RESTful API endpoints
   - Microsoft Graph API integration
   - Azure AD authentication handling
   - Email search and processing

3. **Authentication System**
   - OAuth 2.0 device code flow
   - Azure Active Directory integration
   - Secure token management
   - Session persistence

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      KNGS Email Progress Checker                │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (Electron + React)                                   │
│  ├─ File Upload Component                                       │
│  ├─ Data Visualization Dashboard                                │
│  ├─ Employee Search Interface                                   │
│  └─ Authentication Modal                                        │
├─────────────────────────────────────────────────────────────────┤
│  Backend (Python Flask)                                        │
│  ├─ REST API Endpoints                                          │
│  ├─ Microsoft Graph Client                                      │
│  ├─ Excel Processing Engine                                     │
│  └─ Authentication Manager                                      │
├─────────────────────────────────────────────────────────────────┤
│  External Services                                              │
│  ├─ Microsoft Graph API                                         │
│  ├─ Azure Active Directory                                      │
│  └─ Office 365 Email Services                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Target Use Case

### 1. Human Resources Management
- Track employee progress against established benchmarks
- Monitor completion rates for assigned tasks
- Generate progress reports for management review

## Data Flow

1. **Data Ingestion**: Excel files containing employee progress data are uploaded
2. **Processing**: Backend processes and validates the Excel data structure
3. **Authentication**: Users authenticate with Microsoft Graph via device code flow
4. **Email Search**: System searches for employee-related emails using Graph API
5. **Correlation**: Email data is correlated with progress data from Excel
6. **Visualization**: Results are presented in an interactive dashboard

## Technical Specifications

### Runtime Requirements
- **Node.js**: Version 14 or higher
- **Python**: Version 3.8 or higher
- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Memory**: Minimum 4GB RAM recommended
- **Storage**: 500MB free space for installation

### Network Requirements
- Internet connectivity for Microsoft Graph API access
- HTTPS outbound connections to `*.microsoftonline.com`
- Access to `graph.microsoft.com` endpoints

### Security Considerations
- All authentication tokens are stored securely in memory
- No sensitive data is persisted to disk
- HTTPS encryption for all API communications
- Compliance with Microsoft Graph API security standards

## Integration Points

### Microsoft Graph API
- **Endpoint**: `https://graph.microsoft.com/v1.0/`
- **Authentication**: OAuth 2.0 with device code flow
- **Scopes**: `User.Read`, `Mail.Read`, `Mail.Send`
- **Rate Limiting**: Adheres to Microsoft's throttling policies

### Azure Active Directory
- **Tenant**: Configurable for organizational or personal accounts
- **Client ID**: Registered application in Azure AD
- **Permissions**: Delegated permissions for email access

## Performance Characteristics

### Response Times
- Excel file processing: < 5 seconds for files up to 10MB
- Email search queries: 2-10 seconds depending on result size
- Authentication flow: 30-60 seconds (user-dependent)

### Scalability
- Supports Excel files with up to 50,000 rows
- Concurrent email searches limited by Graph API throttling
- Memory usage scales linearly with data size

## Monitoring & Logging

### Application Logs
- Authentication events and errors
- API request/response logging
- Performance metrics and timing
- Error tracking and debugging information

### Health Checks
- Backend service health endpoint: `/api/health`
- Authentication status monitoring
- Microsoft Graph API connectivity checks

## Deployment Architecture

### Development Mode
- React development server on port 3000
- Flask backend on port 5002
- Electron wrapper for desktop experience

### Production Mode
- Compiled React bundle served by Electron
- Packaged Python backend as executable
- Self-contained desktop application
