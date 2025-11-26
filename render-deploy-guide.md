# 🚀 Render Deployment Guide - Punjab Rozgar Portal

## Why Render?
- **Simple Setup**: Git-based deployment
- **Free Tier**: Good for testing
- **Built-in PostgreSQL**: Database included
- **Auto HTTPS**: SSL certificates managed
- **Great for Full-Stack**: Backend + Frontend in one place

## Deployment Steps

### 1. Prepare Your Repository
```bash
# Ensure your code is pushed to GitHub
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Deploy Backend (Web Service)

#### Via Render Dashboard:
1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure service:

```yaml
Name: punjab-rozgar-api
Environment: Python 3
Build Command: pip install -r backend/requirements.txt
Start Command: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### Environment Variables:
```env
PYTHON_VERSION=3.11
DATABASE_URL=$DATABASE_URL  # Render provides this
JWT_SECRET=your-super-secret-key-change-this
ENVIRONMENT=production
```

### 3. Deploy Database (PostgreSQL)
1. In Render Dashboard: "New +" → "PostgreSQL"
2. Name: `punjab-rozgar-db`
3. Copy the Internal Database URL
4. Add to your web service environment variables

### 4. Deploy Frontend (Static Site)
1. "New +" → "Static Site"
2. Connect same repository
3. Configure:

```yaml
Name: punjab-rozgar-portal
Build Command: # Leave empty for static HTML
Publish Directory: frontend
```

### 5. Update Frontend Configuration
```javascript
// Update frontend/config/environment.js
const API_BASE_URL = 'https://punjab-rozgar-api.onrender.com';
```

## Alternative: Render Blueprint (One-Click Deploy)

Create `render.yaml` in your project root:

```yaml
services:
  - type: web
    name: punjab-rozgar-api
    env: python
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: punjab-rozgar-db
          property: connectionString
      - key: JWT_SECRET
        generateValue: true
      - key: ENVIRONMENT
        value: production

  - type: pserv
    name: punjab-rozgar-db
    databaseName: punjab_rozgar
    databaseUser: admin

databases:
  - name: punjab-rozgar-db
    databaseName: punjab_rozgar
    user: admin
```

## Post-Deployment

### 1. Run Database Migrations
```bash
# In Render shell (available in dashboard)
python -m alembic upgrade head
```

### 2. Create Admin User
```bash
# Run the admin promotion script
python scripts/promote_admin.py
```

### 3. Test Your Deployment
- API Docs: https://punjab-rozgar-api.onrender.com/docs
- Frontend: https://punjab-rozgar-portal.onrender.com
- Health Check: https://punjab-rozgar-api.onrender.com/health

## Benefits
✅ **Free Tier**: 750 hours/month free  
✅ **Auto-Deploy**: Deploys on git push  
✅ **Managed Database**: PostgreSQL included  
✅ **HTTPS**: SSL automatically configured  
✅ **Monitoring**: Built-in logs and metrics  
✅ **Custom Domains**: Easy to add  

## Cost Estimation
- **Free Tier**: Good for development/testing
- **Starter**: $7/month for web service + $7/month for database
- **Total**: ~$14/month for production setup

## Troubleshooting
- View logs in Render dashboard
- Use shell access for debugging
- Monitor resource usage in dashboard