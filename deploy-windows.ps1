# Punjab Rozgar Portal - Windows Deployment Script
# Run this script to quickly deploy the complete system

Write-Host "🚀 Punjab Rozgar Portal - Quick Deployment" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Function to print colored output
function Write-Info { 
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green 
}

function Write-Warning { 
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow 
}

function Write-Error { 
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red 
}

try {
    # Step 1: Check Python installation
    Write-Info "Checking Python installation..."
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Info "Python found: $pythonVersion"
    } else {
        Write-Error "Python not found. Please install Python 3.8 or higher."
        exit 1
    }

    # Step 2: Install backend dependencies
    Write-Info "Installing backend dependencies..."
    Set-Location -Path "backend"
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install dependencies"
        exit 1
    }
    Set-Location -Path ".."

    # Step 3: Start backend server in background
    Write-Info "Starting backend server..."
    Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload" -WorkingDirectory "backend" -WindowStyle Hidden

    # Wait for backend to start
    Write-Info "Waiting for backend to initialize..."
    Start-Sleep -Seconds 5

    # Step 4: Create test users
    Write-Info "Creating test users..."
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/auth/create-test-users" -Method GET -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Info "Test users created successfully"
        }
    } catch {
        Write-Warning "Could not create test users: $($_.Exception.Message)"
    }

    # Step 5: Start frontend server
    Write-Info "Starting frontend server..."
    Start-Process -FilePath "python" -ArgumentList "-m", "http.server", "3000" -WorkingDirectory "frontend" -WindowStyle Hidden

    # Step 6: Open browsers
    Write-Info "Opening browser tabs..."
    Start-Sleep -Seconds 2
    Start-Process "http://127.0.0.1:8000"
    Start-Process "http://127.0.0.1:8000/docs"
    Start-Process "http://127.0.0.1:3000"

    Write-Host ""
    Write-Host "🎉 Punjab Rozgar Portal is ready!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📧 Test Credentials:" -ForegroundColor Cyan
    Write-Host "   Admin:    admin@test.com / admin123" -ForegroundColor White
    Write-Host "   Employer: employer@test.com / employer123" -ForegroundColor White  
    Write-Host "   Seeker:   jobseeker@test.com / jobseeker123" -ForegroundColor White
    Write-Host ""
    Write-Host "🌐 Access Points:" -ForegroundColor Cyan
    Write-Host "   Backend API: http://127.0.0.1:8000" -ForegroundColor White
    Write-Host "   API Docs:    http://127.0.0.1:8000/docs" -ForegroundColor White
    Write-Host "   Frontend:    http://127.0.0.1:3000" -ForegroundColor White
    Write-Host ""
    Write-Host "⚠️  To stop servers later, close the Python processes in Task Manager" -ForegroundColor Yellow

} catch {
    Write-Error "Deployment failed: $($_.Exception.Message)"
    exit 1
}