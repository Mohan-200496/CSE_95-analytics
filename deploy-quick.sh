#!/bin/bash
# Quick deployment script for Punjab Rozgar Portal
set -e

echo "🚀 Punjab Rozgar Portal - Quick Deployment"
echo "=========================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Windows
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    print_status "Windows detected - using PowerShell commands"
    PYTHON_CMD="python"
    PIP_CMD="pip"
else
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
fi

# Step 1: Install dependencies
print_status "Installing dependencies..."
cd backend
$PIP_CMD install -r requirements.txt
cd ..

# Step 2: Initialize database
print_status "Initializing database..."
cd backend
$PYTHON_CMD -c "
import asyncio
import sys
import os
sys.path.append('.')

from app.core.database import create_tables
from app.models import *

async def init_db():
    try:
        await create_tables()
        print('✅ Database tables created successfully')
    except Exception as e:
        print(f'❌ Database initialization failed: {e}')

asyncio.run(init_db())
"
cd ..

# Step 3: Create test users
print_status "Creating test users..."
cd backend
$PYTHON_CMD -c "
import requests
import time

# Wait for server to be ready
print('Waiting for server...')
time.sleep(2)

try:
    response = requests.get('http://127.0.0.1:8000/api/v1/auth/create-test-users', timeout=10)
    if response.status_code == 200:
        print('✅ Test users created successfully')
    else:
        print(f'⚠️ Test users response: {response.status_code}')
except Exception as e:
    print(f'❌ Could not create test users: {e}')
"
cd ..

print_status "Deployment completed!"
echo ""
echo "🎉 Punjab Rozgar Portal is ready!"
echo ""
echo "📧 Test Credentials:"
echo "   Admin:    admin@test.com / admin123"
echo "   Employer: employer@test.com / employer123"
echo "   Seeker:   jobseeker@test.com / jobseeker123"
echo ""
echo "🌐 Access Points:"
echo "   Backend API: http://127.0.0.1:8000"
echo "   API Docs:    http://127.0.0.1:8000/docs"
echo "   Frontend:    http://127.0.0.1:3000"
echo ""
echo "🚀 To start the servers:"
echo "   Backend:  cd backend && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
echo "   Frontend: cd frontend && python -m http.server 3000"