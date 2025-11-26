@echo off
echo ========================================
echo   Punjab Rozgar API Server Starter
echo ========================================
echo.
echo Starting Job API Server...
echo.
cd /d "d:\cap pro\last\capstone-analytics\frontend\api"
echo Current directory: %cd%
echo.
echo Checking if Node.js is installed...
node --version
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)
echo.
echo Starting server on port 3001...
echo.
echo ========================================
echo   Server will run on:
echo   http://localhost:3001
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.
node server.js
echo.
echo Server stopped.
pause