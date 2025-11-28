"""
Database Setup and Verification Script
Use this script to test database connection and setup tables
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.config import get_settings
from app.core.database import async_engine, Base, get_database
from app.models import user, company, job, application, skill, analytics, admin
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_database_connection():
    """Test database connection"""
    try:
        async with async_engine.begin() as conn:
            # Test basic connection
            result = await conn.execute("SELECT 1")
            logger.info("✅ Database connection successful!")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

async def create_tables():
    """Create all tables"""
    try:
        async with async_engine.begin() as conn:
            # Drop all tables (for clean setup)
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("🗑️ Dropped existing tables")
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Created all tables successfully!")
            return True
    except Exception as e:
        logger.error(f"❌ Table creation failed: {e}")
        return False

async def create_admin_user():
    """Create default admin user"""
    try:
        from app.services.auth_service import AuthService
        from app.schemas.user import UserCreate
        
        async with async_engine.begin() as conn:
            # Create admin user
            auth_service = AuthService()
            admin_data = UserCreate(
                email="admin@test.com",
                password="admin123",
                first_name="Admin",
                last_name="User",
                phone="+1234567890",
                user_type="admin"
            )
            
            # This would need to be implemented with proper session
            logger.info("✅ Admin user creation prepared")
            return True
            
    except Exception as e:
        logger.error(f"❌ Admin user creation failed: {e}")
        return False

async def verify_tables():
    """Verify that all required tables exist"""
    try:
        async with async_engine.begin() as conn:
            # Check if tables exist by querying information schema
            if "postgresql" in str(async_engine.url):
                # PostgreSQL query
                result = await conn.execute(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
                )
            else:
                # SQLite query
                result = await conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            
            tables = [row[0] for row in result.fetchall()]
            
            expected_tables = [
                'users', 'companies', 'jobs', 'applications', 
                'skills', 'job_skills', 'user_skills',
                'analytics_events', 'user_analytics', 'job_analytics',
                'admins'
            ]
            
            missing_tables = [t for t in expected_tables if t not in tables]
            
            if missing_tables:
                logger.warning(f"⚠️ Missing tables: {missing_tables}")
            else:
                logger.info("✅ All required tables exist")
                
            logger.info(f"📊 Found tables: {tables}")
            return len(missing_tables) == 0
            
    except Exception as e:
        logger.error(f"❌ Table verification failed: {e}")
        return False

async def main():
    """Main setup and verification function"""
    settings = get_settings()
    
    logger.info("🚀 Starting database setup and verification...")
    logger.info(f"📍 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🗄️ Database URL: {settings.DATABASE_URL[:50]}...")
    
    # Step 1: Test connection
    logger.info("\n1. Testing database connection...")
    if not await check_database_connection():
        logger.error("Cannot proceed without database connection")
        return False
    
    # Step 2: Create tables
    logger.info("\n2. Creating database tables...")
    if not await create_tables():
        logger.error("Cannot proceed without tables")
        return False
    
    # Step 3: Verify tables
    logger.info("\n3. Verifying table creation...")
    if not await verify_tables():
        logger.warning("Some tables may be missing")
    
    # Step 4: Admin user setup
    logger.info("\n4. Setting up admin user...")
    await create_admin_user()
    
    logger.info("\n🎉 Database setup completed!")
    logger.info("\nNext steps:")
    logger.info("1. Start your backend server: uvicorn app.main:app --reload")
    logger.info("2. Test the API endpoints")
    logger.info("3. Create test users via the frontend")
    
    return True

if __name__ == "__main__":
    asyncio.run(main())