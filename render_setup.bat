@echo off
echo.
echo 🚀 Punjab Rozgar Portal - Render PostgreSQL Setup
echo ==================================================
echo.
echo 📋 Pre-Setup Checklist:
echo ✅ Render account created
echo ✅ Frontend deployed on Render
echo ✅ Backend deployed on Render
echo ⏳ PostgreSQL database (this guide)
echo.
echo 🗄️ Step 1: Create PostgreSQL Database
echo --------------------------------------
echo 1. Go to: https://dashboard.render.com
echo 2. Click 'New' → 'PostgreSQL'
echo 3. Configure:
echo    Name: punjab-rozgar-db
echo    Database: punjab_rozgar
echo    User: (auto-generated)
echo    Plan: Free (or preferred)
echo    Region: Same as backend service
echo.
echo 🔧 Step 2: Get Connection Details
echo ---------------------------------
echo After database creation, copy from Render dashboard:
echo 📋 Internal Database URL (recommended for backend)
echo 📋 External Database URL (for external tools)
echo.
echo ⚙️ Step 3: Configure Backend Service
echo ------------------------------------
echo In your backend service environment variables:
echo DATABASE_URL=postgresql://user:password@host:5432/database
echo SECRET_KEY=your-super-secret-key-here
echo ALGORITHM=HS256
echo ACCESS_TOKEN_EXPIRE_MINUTES=30
echo RENDER=true
echo DEBUG=false
echo ENVIRONMENT=production
echo.
echo 🚀 Step 4: Deploy and Test
echo -------------------------
echo 1. Push code changes to Git repository
echo 2. Render auto-deploys backend
echo 3. Monitor deployment logs
echo 4. Test database connection
echo.
echo ✅ Step 5: Verification
echo ----------------------
echo Run health check: python health_check.py
echo Check service logs for 'Database connection successful'
echo.
echo 🎉 Your PostgreSQL database will provide:
echo ✅ Persistent storage
echo ✅ Better performance
echo ✅ Automatic backups
echo ✅ Analytics capabilities
echo.
echo Press any key to continue...
pause >nul