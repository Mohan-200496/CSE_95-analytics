@echo off
echo ========================================
echo   CSE_95 Analytics - GitHub Setup
echo ========================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git is not installed or not in PATH
    echo Please install Git from https://git-scm.com/
    pause
    exit /b 1
)

echo Git is installed successfully!
echo.

echo Current directory: %cd%
echo.

echo ========================================
echo   Step 1: Initialize Git Repository
echo ========================================
git init
git add .
git commit -m "Initial commit: CSE_95 Analytics - Punjab Rozgar Portal"

echo.
echo ========================================
echo   Step 2: GitHub Repository Setup
echo ========================================
echo.
echo MANUAL STEPS REQUIRED:
echo.
echo 1. Go to GitHub.com and sign in to your account
echo 2. Click "New Repository" or go to: https://github.com/new
echo 3. Repository name: CSE_95-analytics
echo 4. Description: Punjab Rozgar Analytics Portal - Employment analytics platform for Punjab state
echo 5. Make sure it's PUBLIC
echo 6. DO NOT initialize with README (we already have files)
echo 7. Click "Create repository"
echo.
echo After creating the repository, GitHub will show you commands like:
echo   git remote add origin https://github.com/YOURUSERNAME/CSE_95-analytics.git
echo   git branch -M main
echo   git push -u origin main
echo.

set /p username="Enter your GitHub username: "
echo.

echo ========================================
echo   Step 3: Add Remote and Push
echo ========================================

REM Add remote origin
git remote add origin https://github.com/%username%/CSE_95-analytics.git

REM Rename branch to main
git branch -M main

echo.
echo Ready to push to GitHub!
echo Repository URL: https://github.com/%username%/CSE_95-analytics.git
echo.

set /p confirm="Press Y to push to GitHub (make sure you created the repository first): "
if /i "%confirm%"=="Y" (
    echo Pushing to GitHub...
    git push -u origin main
    echo.
    echo ========================================
    echo   SUCCESS! 
    echo ========================================
    echo.
    echo Your repository is now available at:
    echo https://github.com/%username%/CSE_95-analytics
    echo.
    echo Repository features:
    echo ✅ Complete source code
    echo ✅ Professional README with badges
    echo ✅ MIT License
    echo ✅ Contributing guidelines  
    echo ✅ Proper .gitignore
    echo ✅ Changelog documentation
    echo.
    echo Next steps:
    echo 1. Visit your repository on GitHub
    echo 2. Add repository description and topics
    echo 3. Enable GitHub Pages if you want to host the frontend
    echo 4. Add collaborators if working in a team
    echo 5. Star your own repository! ⭐
    echo.
) else (
    echo.
    echo Push cancelled. You can manually push later with:
    echo git push -u origin main
    echo.
)

echo.
echo Repository structure uploaded:
echo 📂 CSE_95-analytics/
echo ├── 📂 backend/                 (FastAPI Backend)
echo ├── 📂 frontend/                (Frontend Application)  
echo ├── 📄 README.md                (Professional documentation)
echo ├── 📄 LICENSE                  (MIT License)
echo ├── 📄 .gitignore               (Git ignore rules)
echo ├── 📄 CONTRIBUTING.md          (Contribution guidelines)
echo ├── 📄 CHANGELOG.md             (Version history)
echo ├── 📄 docker-compose.yml       (Container orchestration)
echo └── 📄 start-api-server.bat     (Quick start script)
echo.

pause