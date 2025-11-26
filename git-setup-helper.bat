@echo off
echo ========================================
echo   CSE_95 Analytics - Git Setup Helper
echo ========================================
echo.

echo Please follow these steps:
echo.
echo 1. Install Git from: https://git-scm.com/download/windows
echo 2. Restart your command prompt/PowerShell
echo 3. Run this batch file again
echo.

pause

REM Check if git is now available
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Git is not yet available. Please install Git and restart your terminal.
    echo Download from: https://git-scm.com/download/windows
    pause
    exit /b 1
)

echo Git is now available! Continuing with setup...

cd /d "d:\cap pro\last\capstone-analytics"
git init
git add .
git commit -m "Initial commit: CSE_95 Analytics - Punjab Rozgar Portal"

echo.
echo Repository initialized! Now create your GitHub repository:
echo.
echo 1. Go to https://github.com/new
echo 2. Repository name: CSE_95-analytics  
echo 3. Make it PUBLIC
echo 4. Don't initialize with README
echo 5. Click "Create repository"
echo.

set /p username="Enter your GitHub username: "
git remote add origin https://github.com/%username%/CSE_95-analytics.git
git branch -M main

echo.
echo Ready to push! Make sure you created the GitHub repository first.
set /p confirm="Press Y to push to GitHub: "

if /i "%confirm%"=="Y" (
    git push -u origin main
    echo.
    echo SUCCESS! Your repository is now at:
    echo https://github.com/%username%/CSE_95-analytics
) else (
    echo You can push later with: git push -u origin main
)

pause