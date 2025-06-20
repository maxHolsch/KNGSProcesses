# KNGS Email Progress Checker - Run Instructions

## Quick Start

### Option 1: Using the Python Runner (Recommended)
```bash
python3 run_app.py
```

### Option 2: Using the Shell Script
```bash
./run_app.sh
```

## What This Does

The run script will:

1. **Start the Email Service** on port 5002
   - Handles Microsoft Graph API authentication
   - Provides email search functionality
   - Shows device code authentication prompts in the terminal

2. **Start the Electron App** with React development server
   - Automatically installs npm dependencies if needed
   - Opens the desktop application
   - Connects to the email service for email functionality

## Prerequisites

- **Python 3.7+** with pip
- **Node.js 16+** with npm
- **Microsoft Azure App Registration** (already configured)

## First Time Setup

1. **Install Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Node.js Dependencies:**
   ```bash
   npm install
   ```

3. **Run the Application:**
   ```bash
   python3 run_app.py
   ```

## How to Use the Application

### Step 1: Start the Application
Run the script and wait for both services to start:
```
🎯 KNGS Email Progress Checker - Starting Application
🚀 Starting email service...
✅ Email service started successfully on port 5002
🖥️  Starting Electron app...
✅ Electron app started successfully
🎉 Application started successfully!
```

### Step 2: Upload Excel File
1. The Electron app will open automatically
2. Click "Upload File" and select your Excel spreadsheet
3. The app will parse employee data from the spreadsheet

### Step 3: Check Employee Progress
1. Go to the "Check Progress" tab
2. Search for an employee name
3. Click "Check Progress"

### Step 4: Authenticate with Microsoft Graph (First Time Only)
When you first check emails, you'll see:
```
🔐 Authenticating with Microsoft Graph...
📱 Please check the terminal for device code instructions
```

In the terminal, you'll see something like:
```
To sign in, use a web browser to open the page https://microsoft.com/devicelogin 
and enter the code XXXXXXXXX to authenticate.
```

1. Open https://microsoft.com/devicelogin in your browser
2. Enter the displayed code
3. Sign in with your Microsoft account
4. Grant permissions to the application

### Step 5: View Results
After authentication, you'll see:
- **Employee Records**: All spreadsheet rows assigned to that employee
- **Related Emails**: Emails with the employee's name in the subject line
- **Email Details**: Sender, date, read status, attachments, and preview

## Features

### Email Search
- Searches for emails with employee name in subject line
- Shows read/unread status
- Displays email previews
- Indicates attachments with 📎 icon
- Shows sender information and timestamps

### Data Integration
- Parses Excel spreadsheets automatically
- Matches employee names to email searches
- Shows ticket numbers and assignments
- Displays all relevant data columns

### Authentication
- **Single Sign-On**: Authenticate once per session
- **Token Caching**: Reuses authentication tokens
- **Device Code Flow**: Secure authentication without storing passwords

## Troubleshooting

### Email Service Issues
If you see "Email service is not running":
1. Check that port 5002 is not in use by another application
2. Restart the application
3. Check the terminal for error messages

### Authentication Issues
If authentication fails:
1. Make sure you have internet connectivity
2. Check that the device code hasn't expired (they expire after 15 minutes)
3. Try restarting the application for a fresh authentication

### Electron App Issues
If the Electron app doesn't open:
1. Check that Node.js and npm are installed
2. Run `npm install` manually if dependencies are missing
3. Check for port conflicts (React dev server uses port 3000)

## Stopping the Application

Press `Ctrl+C` in the terminal to stop both services:
```
⚠️  Keyboard interrupt received
🧹 Cleaning up...
✅ Email service stopped
✅ Electron app stopped
```

## Technical Details

### Ports Used
- **5002**: Email service API
- **3000**: React development server
- **Electron**: Desktop application (connects to port 3000)

### API Endpoints
- `GET /api/health` - Service health check
- `GET /api/auth/user` - Get current user info
- `POST /api/emails/search` - Search emails by employee name

### File Structure
```
├── run_app.py              # Main application runner
├── run_app.sh              # Shell script wrapper
├── email_service_interactive.py  # Email service with visible auth
├── src/                    # React application source
├── main.js                 # Electron main process
└── package.json            # Node.js dependencies
```

## Support

If you encounter issues:
1. Check the terminal output for detailed error messages
2. Ensure all prerequisites are installed
3. Verify your Microsoft account has the necessary permissions
4. Try restarting the application

The application provides detailed logging to help diagnose any issues. 