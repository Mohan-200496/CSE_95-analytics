# 🚀 Vercel + Railway Deployment Guide

## Why This Stack?
- **Vercel**: Lightning-fast frontend with global CDN
- **Railway**: Modern backend hosting with PostgreSQL
- **Best Performance**: Optimized for modern web apps

## Part 1: Deploy Backend to Railway

### 1. Setup Railway Account
- Visit: https://railway.app
- Sign up with GitHub
- Connect your repository

### 2. Deploy Backend
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create new project
railway new punjab-rozgar-api

# Deploy
railway up
```

### 3. Configure Environment Variables in Railway Dashboard
```env
DATABASE_URL=postgresql://...  # Railway provides this automatically
JWT_SECRET=your-super-secret-key
ENVIRONMENT=production
CORS_ORIGINS=https://your-frontend-domain.vercel.app
```

### 4. Setup PostgreSQL (Automatic with Railway)
- Railway automatically provisions PostgreSQL
- Database URL provided in environment variables
- Auto-backup and scaling included

## Part 2: Deploy Frontend to Vercel

### 1. Prepare Frontend for Deployment
```bash
# Update API endpoints in your frontend config
# Point to Railway backend URL
```

### 2. Deploy to Vercel
```bash
# Install Vercel CLI
npm install -g vercel

# From frontend directory
cd frontend
vercel

# Or deploy via GitHub integration (recommended)
# Connect repository at: https://vercel.com/new
```

### 3. Configure Environment Variables
```env
NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app
NEXT_PUBLIC_ENVIRONMENT=production
```

## Part 3: Connect Frontend to Backend

### Update API Configuration
```javascript
// In frontend/config/environment.js
const API_BASE_URL = 'https://punjab-rozgar-api.up.railway.app';
```

## Benefits of This Setup
✅ **Global CDN**: Vercel serves frontend worldwide  
✅ **Auto-scaling**: Railway scales backend automatically  
✅ **PostgreSQL**: Production-grade database included  
✅ **HTTPS**: SSL certificates automatically managed  
✅ **Git Integration**: Deploy on every push  
✅ **Custom Domains**: Easy to add your own domain  

## Cost Estimation
- **Vercel**: Free for personal projects, $20/month for team
- **Railway**: $5-20/month based on usage
- **Total**: ~$25/month for production-ready setup

## Post-Deployment Checklist
1. Test API endpoints via Railway URL
2. Verify frontend loads from Vercel
3. Test complete user authentication flow
4. Check analytics tracking functionality
5. Verify database connectivity