"""
Punjab Rozgar Portal - FastAPI Backend
Main application entry point with analytics integration
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
import uvicorn
import logging
import os
from datetime import datetime
from contextlib import asynccontextmanager

# Core imports
from app.core.config import get_settings
from app.core.database import get_database, create_tables, async_engine
from app.core.logging import setup_logging
from sqlalchemy import text

# API route imports
from app.api.v1.auth import router as auth_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.users import router as users_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.admin import router as admin_router
from app.api.v1.applications import router as applications_router
from app.api.v1.recommendations import router as recommendations_router

# Analytics and middleware
from app.analytics.tracker import AnalyticsTracker
from app.middleware.analytics import AnalyticsMiddleware
from app.middleware.security import SecurityMiddleware

# Load settings
settings = get_settings()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

async def migrate_production_database():
    """Migrate production database to ensure all columns exist"""
    if not os.getenv("RENDER"):  # Only run on production/Render
        return
    
    logger.info("🔄 Running production database migration...")
    
    try:
        async with async_engine.begin() as conn:
            # Check if jobs table exists and get columns
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'jobs'
                ORDER BY ordinal_position
            """))
            existing_columns = {row[0] for row in result}
            logger.info(f"📋 Found existing columns: {existing_columns}")
            
            # Required columns that might be missing
            required_columns = {
                'resume_required': 'BOOLEAN DEFAULT true',
                'application_url': 'TEXT',
                'contact_email': 'VARCHAR(200)',
                'contact_phone': 'VARCHAR(20)',
                'views_count': 'INTEGER DEFAULT 0',
                'applications_count': 'INTEGER DEFAULT 0',
                'saves_count': 'INTEGER DEFAULT 0',
                'shares_count': 'INTEGER DEFAULT 0',
                'slug': 'VARCHAR(500)',
                'meta_description': 'TEXT',
                'featured': 'BOOLEAN DEFAULT false',
                'urgent': 'BOOLEAN DEFAULT false',
                'government_scheme': 'BOOLEAN DEFAULT false',
                'reservation_category': 'VARCHAR(100)',
                'age_limit_min': 'INTEGER',
                'age_limit_max': 'INTEGER',
                'benefits': 'TEXT',
                'working_hours': 'VARCHAR(100)',
                'interview_process': 'TEXT',
                'additional_info': 'TEXT'
            }
            
            # Add missing columns
            missing_columns = []
            for column, definition in required_columns.items():
                if column not in existing_columns:
                    missing_columns.append(column)
                    logger.info(f"➕ Adding missing column: {column}")
                    try:
                        await conn.execute(text(f"ALTER TABLE jobs ADD COLUMN {column} {definition}"))
                        logger.info(f"✅ Successfully added {column}")
                    except Exception as e:
                        logger.error(f"❌ Failed to add {column}: {e}")
            
            if missing_columns:
                logger.info(f"🔧 Added {len(missing_columns)} missing columns: {missing_columns}")
            else:
                logger.info("✅ All required columns already exist")
            
            logger.info("✅ Production database migration completed")
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        # Don't fail the startup, just log the error
        raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Punjab Rozgar Portal Backend...")
    
    # Detect deployment environment
    if os.getenv("RENDER"):
        logger.info("🌐 Running on Render.com")
    elif os.getenv("DYNO"):
        logger.info("🌐 Running on Heroku")
    elif os.getenv("RAILWAY_ENVIRONMENT"):
        logger.info("🌐 Running on Railway")
    else:
        logger.info("💻 Running locally")
    
    # Initialize database
    await create_tables()
    logger.info("Database tables created/verified")
    
    # Run production database migration if needed
    await migrate_production_database()
    
    # Initialize analytics tracker
    analytics_tracker = AnalyticsTracker()
    app.state.analytics = analytics_tracker
    logger.info("Analytics system initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Punjab Rozgar Portal Backend...")

# Create FastAPI application
app = FastAPI(
    title="Punjab Rozgar Portal API",
    description="Employment portal backend with comprehensive analytics for Punjab government",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Security middleware (add these first) - TEMPORARILY DISABLED FOR MOBILE DEBUGGING
# app.add_middleware(
#     TrustedHostMiddleware,
#     allowed_hosts=settings.ALLOWED_HOSTS
# )
# app.add_middleware(SecurityMiddleware)
# app.add_middleware(AnalyticsMiddleware)

# Configure CORS with maximum compatibility for deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for deployment
    allow_credentials=False,  # Must be False when allow_origins is "*"
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Additional CORS handling for Render deployment
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    """Add CORS headers to all responses for Render deployment"""
    
    # Handle preflight requests immediately
    if request.method == "OPTIONS":
        response = JSONResponse(content={"status": "ok"})
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Max-Age"] = "86400"
        return response
    
    # Process the request
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Request processing error: {str(e)}")
        response = JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {str(e)}"}
        )
    
    # Add CORS headers to all responses
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Expose-Headers"] = "*"
    
    return response

# Add debugging middleware for requests
@app.middleware("http")
async def debug_requests(request: Request, call_next):
    """Log all requests for debugging"""
    start_time = datetime.utcnow()
    logger.info(f"Request: {request.method} {request.url}")
    logger.info(f"Origin: {request.headers.get('origin', 'No origin header')}")
    
    response = await call_next(request)
    
    process_time = (datetime.utcnow() - start_time).total_seconds()
    logger.info(f"Response: {response.status_code} in {process_time:.3f}s")
    
    return response

# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """System health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "service": "Punjab Rozgar Portal API"
    }

# CORS test endpoint
@app.get("/cors-test", tags=["System"])
async def cors_test():
    """Test CORS configuration"""
    return {
        "status": "success",
        "message": "CORS is working correctly",
        "timestamp": datetime.utcnow().isoformat(),
        "cors_headers": "should be present in response"
    }

@app.post("/cors-test", tags=["System"])
async def cors_test_post(data: dict = None):
    """Test CORS with POST request"""
    return {
        "status": "success",
        "message": "POST CORS is working correctly",
        "received_data": data,
        "timestamp": datetime.utcnow().isoformat()
    }

# Database initialization endpoint
# Demo accounts endpoint (temporarily disabled for debugging)
# @app.post("/init-demo-accounts", tags=["System"])
# async def init_demo_accounts(db: AsyncSession = Depends(get_database)):
    """Initialize demo accounts in database"""
    try:
        from app.models.user import User, UserRole, AccountStatus
        from passlib.context import CryptContext
        from sqlalchemy import select
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Check if admin already exists
        result = await db.execute(select(User).where(User.email == "admin@test.com"))
        if result.scalar_one_or_none():
            return {"message": "Demo accounts already exist", "status": "already_initialized"}
        
        # Import UserRole enum
        from app.models.user import UserRole, AccountStatus
        
        # Create Admin User  
        admin_user = User(
            user_id="admin_demo_001",
            email="admin@test.com",
            hashed_password=pwd_context.hash("admin123"),
            first_name="Admin",
            last_name="User",
            phone="+1234567890",
            role=UserRole.ADMIN,
            status=AccountStatus.ACTIVE,
            email_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(admin_user)
        await db.flush()
        
        # Create Employer User
        employer_user = User(
            user_id="employer_demo_001",
            email="employer@test.com", 
            hashed_password=pwd_context.hash("employer123"),
            first_name="Test",
            last_name="Employer",
            phone="+1234567891",
            role=UserRole.EMPLOYER,
            status=AccountStatus.ACTIVE,
            email_verified=True,
            company_name="Demo Tech Solutions",  # Store company name in user record for now
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(employer_user)
        await db.flush()
        
        # TODO: Create Company record separately once Company model is stable
        
        # Create Job Seeker User
        jobseeker_user = User(
            user_id="jobseeker_demo_001",
            email="jobseeker@email.com",
            hashed_password=pwd_context.hash("jobseeker123"),
            first_name="Test", 
            last_name="JobSeeker",
            phone="+1234567892",
            role=UserRole.JOB_SEEKER,
            status=AccountStatus.ACTIVE,
            email_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(jobseeker_user)
        
        await db.commit()
        
        return {
            "message": "Demo accounts created successfully",
            "status": "initialized",
            "accounts": [
                {"email": "admin@test.com", "password": "admin123", "type": "admin"},
                {"email": "employer@test.com", "password": "employer123", "type": "employer"}, 
                {"email": "jobseeker@email.com", "password": "jobseeker123", "type": "jobseeker"}
            ]
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error initializing demo accounts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize demo accounts: {str(e)}")

# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Punjab Rozgar Portal API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/health",
        "analytics": "/api/v1/analytics"
    }

# Analytics event tracking endpoint (high priority)
@app.post("/api/track", tags=["Analytics"])
async def track_event(request: Request):
    """Quick event tracking endpoint for frontend"""
    try:
        data = await request.json()
        tracker = request.app.state.analytics
        
        # Track the event
        event_id = await tracker.track_event(
            event_name=data.get("event"),
            properties=data.get("data", {}),
            user_id=data.get("user_id"),
            session_id=data.get("session_id"),
            request=request
        )
        
        return {"success": True, "event_id": event_id}
    
    except Exception as e:
        logger.error(f"Event tracking error: {e}")
        return {"success": False, "error": "Failed to track event"}

# Include API routers
app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

app.include_router(
    users_router,
    prefix="/api/v1/users",
    tags=["Users"]
)

app.include_router(
    jobs_router,
    prefix="/api/v1/jobs", 
    tags=["Jobs"]
)

app.include_router(
    analytics_router,
    prefix="/api/v1/analytics",
    tags=["Analytics"]
)

app.include_router(
    admin_router,
    prefix="/api/v1/admin",
    tags=["Administration"]
)

app.include_router(
    applications_router,
    prefix="/api/v1/applications",
    tags=["Applications"]
)

app.include_router(
    recommendations_router,
    prefix="/api/v1/recommendations",
    tags=["Recommendations"]
)

# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Global HTTP exception handler with analytics tracking"""
    
    # Track error events
    if hasattr(request.app.state, 'analytics'):
        await request.app.state.analytics.track_event(
            event_name="api_error",
            properties={
                "status_code": exc.status_code,
                "detail": exc.detail,
                "path": str(request.url.path),
                "method": request.method
            },
            request=request
        )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Track critical errors
    if hasattr(request.app.state, 'analytics'):
        await request.app.state.analytics.track_event(
            event_name="system_error",
            properties={
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "path": str(request.url.path),
                "method": request.method
            },
            request=request
        )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Development server
if __name__ == "__main__":
    # Use PORT environment variable for Render deployment
    port = int(os.environ.get("PORT", settings.PORT))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Bind to all interfaces for deployment
        port=port,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )
