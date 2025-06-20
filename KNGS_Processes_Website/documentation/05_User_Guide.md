# KNGS Email Progress Checker - User Guide

## Overview

The KNGS Email Progress Checker is an intuitive desktop application that combines Excel spreadsheet data with Microsoft email search capabilities to provide comprehensive employee progress tracking. This guide will walk you through every aspect of using the application effectively.

## Getting Started

### First Launch

1. **Start the Application**
   - Double-click the application icon or run `python run_app.py`
   - The application will automatically open in a new window
   - Both the backend service and frontend interface will start simultaneously

2. **Initial Setup Verification**
   - The main interface will display with navigation tabs
   - Ensure you see the file upload area on the main tab
   - Check that the "Check Progress" tab is accessible

### Main Interface Overview

The application features a clean, modern interface with two main sections:

#### Navigation Tabs
- **Main Tab**: Excel file upload and data visualization
- **Check Progress Tab**: Employee search and email analysis

#### Status Indicators
- **Connection Status**: Shows backend service connectivity
- **Authentication Status**: Displays Microsoft Graph authentication state

## Working with Excel Data

### Preparing Your Excel File

Your Excel file must meet specific requirements:

#### Required Structure
- **Sheet Name**: Must contain a sheet named "in progress" (case insensitive)
- **Column A**: Employee ticket numbers or IDs
- **Column F**: Employee names (exactly as they appear in emails)

#### Example Structure:
```
| A (Ticket) | B | C | D | E | F (Employee) | G | H |
|------------|---|---|---|---|--------------|---|---|
| TICK-001   |   |   |   |   | John Smith   |   |   |
| TICK-002   |   |   |   |   | Jane Doe     |   |   |
| TICK-003   |   |   |   |   | Bob Johnson  |   |   |
```

### Uploading Excel Files

#### Method 1: Drag and Drop
1. Open your file explorer
2. Navigate to your Excel file (.xlsx or .xls)
3. Drag the file into the upload area
4. The file will be processed automatically

#### Method 2: Click to Upload
1. Click the "Click to upload" text in the upload area
2. Select your Excel file from the file dialog
3. Click "Open" to upload

### Viewing Uploaded Data

Once uploaded successfully, you'll see:

#### Data Summary
- **Total Records**: Number of rows processed
- **Unique Employees**: Count of distinct employee names
- **Unique Tickets**: Count of distinct ticket numbers

#### Interactive Data Table
- **Search Function**: Type in the search box to filter records
- **Column Sorting**: Click column headers to sort data
- **Hover Effects**: Row highlighting for better readability

#### Data Validation Messages
- **Success**: Green confirmation message
- **Warnings**: Yellow alerts for data inconsistencies  
- **Errors**: Red error messages for structural issues

## Employee Progress Checking

### Microsoft Graph Authentication

Before checking employee emails, you must authenticate with Microsoft Graph:

#### Device Code Authentication Flow
1. Navigate to the "Check Progress" tab
2. Select an employee and click "Check Progress"
3. An authentication modal will appear with:
   - **Device Code**: A short alphanumeric code (e.g., "FC87NDD2E")
   - **Verification URL**: Usually `https://microsoft.com/devicelogin`
   - **Instructions**: Step-by-step authentication guidance

#### Completing Authentication
1. Open a web browser
2. Navigate to the verification URL
3. Enter the device code when prompted
4. Sign in with your Microsoft account (personal or organizational)
5. Grant the requested permissions
6. Return to the application

### Searching Employee Emails

#### Employee Selection Process
1. **Type to Search**: Start typing an employee name in the search field
2. **Dropdown Filtering**: The dropdown will filter based on your input
3. **Selection**: Click on the desired employee name
4. **Verification**: Confirm the selected employee appears in the input field

#### Initiating Email Search
1. Click the "Check Progress" button
2. If not authenticated, follow the authentication process above
3. The application will search for emails containing the employee's name
4. Results will appear in the email results section

### Understanding Email Results

#### Email Information Displayed
Each email result shows:
- **Subject Line**: Complete email subject
- **Sender**: Name and email address of the sender
- **Date/Time**: When the email was received
- **Read Status**: Whether the email has been read
- **Attachments**: Indicator if email contains attachments
- **Preview**: Brief preview of email content

#### Result Metrics
- **Total Found**: Number of emails found for the employee
- **Search Query**: Confirmation of the search term used
- **Timestamp**: When the search was performed

## Advanced Features

### Data Filtering and Search

#### Global Search
- Type in the main search box to filter across all data columns
- Search is case-insensitive and matches partial text
- Results update in real-time as you type

#### Column-Specific Sorting
- Click any column header to sort by that column
- First click: Ascending order
- Second click: Descending order
- Third click: Return to original order

### Employee Quick Selection

From the data view, you can quickly select employees:
1. View the employee summary statistics
2. Click on any employee name in the data table
3. The employee will be automatically selected in the "Check Progress" tab

### Progress Correlation

The application helps correlate Excel data with email activity:
- **Ticket Matching**: Compare ticket numbers with email subjects
- **Timeline Analysis**: Review email dates against progress milestones
- **Communication Patterns**: Identify email frequency and types

## Troubleshooting Common Issues

### File Upload Problems

#### "No 'in progress' sheet found"
**Cause**: Excel file doesn't contain the required sheet name
**Solution**:
1. Ensure your Excel file has a sheet named "in progress"
2. Check for extra spaces in the sheet name
3. Verify the sheet name is spelled correctly

#### "Empty sheet detected"
**Cause**: The "in progress" sheet contains no data
**Solution**:
1. Verify Column A contains ticket numbers
2. Ensure Column F contains employee names
3. Check that data starts from row 1 or 2

#### File Format Errors
**Cause**: Unsupported file format
**Solution**:
1. Save your file as .xlsx (preferred) or .xls
2. Ensure the file is not corrupted
3. Try opening the file in Excel to verify it's valid

### Authentication Issues

#### Device Code Expired
**Symptoms**: "Device code expired" error message
**Solution**:
1. Request a new device code
2. Complete authentication within 15 minutes
3. Ensure stable internet connection during authentication

#### Permission Denied
**Symptoms**: "Insufficient privileges" error
**Solution**:
1. Contact your IT administrator
2. Verify your account has necessary email permissions
3. Try using a personal Microsoft account if applicable

#### Authentication Loop
**Symptoms**: Repeatedly asked to authenticate
**Solution**:
1. Clear browser cache and cookies
2. Try a different browser for authentication
3. Wait 5 minutes and try again

### Email Search Issues

#### No Emails Found
**Possible Causes**:
- Employee name not exactly matching email content
- Employee has no email activity
- Insufficient search permissions

**Solutions**:
1. Try alternative name spellings or variations
2. Check if employee name appears in email subjects or content
3. Verify authentication permissions include Mail.Read

#### Slow Search Results
**Causes**: Large mailbox or network latency
**Solutions**:
1. Be patient - searches can take 10-30 seconds
2. Check your internet connection
3. Try searching during off-peak hours

### Performance Issues

#### Application Running Slowly
**Solutions**:
1. Close other applications to free memory
2. Restart the KNGS application
3. Check available disk space

#### Large File Processing
**For files with many rows**:
1. Consider splitting large files into smaller sections
2. Allow extra time for processing
3. Ensure sufficient RAM is available

## Best Practices

### Data Preparation
1. **Consistent Naming**: Use consistent employee name formats
2. **Clean Data**: Remove empty rows and columns
3. **Backup Files**: Keep original Excel files as backups

### Authentication Management
1. **Stay Authenticated**: Complete searches while authenticated
2. **Security**: Don't share device codes with others
3. **Regular Re-authentication**: Expect to re-authenticate periodically

### Efficient Workflow
1. **Batch Processing**: Upload Excel data first
2. **Systematic Checking**: Work through employees methodically
3. **Documentation**: Keep notes of findings outside the application

## Privacy and Security

### Data Handling
- Excel data is processed locally and not stored permanently
- Email content is retrieved but not saved to disk
- Authentication tokens are stored temporarily in memory

### Access Control
- Only you can access emails your account has permission to read
- The application doesn't store or transmit sensitive data
- All Microsoft Graph communications use encrypted connections

## Getting Help

### Application Support
- Check this user guide for common solutions
- Review error messages carefully for specific guidance
- Ensure you're using the latest version of the application

### Technical Issues
- Verify system requirements are met
- Check internet connectivity
- Confirm Microsoft Graph service availability

This user guide provides comprehensive instructions for effective use of the KNGS Email Progress Checker. For technical implementation details, refer to the accompanying technical documentation. 