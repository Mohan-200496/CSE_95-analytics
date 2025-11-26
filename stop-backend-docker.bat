@echo off
echo Stopping Punjab Rozgar Backend Docker Container...
echo.

cd /d "%~dp0"

REM Stop the container
docker-compose down

echo.
echo Backend stopped successfully!
echo.
pause