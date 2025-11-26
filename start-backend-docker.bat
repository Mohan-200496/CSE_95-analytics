@echo off
echo Building Punjab Rozgar Backend Docker Container...
echo.

REM Navigate to project root
cd /d "%~dp0"

REM Build the Docker image
echo Building Docker image...
docker-compose build punjab-rozgar-backend

if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to build Docker image
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Docker image built successfully!
echo.

REM Start the container
echo Starting Punjab Rozgar Backend...
docker-compose up punjab-rozgar-backend

echo.
echo Backend is running!
echo API available at: http://localhost:8000
echo API Documentation: http://localhost:8000/api/docs
echo Health Check: http://localhost:8000/health
echo.

pause