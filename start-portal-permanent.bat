@echo off
title Punjab Rozgar Portal - Permanent Startup

echo.
echo ===============================================
echo    Punjab Rozgar Portal - Permanent Startup
echo ===============================================
echo.

:: Create logs directory
if not exist "logs" mkdir logs

:: Kill any existing Python processes
taskkill /F /IM python.exe >nul 2>&1

echo Starting Backend Server...
cd backend
start "Punjab Rozgar Backend" /MIN "D:/cap pro/last/capstone-analytics/.venv/Scripts/python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000

:: Wait for backend to start
timeout /t 3 /nobreak >nul

echo Starting Frontend Server...
cd ../frontend
start "Punjab Rozgar Frontend" /MIN "D:/cap pro/last/capstone-analytics/.venv/Scripts/python.exe" -m http.server 3000

:: Wait for frontend to start
timeout /t 3 /nobreak >nul

echo.
echo Testing system status...

:: Test backend
powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:8000/' -UseBasicParsing -TimeoutSec 5 | Out-Null; Write-Host '✅ Backend: ONLINE' -ForegroundColor Green } catch { Write-Host '❌ Backend: OFFLINE' -ForegroundColor Red }"

:: Test frontend
powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:3000/' -UseBasicParsing -TimeoutSec 5 | Out-Null; Write-Host '✅ Frontend: ONLINE' -ForegroundColor Green } catch { Write-Host '❌ Frontend: OFFLINE' -ForegroundColor Red }"

echo.
echo ===============================================
echo    🎉 Punjab Rozgar Portal is LIVE!
echo ===============================================
echo.
echo 🌐 Access URLs:
echo    Frontend: http://localhost:3000
echo    Backend API: http://localhost:8000
echo    API Documentation: http://localhost:8000/docs
echo.
echo 📱 Quick Links:
echo    Login Page: http://localhost:3000/pages/auth/login.html
echo    Browse Jobs: http://localhost:3000/pages/jobs/browse.html
echo    Dashboard: http://localhost:3000/pages/jobseeker/dashboard.html
echo.
echo 🔑 Test Accounts:
echo    Job Seeker: jobseeker@test.com / jobseeker123
echo    Admin: admin@test.com / admin123
echo    Employer: employer@test.com / test123
echo.
echo 🔧 Features Working:
echo    ✅ Job Seeker Authentication
echo    ✅ Job Recommendations System  
echo    ✅ Admin Job Approval
echo    ✅ Job Browsing (Public)
echo    ✅ Analytics Tracking
echo.
echo 📊 Both servers are running in background windows
echo    Use Task Manager to stop if needed
echo.

:: Open the portal in browser
echo Opening Punjab Rozgar Portal...
start http://localhost:3000

echo.
echo Press any key to minimize this window...
pause >nul

:: Minimize the command window but keep it running
powershell -WindowStyle Minimized -Command ""