@echo off
echo =================================
echo Punjab Rozgar Backend - Docker Info
echo =================================
echo.

REM Get IP addresses
echo Your network IP addresses:
echo.
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    echo %%a
)

echo.
echo =================================
echo Docker Container Status:
echo =================================
docker-compose ps

echo.
echo =================================
echo Backend URLs:
echo =================================
echo Local Access: http://localhost:8000
echo API Docs: http://localhost:8000/api/docs
echo Health Check: http://localhost:8000/health
echo.

REM Get the actual IP for external access
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address" ^| findstr /v "127.0.0.1"') do (
    set "IP=%%a"
    set "IP=!IP: =!"
    echo External Access: http://!IP!:8000
    echo Frontend Config: const API_BASE_URL = 'http://!IP!:8000/api/v1';
    goto :done
)
:done

echo.
echo =================================
echo Container Logs (last 20 lines):
echo =================================
docker-compose logs --tail=20 punjab-rozgar-backend

pause