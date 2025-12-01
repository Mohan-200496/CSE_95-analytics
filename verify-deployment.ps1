# Punjab Rozgar Portal - Deployment Verification Script (PowerShell)
# This script helps verify the backend deployment and CORS configuration

Write-Host "Punjab Rozgar Portal - Deployment Verification" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

$BackendUrl = "https://cse-95-analytics.onrender.com"
$FrontendOrigin = "https://punjab-rozgar-portal1.onrender.com"

Write-Host "Testing backend availability..." -ForegroundColor Yellow

# Test 1: Health check
Write-Host "1. Testing health endpoint..." -ForegroundColor White
try {
    $healthResponse = Invoke-WebRequest -Uri "$BackendUrl/health" -Method GET -ErrorAction Stop
    if ($healthResponse.StatusCode -eq 200) {
        Write-Host "✅ Backend is online and healthy" -ForegroundColor Green
        $healthData = $healthResponse.Content | ConvertFrom-Json
        Write-Host "   Status: $($healthData.status)" -ForegroundColor Gray
    }
}
catch {
    Write-Host "❌ Backend health check failed" -ForegroundColor Red
    Write-Host "   The service might be sleeping (Render free tier) or there's a deployment issue" -ForegroundColor Yellow
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Login endpoint test
Write-Host "2. Testing login functionality..." -ForegroundColor White
try {
    $loginBody = @{
        email = "jobseeker@test.com"
        password = "jobseeker123"
    } | ConvertTo-Json

    $loginHeaders = @{
        "Content-Type" = "application/json"
        "Origin" = $FrontendOrigin
    }

    $loginResponse = Invoke-WebRequest -Uri "$BackendUrl/api/v1/auth/login" -Method POST -Body $loginBody -Headers $loginHeaders -ErrorAction Stop
    if ($loginResponse.StatusCode -eq 200) {
        Write-Host "✅ Login endpoint working" -ForegroundColor Green
        $loginData = $loginResponse.Content | ConvertFrom-Json
        Write-Host "   User: $($loginData.user.email) ($($loginData.user.role))" -ForegroundColor Gray
    }
}
catch {
    Write-Host "❌ Login endpoint failed" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. If backend is offline/sleeping: Visit $BackendUrl to wake it up" -ForegroundColor White
Write-Host "2. Test with: Open test-cors.html in a browser" -ForegroundColor White
Write-Host "3. Frontend test: https://punjab-rozgar-portal1.onrender.com" -ForegroundColor White

Write-Host ""
Write-Host "Test Credentials:" -ForegroundColor Cyan
Write-Host "   Job Seeker: jobseeker@test.com / jobseeker123" -ForegroundColor Gray
Write-Host "   Employer: employer@test.com / employer123" -ForegroundColor Gray
Write-Host "   Admin: admin@test.com / admin123" -ForegroundColor Gray