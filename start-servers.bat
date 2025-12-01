@echo off
REM Punjab Rozgar Portal - Quick Start Script
REM This script starts both backend and frontend servers

echo.
echo 🚀 Punjab Rozgar Portal - Quick Start
echo =====================================
echo.

REM Start backend server
echo [INFO] Starting backend server...
cd backend
start /B python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
cd ..

REM Wait for backend to initialize
echo [INFO] Waiting for backend to initialize...
timeout /t 3 /nobreak > nul

REM Start frontend server  
echo [INFO] Starting frontend server...
cd frontend
start /B python -m http.server 3000
cd ..

REM Wait a moment then open browsers
echo [INFO] Opening browser tabs...
timeout /t 2 /nobreak > nul

start http://127.0.0.1:8000
start http://127.0.0.1:8000/docs  
start http://127.0.0.1:3000

echo.
echo 🎉 Punjab Rozgar Portal is ready!
echo.
echo 📧 Test Credentials:
echo    Admin:    admin@test.com / admin123
echo    Employer: employer@test.com / employer123  
echo    Seeker:   jobseeker@test.com / jobseeker123
echo.
echo 🌐 Access Points:
echo    Backend API: http://127.0.0.1:8000
echo    API Docs:    http://127.0.0.1:8000/docs
echo    Frontend:    http://127.0.0.1:3000
echo.
echo ⚠️ Keep this window open to keep servers running
echo Press Ctrl+C to stop servers
pause