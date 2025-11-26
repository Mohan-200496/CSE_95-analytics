# Punjab Rozgar Portal - Deployment Guide

## 🚀 Deployment Options

### Option 1: Local Development (Recommended for Testing)

#### Quick Start with Batch Files
```bash
# Start the backend
start-backend-docker.bat

# Or manually:
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Setup
```bash
cd frontend
# Serve with Python (simple)
python -m http.server 8080

# Or with Node.js (for API features)
cd api
node server.js
```

Access:
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

### Option 2: Docker Deployment (Production Ready)

#### Prerequisites
- Docker Desktop installed
- Docker Compose available

#### Deploy with Docker Compose
```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### Custom Docker Build
```bash
# Build backend image
cd backend
docker build -t punjab-rozgar-backend .

# Run container
docker run -d \
  --name punjab-rozgar-api \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  punjab-rozgar-backend
```

---

### Option 3: Cloud Deployment

#### A) Vercel (Frontend Only)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy frontend
cd frontend
vercel --prod
```

#### B) Railway (Full Stack)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

#### C) Render (Full Stack)
1. Connect GitHub repository to Render
2. Create Web Service for backend:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Create Static Site for frontend:
   - Publish Directory: `frontend`

#### D) Heroku (Backend)
```bash
# Install Heroku CLI
heroku create punjab-rozgar-api

# Add Procfile
echo "web: uvicorn app.main:app --host 0.0.0.0 --port \$PORT" > backend/Procfile

# Deploy
git subtree push --prefix=backend heroku main
```

---

### Option 4: VPS/Server Deployment

#### Prerequisites
- Ubuntu 20.04+ server
- Domain name (optional)
- SSL certificate (recommended)

#### Setup Script
```bash
#!/bin/bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip nginx docker.io docker-compose

# Clone repository
git clone https://github.com/yourusername/CSE_95-analytics.git
cd CSE_95-analytics

# Start with Docker
docker-compose up -d

# Configure Nginx (optional)
sudo cp nginx.conf /etc/nginx/sites-available/punjab-rozgar
sudo ln -s /etc/nginx/sites-available/punjab-rozgar /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

---

## 🔧 Environment Configuration

### Backend Environment Variables
Create `backend/.env`:
```env
DATABASE_URL=sqlite:///./data/punjab_rozgar.db
SECRET_KEY=your-secret-key-here
ANALYTICS_ENABLED=true
DEBUG=false
ENVIRONMENT=production
CORS_ORIGINS=["https://yourdomain.com"]
```

### Frontend Configuration
Update `frontend/config/environment.js`:
```javascript
const config = {
    API_BASE_URL: 'https://your-backend-url.com',
    ANALYTICS_ENABLED: true,
    ENVIRONMENT: 'production'
};
```

---

## 📊 Production Checklist

### Security
- [ ] Change default JWT secret key
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Set up firewall rules
- [ ] Enable rate limiting

### Performance
- [ ] Enable gzip compression
- [ ] Set up CDN for static assets
- [ ] Configure database connection pooling
- [ ] Enable caching headers
- [ ] Monitor resource usage

### Monitoring
- [ ] Set up logging
- [ ] Configure error tracking
- [ ] Monitor uptime
- [ ] Set up backup strategy
- [ ] Configure analytics dashboard

---

## 🔍 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port 8000
netstat -ano | findstr :8000
# Kill the process
taskkill /PID [PID_NUMBER] /F
```

#### Database Connection Error
```bash
# Ensure database directory exists
mkdir -p backend/data
# Check permissions
chmod 755 backend/data
```

#### Frontend API Connection
- Check CORS settings in backend
- Verify API URLs in frontend config
- Check browser console for errors

### Production Deployment Issues

#### SSL Certificate Setup
```bash
# Using Let's Encrypt with Certbot
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

#### Database Migration
```bash
# Run migrations
cd backend
python -m alembic upgrade head
```

---

## 📱 Mobile/PWA Setup

### Progressive Web App Configuration
The app includes PWA features. To enable:

1. Serve over HTTPS
2. Ensure service worker is registered
3. Add app to mobile home screen

---

## 🚀 Quick Deploy Commands

### Development
```bash
# Backend
cd backend && uvicorn app.main:app --reload

# Frontend
cd frontend && python -m http.server 8080
```

### Production
```bash
# Docker
docker-compose up -d

# Or manual
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 📞 Support

If you encounter any deployment issues:
1. Check the logs: `docker-compose logs`
2. Review environment variables
3. Verify port availability
4. Check firewall settings
5. Refer to the troubleshooting section above

For additional support, please open an issue on the GitHub repository.