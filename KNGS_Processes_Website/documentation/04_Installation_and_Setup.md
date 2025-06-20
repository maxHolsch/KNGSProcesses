# KNGS Email Progress Checker - Installation & Setup Guide

## Overview

This comprehensive guide provides step-by-step instructions for installing, configuring, and deploying the KNGS Email Progress Checker application. The guide covers both development and production environments across multiple operating systems.

## System Requirements

### Hardware Requirements

#### Minimum Requirements
- **CPU**: 2-core processor (Intel Core i3 or AMD equivalent)
- **RAM**: 4GB system memory
- **Storage**: 2GB free disk space
- **Network**: Broadband internet connection

#### Recommended Requirements
- **CPU**: 4-core processor (Intel Core i5 or AMD equivalent)
- **RAM**: 8GB system memory
- **Storage**: 5GB free disk space on SSD
- **Network**: High-speed internet connection

### Operating System Support

#### Windows
- **Windows 10**: Version 1909 or later
- **Windows 11**: All versions supported
- **Windows Server**: 2019 or later

#### macOS
- **macOS Catalina**: 10.15 or later
- **macOS Big Sur**: 11.0 or later
- **macOS Monterey**: 12.0 or later
- **macOS Ventura**: 13.0 or later

#### Linux
- **Ubuntu**: 18.04 LTS or later
- **CentOS**: 7 or later
- **Fedora**: 30 or later
- **Debian**: 10 or later

## Prerequisites Installation

### 1. Node.js Installation

#### Windows
1. Download Node.js from [nodejs.org](https://nodejs.org/)
2. Choose LTS version (recommended)
3. Run the installer and follow the setup wizard
4. Verify installation:
   ```cmd
   node --version
   npm --version
   ```

#### macOS
**Option 1: Official Installer**
1. Download from [nodejs.org](https://nodejs.org/)
2. Run the .pkg installer
3. Follow installation prompts

**Option 2: Homebrew**
```bash
brew install node
```

#### Linux (Ubuntu/Debian)
```bash
# Update package index
sudo apt update

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version
```

### 2. Python Installation

#### Windows
1. Download Python 3.8+ from [python.org](https://python.org/)
2. **Important**: Check "Add Python to PATH" during installation
3. Run installer as administrator
4. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

#### macOS
**Option 1: Official Installer**
1. Download from [python.org](https://python.org/)
2. Run the installer package

**Option 2: Homebrew**
```bash
brew install python@3.11
```

#### Linux (Ubuntu/Debian)
```bash
# Install Python 3 and pip
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Verify installation
python3 --version
pip3 --version
```

### 3. Git Installation

#### Windows
1. Download Git from [git-scm.com](https://git-scm.com/)
2. Run installer with default settings
3. Verify: `git --version`

#### macOS
```bash
# Install via Homebrew
brew install git

# Or use Xcode Command Line Tools
xcode-select --install
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt install git

# CentOS/RHEL
sudo yum install git
```

## Application Installation

### 1. Download/Clone the Application

#### Option 1: Download ZIP
1. Download the project ZIP file
2. Extract to desired location
3. Open terminal/command prompt in the extracted folder

#### Option 2: Git Clone
```bash
git clone <repository-url>
cd KNGS_Processes_Website
```

### 2. Python Dependencies Installation

#### Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### Install Python Dependencies
```bash
# Install from requirements.txt
pip install -r requirements.txt

# Verify installation
pip list
```

### 3. Node.js Dependencies Installation

```bash
# Install npm dependencies
npm install

# Verify installation
npm list --depth=0
```

## Configuration Setup

### 1. Azure AD Application Registration

#### Step 1: Access Azure Portal
1. Navigate to [portal.azure.com](https://portal.azure.com/)
2. Sign in with administrator credentials
3. Go to "Azure Active Directory"

#### Step 2: Register Application
1. Click "App registrations" → "New registration"
2. Enter application details:
   - **Name**: "KNGS Email Progress Checker"
   - **Supported account types**: "Accounts in any organizational directory and personal Microsoft accounts"
   - **Redirect URI**: Leave blank for device code flow

#### Step 3: Configure Permissions
1. Go to "API permissions"
2. Click "Add a permission" → "Microsoft Graph"
3. Select "Delegated permissions"
4. Add the following permissions:
   - `User.Read`
   - `Mail.Read`
   - `Mail.Send`
5. Click "Grant admin consent" (if you have admin privileges)

#### Step 4: Get Application ID
1. Go to "Overview" tab
2. Copy the "Application (client) ID"
3. Note the "Directory (tenant) ID"

### 2. Application Configuration

#### Create Configuration File
Create `config.cfg` in the project root:

```ini
[azure]
clientId = YOUR_APPLICATION_CLIENT_ID
tenantId = common
graphUserScopes = User.Read Mail.Read Mail.Send
```

#### Environment Variables (Optional)
```bash
# Windows
set AZURE_CLIENT_ID=your_client_id_here
set AZURE_TENANT_ID=common

# macOS/Linux
export AZURE_CLIENT_ID=your_client_id_here
export AZURE_TENANT_ID=common
```

### 3. Network Configuration

#### Firewall Rules
Ensure the following ports are accessible:
- **Port 3000**: React development server
- **Port 5002**: Flask backend API
- **Outbound HTTPS (443)**: Microsoft Graph API access

#### Proxy Configuration (if applicable)
```bash
# Set proxy environment variables
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
```

## Running the Application

### Development Mode

#### Automatic Startup (Recommended)
```bash
# Start both backend and frontend
python run_app.py
```

This will:
- Start the Flask backend on port 5002
- Start the React development server on port 3000
- Launch the Electron application
- Display authentication codes when needed

#### Manual Startup (Alternative)
```bash
# Terminal 1: Start email service
python email_service_interactive.py

# Terminal 2: Start Electron app
npm run dev
```

### Production Mode

#### Build and Run
```bash
# Build React application
npm run react-build

# Start production server
npm start
```

## Verification and Testing

### 1. Health Check
```bash
# Test backend health
curl http://127.0.0.1:5002/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-20T19:42:00Z",
  "service": "KNGS Email Progress Checker"
}
```

### 2. Authentication Test
1. Launch the application
2. Navigate to "Check Progress" tab
3. Enter an employee name
4. Click "Check Progress"
5. Follow device code authentication flow

### 3. Excel File Test
1. Prepare an Excel file with:
   - Sheet named "in progress"
   - Column A: Ticket numbers
   - Column F: Employee names
2. Upload the file in the application
3. Verify data displays correctly

## Troubleshooting Common Issues

### Installation Issues

#### Node.js/npm Issues
**Problem**: `npm install` fails with permission errors
**Solution**:
```bash
# Windows (run as administrator)
npm install --global windows-build-tools

# macOS/Linux
sudo chown -R $(whoami) ~/.npm
npm install
```

#### Python Dependencies Issues
**Problem**: `pip install` fails with compilation errors
**Solution**:
```bash
# Install build tools
# Windows
pip install --upgrade setuptools wheel

# macOS
xcode-select --install

# Linux
sudo apt-get install build-essential python3-dev
```

### Configuration Issues

#### Azure AD Authentication
**Problem**: "Invalid client" error
**Solution**:
1. Verify client ID in `config.cfg`
2. Ensure application is registered in Azure AD
3. Check API permissions are granted

**Problem**: "Insufficient privileges" error
**Solution**:
1. Verify API permissions in Azure AD
2. Request admin consent for permissions
3. Check user has necessary licenses

### Runtime Issues

#### Port Conflicts
**Problem**: "Port already in use" error
**Solution**:
```bash
# Find process using port
# Windows
netstat -ano | findstr :5002
taskkill /PID <pid> /F

# macOS/Linux
lsof -i :5002
kill -9 <pid>
```

#### Electron Application Issues
**Problem**: Electron app doesn't start
**Solution**:
1. Clear npm cache: `npm cache clean --force`
2. Reinstall dependencies: `rm -rf node_modules && npm install`
3. Check Node.js version compatibility

### Network Issues

#### Microsoft Graph API Connectivity
**Problem**: "Network request failed" errors
**Solution**:
1. Verify internet connectivity
2. Check firewall/proxy settings
3. Test direct access to `https://graph.microsoft.com`

#### CORS Issues
**Problem**: "CORS policy" errors in browser
**Solution**:
1. Verify frontend URL in CORS configuration
2. Check backend is running on correct port
3. Clear browser cache

## Performance Optimization

### System Optimization

#### Memory Management
```bash
# Increase Node.js memory limit
export NODE_OPTIONS="--max-old-space-size=4096"
```

#### Disk Space Management
```bash
# Clean npm cache
npm cache clean --force

# Clean Python cache
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

### Application Optimization

#### Backend Performance
- Use virtual environments for Python dependencies
- Implement connection pooling for Graph API
- Cache authentication tokens appropriately

#### Frontend Performance
- Use React production build for deployment
- Implement lazy loading for large datasets
- Optimize Electron renderer process

## Deployment Considerations

### Security Hardening
1. **Restrict API Access**: Limit CORS origins to specific domains
2. **Network Security**: Use HTTPS in production
3. **Update Management**: Regularly update dependencies
4. **Monitoring**: Implement logging and monitoring

### Backup and Recovery
1. **Configuration Backup**: Backup `config.cfg` and environment variables
2. **Data Backup**: Backup user data and logs
3. **Recovery Procedures**: Document recovery steps

### Scaling Considerations
1. **Load Balancing**: Use reverse proxy for multiple instances
2. **Database**: Consider database for persistent data
3. **Caching**: Implement Redis or similar for caching
4. **Monitoring**: Use application performance monitoring tools

This installation and setup guide provides comprehensive instructions for successfully deploying the KNGS Email Progress Checker application in various environments. 