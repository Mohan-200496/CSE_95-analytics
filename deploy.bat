@echo off
REM Quick deployment script for Punjab Rozgar Portal (Windows)

echo 🚀 Punjab Rozgar Portal - Quick Deploy
echo ======================================

REM Check if Docker Desktop is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop.
    pause
    exit /b 1
)

echo ✅ Docker is running

REM Check if docker-compose.yml exists
if not exist docker-compose.yml (
    echo ❌ docker-compose.yml not found. Run this script from project root.
    pause
    exit /b 1
)

echo 📦 Building and starting services...
docker-compose up -d

echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check if backend is responding
echo 🔍 Checking backend health...
curl -f http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Backend may still be starting...
) else (
    echo ✅ Backend is healthy
)

echo.
echo 🎉 Deployment Complete!
echo ========================
echo 📱 Frontend: Open frontend/index.html in browser
echo 🚀 Backend API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo 📊 View logs: docker-compose logs -f
echo 🛑 Stop services: docker-compose down
echo.
echo Press any key to open the application...
pause >nul

REM Open the application in default browser
start "" "frontend/index.html"