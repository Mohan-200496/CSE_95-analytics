#!/bin/bash
# Git Commands for Punjab Rozgar Portal
# Run these commands in Git Bash

echo "🚀 Pushing Punjab Rozgar Portal to GitHub"
echo "========================================="

# 1. Initialize git repository (if not already done)
echo "📁 Initializing Git repository..."
git init

# 2. Add all files to staging
echo "📦 Adding all files to staging..."
git add .

# 3. Check what files are being added
echo "📋 Files to be committed:"
git status

# 4. Create initial commit
echo "💾 Creating commit..."
git commit -m "🎉 Initial commit: Punjab Rozgar Portal with monochromatic theme and cloud deployment setup

✨ Features:
- Complete job portal with FastAPI backend
- Professional monochromatic black/white/gray theme
- JWT authentication system
- Comprehensive analytics engine
- Docker containerization
- Multi-cloud deployment configurations (Heroku, Vercel, Railway, Render)
- Admin dashboard and user management
- Job search, applications, and recommendations
- Real-time notifications and email system

🔧 Tech Stack:
- Backend: FastAPI, SQLAlchemy, SQLite/PostgreSQL
- Frontend: Vanilla JavaScript, HTML5, CSS3
- Analytics: Chart.js, custom tracking system
- Deployment: Docker, Nginx, multi-platform ready

📱 Pages Included:
- Landing page with hero section
- Job browsing and search
- User authentication (login/register)
- Jobseeker dashboard and profile
- Employer dashboard and job posting
- Admin panel with analytics
- Contact and static pages
- Deployment health checker

🌐 Ready for deployment on:
- Heroku (full-stack)
- Vercel + Railway (modern stack)
- Render (simple setup)
- VPS with Nginx configuration"

# 5. Add remote origin (replace with your repository URL)
echo "🔗 Setting up remote repository..."
echo "⚠️  IMPORTANT: Replace 'your-username' and 'your-repo-name' with actual values!"
echo ""
echo "If you haven't created a GitHub repository yet:"
echo "1. Go to https://github.com/new"
echo "2. Create a repository named 'punjab-rozgar-portal' or similar"
echo "3. Copy the repository URL"
echo "4. Run: git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git"
echo ""

# Example - uncomment and modify with your actual repo URL:
# git remote add origin https://github.com/Mohan-200496/punjab-rozgar-portal.git

# 6. Push to GitHub
echo "🚢 Pushing to GitHub main branch..."
echo "Run this after setting up the remote:"
echo "git push -u origin main"

echo ""
echo "✅ All commands ready!"
echo "📖 For detailed deployment after pushing, see:"
echo "   - heroku-deploy-guide.md"
echo "   - vercel-railway-deploy-guide.md"
echo "   - render-deploy-guide.md"