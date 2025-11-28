# Render Deployment Guide

## Overview
This guide helps you deploy the Punjab Rozgar Portal to Render with PostgreSQL database for persistent storage.

## Prerequisites
- Render account (free tier available)
- Git repository with your code
- Frontend and Backend already deployed on Render

## Database Setup

### 1. Create PostgreSQL Database on Render

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Login to your account

2. **Create New PostgreSQL Database**
   - Click "New" → "PostgreSQL"
   - Configure database:
     ```
     Name: punjab-rozgar-db
     Database: punjab_rozgar
     User: (auto-generated)
     Plan: Free (or your preferred plan)
     Region: Same as your backend service
     ```

3. **Get Database Connection Details**
   After creation, copy these values from the database dashboard:
   ```
   Internal Database URL: postgresql://user:password@host:5432/database
   External Database URL: postgresql://user:password@host:5432/database
   ```

### 2. Configure Backend Environment Variables

In your Backend service on Render:

1. **Go to Backend Service Settings**
   - Navigate to your backend service
   - Go to "Environment" tab

2. **Add Environment Variables**
   ```
   DATABASE_URL = postgresql://user:password@host:5432/database
   SECRET_KEY = your-super-secret-key-here
   ALGORITHM = HS256
   ACCESS_TOKEN_EXPIRE_MINUTES = 30
   RENDER = true
   DEBUG = false
   ENVIRONMENT = production
   ```

3. **Important Settings**
   - Use the **Internal Database URL** for better performance
   - Set `RENDER=true` to enable Render-specific configuration
   - Keep `DEBUG=false` for production

### 3. Install Required Dependencies

Ensure your `backend/requirements.txt` includes PostgreSQL dependencies:

```txt
fastapi[all]
uvicorn[standard]
sqlalchemy[asyncio]
alembic
psycopg2-binary
asyncpg
python-multipart
python-jose[cryptography]
passlib[bcrypt]
email-validator
aiosqlite
pydantic[email]
```

### 4. Database Migration

The backend will automatically:
1. Detect the PostgreSQL connection
2. Create all tables on first startup
3. Initialize with default data

**Manual Migration (if needed):**
```bash
# Connect to your Render backend shell
alembic upgrade head
```

### 5. Frontend Configuration

Update your frontend environment if needed:
```javascript
// config/environment.js
const BACKEND_BASE_URL = 'https://your-backend-service.onrender.com';
```

## Deployment Steps

### 1. Update Repository
Push all changes to your Git repository:
```bash
git add .
git commit -m "Add PostgreSQL support for Render"
git push origin main
```

### 2. Deploy Services

1. **Backend Deployment**
   - Render will auto-deploy from Git
   - Monitor logs for successful database connection
   - Check for any dependency installation issues

2. **Frontend Deployment**
   - Update if you changed API URLs
   - Ensure CORS is properly configured

### 3. Verification

1. **Test Database Connection**
   - Check backend service logs
   - Look for successful database connection messages

2. **Test Application Flow**
   - Create test user account
   - Post a test job
   - Verify data persists after service restart

## Database Features with PostgreSQL

### Advantages over SQLite:
- **Persistent Storage**: Data survives service restarts
- **Concurrent Access**: Multiple users simultaneously
- **Advanced Features**: Full-text search, JSON columns
- **Scalability**: Better performance under load
- **Backup & Recovery**: Automated Render backups

### Analytics Capabilities:
- Real-time user tracking
- Job posting analytics
- Search pattern analysis
- Performance metrics
- Usage statistics

## Monitoring & Maintenance

### Health Checks
Your backend includes health check endpoints:
- `GET /health` - Basic service health
- `GET /health/database` - Database connection status

### Logs
Monitor application logs in Render dashboard:
- Database connection status
- API request/response logs
- Error tracking
- Performance metrics

### Database Management
- **Render Dashboard**: View connection stats
- **pgAdmin**: Connect externally for database management
- **Backup**: Render provides automatic backups

## Troubleshooting

### Common Issues:

1. **Connection Refused**
   - Check DATABASE_URL format
   - Verify database is running
   - Confirm network connectivity

2. **Migration Errors**
   - Check table creation permissions
   - Verify database schema
   - Review migration logs

3. **CORS Issues**
   - Update CORS_ORIGINS in config
   - Include your frontend domain
   - Check protocol (http vs https)

### Debug Commands:
```python
# Test database connection
python -c "from app.core.database import engine; print('Connected!' if engine else 'Failed')"

# Check tables
python -c "from app.core.database import engine; print(engine.table_names())"
```

## Security Best Practices

1. **Environment Variables**
   - Never commit secrets to Git
   - Use Render environment variables
   - Rotate keys regularly

2. **Database Security**
   - Use Internal URLs when possible
   - Monitor access logs
   - Regular security updates

3. **CORS Configuration**
   - Only allow trusted origins
   - Use HTTPS in production
   - Validate API endpoints

## Next Steps

1. ✅ Set up PostgreSQL database on Render
2. ✅ Configure environment variables
3. ✅ Deploy backend with database connection
4. ✅ Test user registration and job posting
5. ✅ Verify data persistence
6. ✅ Monitor application performance

Your Punjab Rozgar Portal will now have persistent storage with all the benefits of a cloud database!