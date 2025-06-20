#!/usr/bin/env python3

import subprocess
import time
import sys
import os
import signal
import threading
import requests
from pathlib import Path

class AppRunner:
    def __init__(self):
        self.email_service_process = None
        self.electron_process = None
        self.running = True
        
    def check_port(self, port, host='127.0.0.1'):
        """Check if a port is available"""
        try:
            response = requests.get(f'http://{host}:{port}/api/health', timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def wait_for_service(self, port, timeout=30, host='127.0.0.1'):
        """Wait for a service to become available"""
        print(f"⏳ Waiting for service on port {port}...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.check_port(port, host):
                print(f"✅ Service on port {port} is ready!")
                return True
            time.sleep(1)
        return False
    
    def start_email_service(self):
        """Start the email service"""
        print("🚀 Starting email service...")
        try:
            # Use the interactive service that shows device codes
            self.email_service_process = subprocess.Popen(
                [sys.executable, 'email_service_interactive.py'],
                cwd=os.getcwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Monitor email service output in a separate thread
            def monitor_email_service():
                for line in iter(self.email_service_process.stdout.readline, ''):
                    if line.strip():
                        print(f"📧 {line.strip()}")
                    if not self.running:
                        break
            
            email_thread = threading.Thread(target=monitor_email_service, daemon=True)
            email_thread.start()
            
            # Wait for the service to be ready
            if self.wait_for_service(5002):
                print("✅ Email service started successfully on port 5002")
                return True
            else:
                print("❌ Email service failed to start within timeout")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start email service: {e}")
            return False
    
    def start_electron_app(self):
        """Start the Electron app"""
        print("🖥️  Starting Electron app...")
        try:
            # Check if node_modules exists
            if not Path('node_modules').exists():
                print("📦 Installing npm dependencies...")
                install_result = subprocess.run(['npm', 'install'], cwd=os.getcwd())
                if install_result.returncode != 0:
                    print("❌ Failed to install npm dependencies")
                    return False
            
            # Start the Electron app with React dev server
            self.electron_process = subprocess.Popen(
                ['npm', 'run', 'dev'],
                cwd=os.getcwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Monitor Electron output in a separate thread
            def monitor_electron():
                for line in iter(self.electron_process.stdout.readline, ''):
                    if line.strip():
                        print(f"⚡ {line.strip()}")
                    if not self.running:
                        break
            
            electron_thread = threading.Thread(target=monitor_electron, daemon=True)
            electron_thread.start()
            
            print("✅ Electron app started successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start Electron app: {e}")
            return False
    
    def cleanup(self):
        """Clean up processes"""
        print("\n🧹 Cleaning up...")
        self.running = False
        
        if self.email_service_process:
            try:
                self.email_service_process.terminate()
                self.email_service_process.wait(timeout=5)
                print("✅ Email service stopped")
            except:
                try:
                    self.email_service_process.kill()
                    print("🔪 Email service force killed")
                except:
                    pass
        
        if self.electron_process:
            try:
                self.electron_process.terminate()
                self.electron_process.wait(timeout=5)
                print("✅ Electron app stopped")
            except:
                try:
                    self.electron_process.kill()
                    print("🔪 Electron app force killed")
                except:
                    pass
    
    def run(self):
        """Main run method"""
        print("🎯 KNGS Email Progress Checker - Starting Application")
        print("=" * 60)
        
        # Set up signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            print(f"\n⚠️  Received signal {signum}, shutting down...")
            self.cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            # Check if we're in the right directory
            if not Path('package.json').exists():
                print("❌ package.json not found. Please run this script from the project root directory.")
                return False
            
            if not Path('email_service_interactive.py').exists():
                print("❌ email_service_interactive.py not found. Please ensure the email service file exists.")
                return False
            
            # Start email service first
            if not self.start_email_service():
                print("❌ Failed to start email service. Exiting.")
                return False
            
            # Give the email service a moment to fully initialize
            time.sleep(2)
            
            # Start Electron app
            if not self.start_electron_app():
                print("❌ Failed to start Electron app. Exiting.")
                self.cleanup()
                return False
            
            print("\n🎉 Application started successfully!")
            print("📧 Email service running on: http://127.0.0.1:5002")
            print("🖥️  Electron app will open automatically")
            print("🔐 When you first check an employee's emails, you'll see device code authentication")
            print("\n💡 Instructions:")
            print("   1. Upload an Excel file with employee data")
            print("   2. Go to 'Check Progress' tab")
            print("   3. Search for an employee and click 'Check Progress'")
            print("   4. Follow device code authentication when prompted")
            print("   5. View employee records and related emails")
            print("\n⚠️  Press Ctrl+C to stop all services")
            print("=" * 60)
            
            # Keep the main thread alive
            try:
                while self.running:
                    time.sleep(1)
                    
                    # Check if processes are still running
                    if self.email_service_process and self.email_service_process.poll() is not None:
                        print("⚠️  Email service stopped unexpectedly")
                        break
                    
                    if self.electron_process and self.electron_process.poll() is not None:
                        print("⚠️  Electron app stopped unexpectedly")
                        break
                        
            except KeyboardInterrupt:
                print("\n⚠️  Keyboard interrupt received")
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        finally:
            self.cleanup()
        
        return True

def main():
    """Main entry point"""
    runner = AppRunner()
    success = runner.run()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main() 