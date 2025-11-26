# Punjab Rozgar Portal - Docker Setup Guide

## Prerequisites

### Install Docker Desktop for Windows
1. Download Docker Desktop: https://www.docker.com/products/docker-desktop
2. Install Docker Desktop
3. Start Docker Desktop
4. Verify installation: `docker --version`

## Quick Start

### Option 1: Using Batch Scripts (Recommended)
```cmd
# Start backend in Docker
start-backend-docker.bat

# Check container status and get IP
docker-info.bat

# Stop backend
stop-backend-docker.bat
```

### Option 2: Manual Commands
```cmd
# Build and start backend
docker-compose up --build punjab-rozgar-backend

# In another terminal - get container info
docker-compose ps
docker-compose logs punjab-rozgar-backend

# Stop container
docker-compose down
```

## Frontend Connection

### Update Frontend API URL
Once backend is running in Docker, update your frontend:

```javascript
// In frontend/js/config.js or similar file
// Replace localhost with your actual IP address
const API_BASE_URL = 'http://YOUR_IP_ADDRESS:8000/api/v1';

// Example:
const API_BASE_URL = 'http://192.168.1.100:8000/api/v1';
```

### Find Your IP Address
Run `docker-info.bat` or use `ipconfig` to find your local IP address.

## Backend URLs

- **API Base**: http://localhost:8000/api/v1
- **API Documentation**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health
- **Admin Panel**: http://localhost:8000/api/v1/admin

## Database

- **Type**: SQLite
- **Location**: `./backend/data/punjab_rozgar.db` (persistent volume)
- **Backup**: Automatically persisted outside container

## Troubleshooting

### Container won't start
```cmd
# Check logs
docker-compose logs punjab-rozgar-backend

# Rebuild container
docker-compose build --no-cache punjab-rozgar-backend
```

### Port conflicts
If port 8000 is already in use, edit `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Use port 8001 instead
```

### Frontend can't connect
1. Check if backend container is running: `docker-compose ps`
2. Use correct IP address (not localhost) in frontend
3. Ensure Windows Firewall allows Docker connections

## Development

### Live Code Reloading
The container is configured with volume mounting, so code changes are reflected automatically.

### Database Access
```cmd
# Access SQLite database
docker-compose exec punjab-rozgar-backend sqlite3 /app/data/punjab_rozgar.db
```

## Production Deployment

For production, update `docker-compose.yml`:
```yaml
environment:
  - ENVIRONMENT=production
  - DEBUG=false
command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```