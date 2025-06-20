#!/bin/bash

# KNGS Email Progress Checker - Run Script
# This script starts both the email service and Electron app

echo "🎯 KNGS Email Progress Checker"
echo "Starting application..."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed."
    exit 1
fi

# Run the Python app runner
python3 run_app.py 