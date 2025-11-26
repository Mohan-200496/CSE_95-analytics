@echo off
echo ========================================
echo   CSE_95 Analytics - GitHub Desktop Setup
echo ========================================
echo.

echo This script will help you prepare your project for GitHub Desktop upload.
echo.

echo STEP 1: Download GitHub Desktop
echo ----------------------------------------
echo 1. Go to: https://desktop.github.com/
echo 2. Download GitHub Desktop for Windows
echo 3. Install and sign in with your GitHub account
echo.

echo STEP 2: Create Repository on GitHub.com
echo ----------------------------------------
echo 1. Go to: https://github.com/new
echo 2. Repository name: CSE_95-analytics
echo 3. Description: Punjab Rozgar Analytics Portal - Employment analytics platform
echo 4. Make it PUBLIC
echo 5. DON'T initialize with README (we have our own)
echo 6. Click "Create repository"
echo.

echo STEP 3: Clone Repository with GitHub Desktop
echo ----------------------------------------
echo 1. Open GitHub Desktop
echo 2. Click "Clone a repository from the Internet"
echo 3. Find your CSE_95-analytics repository
echo 4. Choose a local folder (NOT this current folder)
echo 5. Click "Clone"
echo.

echo STEP 4: Copy Project Files
echo ----------------------------------------
echo Current project location: %cd%
echo.
echo Copy ALL files from this folder to your cloned repository folder:
echo.
echo Files to copy:
echo ✅ backend/ (entire folder)
echo ✅ frontend/ (entire folder)  
echo ✅ README.md
echo ✅ LICENSE
echo ✅ .gitignore
echo ✅ CONTRIBUTING.md
echo ✅ CHANGELOG.md
echo ✅ docker-compose.yml
echo ✅ All .bat files
echo.

echo STEP 5: Commit and Push
echo ----------------------------------------
echo 1. GitHub Desktop will show all your new files
echo 2. Add commit message: "Initial commit: CSE_95 Analytics - Punjab Rozgar Portal"
echo 3. Click "Commit to main"
echo 4. Click "Push origin"
echo.

echo ========================================
echo   Project Ready for Upload!
echo ========================================
echo.
echo Your repository structure:
echo 📂 CSE_95-analytics/
echo ├── 📂 backend/                 # FastAPI Backend (Python)
echo │   ├── app/                    # Application code
echo │   ├── requirements.txt        # Python dependencies
echo │   └── Dockerfile             # Container config
echo ├── 📂 frontend/                # Frontend Application
echo │   ├── index.html             # Landing page
echo │   ├── pages/                 # Application pages
echo │   ├── js/                    # JavaScript modules
echo │   ├── api/                   # Node.js API server
echo │   └── assets/               # Static resources
echo ├── 📄 README.md               # Professional documentation
echo ├── 📄 LICENSE                 # MIT License
echo ├── 📄 .gitignore              # Git ignore rules
echo ├── 📄 CONTRIBUTING.md         # Contribution guidelines
echo ├── 📄 CHANGELOG.md            # Version history
echo ├── 📄 docker-compose.yml      # Container orchestration
echo └── 📄 *.bat                   # Helper scripts
echo.

echo Repository Features:
echo ✅ 1,200+ Jobs across 8 categories
echo ✅ Real-time analytics engine
echo ✅ Mobile-responsive design
echo ✅ Docker containerization
echo ✅ Professional documentation
echo ✅ MIT License (open source)
echo.

echo After upload, your repository will be available at:
echo https://github.com/YOURUSERNAME/CSE_95-analytics
echo.

pause