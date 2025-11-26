@echo off
REM Cloud Deployment Helper for Punjab Rozgar Portal
echo 🌐 Punjab Rozgar Portal - Cloud Deployment Helper
echo ================================================

echo.
echo Select your preferred cloud platform:
echo.
echo 1. Heroku (Most Popular - Full-Stack)
echo 2. Vercel + Railway (Modern Stack - Best Performance)  
echo 3. Render (Simple - All-in-One)
echo 4. Manual Setup Guide
echo 5. Exit
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto heroku
if "%choice%"=="2" goto vercel_railway
if "%choice%"=="3" goto render
if "%choice%"=="4" goto manual
if "%choice%"=="5" goto exit

:heroku
echo.
echo 🚀 Setting up Heroku deployment...
echo.
echo Step 1: Make sure Heroku CLI is installed
echo Download from: https://devcenter.heroku.com/articles/heroku-cli
echo.
echo Step 2: Run these commands:
echo   heroku login
echo   heroku create punjab-rozgar-api
echo   heroku config:set DATABASE_URL="sqlite:///./punjab_rozgar.db" -a punjab-rozgar-api
echo   heroku config:set JWT_SECRET="your-secret-key" -a punjab-rozgar-api
echo   git add .
echo   git commit -m "Deploy to Heroku"
echo   git push heroku main
echo.
echo 📖 For detailed guide, see: heroku-deploy-guide.md
goto end

:vercel_railway
echo.
echo ⚡ Setting up Vercel + Railway deployment...
echo.
echo Frontend (Vercel):
echo   1. Visit https://vercel.com/new
echo   2. Connect your GitHub repository
echo   3. Set root directory to 'frontend'
echo   4. Deploy
echo.
echo Backend (Railway):
echo   1. Visit https://railway.app
echo   2. Connect GitHub repository
echo   3. Deploy from main branch
echo   4. Add PostgreSQL database
echo.
echo 📖 For detailed guide, see: vercel-railway-deploy-guide.md
goto end

:render
echo.
echo 🎯 Setting up Render deployment...
echo.
echo Steps:
echo   1. Visit https://render.com
echo   2. Sign up with GitHub
echo   3. Create Web Service from your repository
echo   4. Add PostgreSQL database
echo   5. Configure environment variables
echo.
echo Build Command: pip install -r backend/requirements.txt
echo Start Command: cd backend ^&^& uvicorn app.main:app --host 0.0.0.0 --port $PORT
echo.
echo 📖 For detailed guide, see: render-deploy-guide.md
goto end

:manual
echo.
echo 📚 Opening deployment guides...
if exist "heroku-deploy-guide.md" start heroku-deploy-guide.md
if exist "vercel-railway-deploy-guide.md" start vercel-railway-deploy-guide.md
if exist "render-deploy-guide.md" start render-deploy-guide.md
echo.
echo All deployment guides are now open!
goto end

:end
echo.
echo 🎉 Your Punjab Rozgar Portal is ready for cloud deployment!
echo.
echo Need help? Check the detailed guides created for you:
echo   - heroku-deploy-guide.md
echo   - vercel-railway-deploy-guide.md  
echo   - render-deploy-guide.md
echo.
pause

:exit
echo Goodbye! 👋