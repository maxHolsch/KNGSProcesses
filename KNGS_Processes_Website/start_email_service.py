#!/usr/bin/env python3

import sys
import os

def main():
    print("📧 Email Service Launcher")
    print("=" * 50)
    print("Choose which version to run:")
    print("1. Synchronous version (RECOMMENDED - no timeout issues)")
    print("2. Asynchronous version (may have timeout issues)")
    print("3. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == '1':
                print("\n🚀 Starting synchronous email service...")
                print("This version should work without timeout issues.")
                os.system("python email_service_sync.py")
                break
            elif choice == '2':
                print("\n🚀 Starting asynchronous email service...")
                print("This version may have timeout issues but supports true async operations.")
                os.system("python email_service.py")
                break
            elif choice == '3':
                print("👋 Goodbye!")
                sys.exit(0)
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == '__main__':
    main() 