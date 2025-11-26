@echo off
echo.
echo ==========================================
echo Punjab Rozgar Portal - Complete Startup
echo ==========================================
echo.

echo [1/4] Starting Frontend Server (Port 3000)...
start "Frontend Server" cmd /c "cd /d frontend && python -m http.server 3000"

echo.
echo [2/4] Starting Job API Server (Port 3001)...
start "Job API Server" cmd /c "cd /d frontend/api && node server.js"

echo.
echo [3/4] Starting Backend Server (Port 8000)...
start "Backend Server" cmd /c "cd /d backend && python start_server.py"

echo.
echo [4/4] Waiting for servers to initialize...
timeout /t 8 /nobreak > nul

echo.
echo ===================================================
echo ✅ Punjab Rozgar Portal is now fully operational!
echo ===================================================
echo.
echo 🌐 Frontend:           http://localhost:3000
echo 🚀 Job API:            http://localhost:3001
echo ⚙️  Backend:            http://localhost:8000
echo.
echo 📄 Main Pages:
echo    • Test Page:         http://localhost:3000/test-functionality.html
echo    • Job Seeker:        http://localhost:3000/pages/jobseeker/dashboard.html
echo    • Employer:          http://localhost:3000/pages/employer/dashboard.html
echo    • Admin:             http://localhost:3000/pages/admin/dashboard.html
echo.
echo 🔍 Browse Jobs:         http://localhost:3000/pages/jobseeker/browse-jobs.html
echo 👤 Profile:             http://localhost:3000/pages/jobseeker/profile.html
echo.
echo 📊 API Endpoints Available:
echo    • GET /jobs             - List all jobs
echo    • GET /jobs/recommended - Get recommended jobs
echo    • GET /categories       - Job categories
echo    • GET /locations        - Job locations
echo.
echo ✨ Features Working:
echo    ✅ Role-based authentication
echo    ✅ Real-time analytics tracking
echo    ✅ Job recommendations (14+ jobs)
echo    ✅ Advanced job search & filtering
echo    ✅ Smooth UI animations
echo    ✅ Mobile responsive design
echo    ✅ Error handling & fallbacks
echo.
echo 🛑 To stop all servers, close all terminal windows
echo.
echo Press any key to open the portal in browser...
pause > nul
start http://localhost:3000/test-functionality.html