#!/usr/bin/env python3

import requests
import json

def test_subject_search():
    """Test the subject line search functionality"""
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Testing Subject Line Email Search...")
    print("=" * 50)
    
    # Test health first
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ Email service is not running. Please start it first.")
            return False
    except:
        print("❌ Email service is not running. Please start it first.")
        return False
    
    print("✅ Email service is running")
    
    # Get employee name from user
    employee_name = input("\n📝 Enter an employee name to search for in email subjects: ").strip()
    
    if not employee_name:
        print("❌ No employee name provided")
        return False
    
    print(f"\n🔍 Searching for emails with '{employee_name}' in subject line...")
    
    try:
        test_data = {
            "employeeName": employee_name,
            "count": 25
        }
        response = requests.post(
            f"{base_url}/api/emails/search", 
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            email_data = response.json()
            emails = email_data.get('emails', [])
            
            print(f"✅ Search completed successfully!")
            print(f"📧 Found {len(emails)} emails with '{employee_name}' in subject line")
            
            if emails:
                print("\n📋 Email Results:")
                print("-" * 50)
                for i, email in enumerate(emails, 1):
                    status = "📩 UNREAD" if not email.get('isRead') else "📧 READ"
                    attachments = " 📎" if email.get('hasAttachments') else ""
                    
                    print(f"{i}. {status}{attachments}")
                    print(f"   Subject: {email.get('subject', 'No Subject')}")
                    print(f"   From: {email.get('from', {}).get('name', 'Unknown')} ({email.get('from', {}).get('address', 'Unknown')})")
                    print(f"   Date: {email.get('receivedDateTime', 'Unknown')}")
                    
                    if email.get('bodyPreview'):
                        preview = email['bodyPreview'][:100] + "..." if len(email['bodyPreview']) > 100 else email['bodyPreview']
                        print(f"   Preview: {preview}")
                    print()
                
                if email_data.get('hasMore'):
                    print("📝 Note: More emails are available (showing first 25)")
            else:
                print(f"\n📭 No emails found with '{employee_name}' in the subject line")
                print("💡 Try:")
                print("   - Check if the employee name is spelled correctly")
                print("   - Try a partial name (first name only)")
                print("   - Check if there are actually emails with this name in subjects")
            
        elif response.status_code == 401:
            print("❌ Authentication failed")
            print("💡 You may need to authenticate with Microsoft Graph first")
            error_data = response.json()
            print(f"📝 Details: {error_data.get('error', 'Unknown error')}")
            
        else:
            print(f"❌ Search failed with status code: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📝 Error: {error_data.get('error', 'Unknown error')}")
                print(f"📝 Details: {error_data.get('details', 'No details')}")
            except:
                print(f"📝 Response: {response.text}")
                
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        print("💡 The search may be taking too long. Try again or check your connection.")
    except Exception as e:
        print(f"❌ Search failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test completed!")
    
    return True

if __name__ == "__main__":
    try:
        test_subject_search()
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}") 