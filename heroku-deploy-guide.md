# 🚀 Heroku Deployment Guide - Punjab Rozgar Portal

## Prerequisites
- Heroku Account (free tier available)
- Git repository
- Heroku CLI installed

## Quick Deployment Steps

### 1. Install Heroku CLI
```bash
# Download from: https://devcenter.heroku.com/articles/heroku-cli
```

### 2. Login to Heroku
```bash
heroku login
```

### 3. Create Heroku Apps
```bash
# Backend API
heroku create punjab-rozgar-api

# Frontend (optional - can use static hosting)
heroku create punjab-rozgar-portal
```

### 4. Configure Environment Variables
```bash
# Set production environment variables
heroku config:set DATABASE_URL="sqlite:///./punjab_rozgar.db" -a punjab-rozgar-api
heroku config:set JWT_SECRET="your-super-secret-jwt-key-change-this" -a punjab-rozgar-api
heroku config:set ENVIRONMENT="production" -a punjab-rozgar-api
heroku config:set CORS_ORIGINS="https://punjab-rozgar-portal.herokuapp.com" -a punjab-rozgar-api
```

### 5. Deploy Backend
```bash
# From your project root
git subtree push --prefix backend heroku main

# Or if you want to deploy the whole project:
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### 6. Setup Database
```bash
# Run database migrations
heroku run python -m alembic upgrade head -a punjab-rozgar-api
```

### 7. View Your Deployed API
```bash
heroku open -a punjab-rozgar-api
```

## Frontend Deployment Options

### Option A: Deploy with Backend (Serve Static Files)
- Backend serves frontend files automatically
- Single app deployment
- Access via: https://punjab-rozgar-api.herokuapp.com

### Option B: Separate Static Deployment
- Deploy frontend to Vercel/Netlify (recommended)
- Better performance for static assets
- CDN distribution

## Post-Deployment
1. Test all endpoints at: https://punjab-rozgar-api.herokuapp.com/docs
2. Update frontend API URLs to point to Heroku backend
3. Test complete user flows

## Cost Estimation
- **Free Tier**: Good for testing/demo (sleeps after 30 min)
- **Hobby ($7/month)**: 24/7 uptime, custom domains
- **Production**: Starts at $25/month with PostgreSQL

## Troubleshooting
```bash
# View logs
heroku logs --tail -a punjab-rozgar-api

# Check app status
heroku ps -a punjab-rozgar-api

# Access console
heroku run python -a punjab-rozgar-api
```