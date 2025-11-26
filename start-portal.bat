@echo off
echo Starting Punjab Rozgar Portal...

echo.
echo Starting Frontend Server on port 3000...
start "Frontend Server" cmd /c "cd /d frontend && python -m http.server 3000"

echo.
echo Starting Backend Server on port 8000...
start "Backend Server" cmd /c "cd /d backend && python start_server.py"

echo.
echo Waiting for servers to start...
timeout /t 5 /nobreak > nul

echo.
echo ===================================
echo Punjab Rozgar Portal is now running!
echo ===================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo Test Page: http://localhost:3000/test-functionality.html
echo.
echo Job Seeker Dashboard: http://localhost:3000/pages/jobseeker/dashboard.html
echo Employer Dashboard:   http://localhost:3000/pages/employer/dashboard.html
echo Admin Dashboard:      http://localhost:3000/pages/admin/dashboard.html
echo.
echo Press any key to exit...
pause > nul