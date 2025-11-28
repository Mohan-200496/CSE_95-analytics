"""
Render Deployment Health Check
Quick script to verify your Render deployment is working
"""

import os
import sys
import asyncio
import logging

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_environment():
    """Check environment variables and configuration"""
    logger.info("🔍 Checking environment configuration...")
    
    # Required environment variables
    required_vars = [
        'DATABASE_URL',
        'SECRET_KEY',
        'ALGORITHM'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
        else:
            # Show partial value for security
            value = os.getenv(var)
            if var == 'SECRET_KEY':
                logger.info(f"✅ {var}: {value[:10]}...***")
            elif var == 'DATABASE_URL':
                logger.info(f"✅ {var}: {value[:20]}...***")
            else:
                logger.info(f"✅ {var}: {value}")
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    # Check if running on Render
    is_render = os.getenv('RENDER') == 'true'
    logger.info(f"🌐 Running on Render: {is_render}")
    
    return True

async def test_database():
    """Test database connection"""
    try:
        from app.core.database import async_engine
        
        logger.info("🗄️ Testing database connection...")
        
        async with async_engine.begin() as conn:
            if "postgresql" in str(async_engine.url):
                result = await conn.execute("SELECT version()")
                version = result.fetchone()[0]
                logger.info(f"✅ PostgreSQL connected: {version[:50]}...")
            else:
                result = await conn.execute("SELECT sqlite_version()")
                version = result.fetchone()[0]
                logger.info(f"✅ SQLite connected: {version}")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

async def test_api_endpoints():
    """Test basic API functionality"""
    try:
        import httpx
        
        # Get base URL
        base_url = os.getenv('RENDER_EXTERNAL_URL', 'http://localhost:8000')
        logger.info(f"🌐 Testing API at: {base_url}")
        
        async with httpx.AsyncClient() as client:
            # Test health endpoint
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                logger.info("✅ Health endpoint working")
            else:
                logger.warning(f"⚠️ Health endpoint returned: {response.status_code}")
            
            # Test docs endpoint
            response = await client.get(f"{base_url}/docs")
            if response.status_code == 200:
                logger.info("✅ API docs accessible")
            else:
                logger.warning(f"⚠️ API docs returned: {response.status_code}")
                
        return True
        
    except Exception as e:
        logger.error(f"❌ API test failed: {e}")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    logger.info("📦 Checking required dependencies...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'psycopg2',  # for PostgreSQL
        'asyncpg',   # for async PostgreSQL
        'pydantic'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'psycopg2':
                import psycopg2
            elif package == 'asyncpg':
                import asyncpg
            else:
                __import__(package)
            logger.info(f"✅ {package} installed")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"❌ {package} missing")
    
    return len(missing_packages) == 0

async def main():
    """Run all health checks"""
    logger.info("🚀 Punjab Rozgar Portal - Render Deployment Health Check")
    logger.info("=" * 60)
    
    all_good = True
    
    # Check 1: Environment
    logger.info("\n1️⃣ Environment Configuration")
    if not check_environment():
        all_good = False
    
    # Check 2: Dependencies
    logger.info("\n2️⃣ Dependencies")
    if not check_dependencies():
        all_good = False
    
    # Check 3: Database
    logger.info("\n3️⃣ Database Connection")
    if not await test_database():
        all_good = False
    
    # Check 4: API (only if not in setup mode)
    if os.getenv('SKIP_API_TEST') != 'true':
        logger.info("\n4️⃣ API Endpoints")
        try:
            if not await test_api_endpoints():
                all_good = False
        except Exception:
            logger.warning("⚠️ API test skipped (server may not be running)")
    
    # Summary
    logger.info("\n" + "=" * 60)
    if all_good:
        logger.info("🎉 All health checks passed! Your Render deployment looks good.")
        logger.info("\n📋 Next steps:")
        logger.info("1. Test user registration at your frontend URL")
        logger.info("2. Create and post a job listing")
        logger.info("3. Verify data persists across deployments")
        logger.info("4. Monitor logs for any issues")
    else:
        logger.error("❌ Some health checks failed. Please review the errors above.")
        logger.info("\n🔧 Troubleshooting tips:")
        logger.info("1. Check environment variables in Render dashboard")
        logger.info("2. Verify PostgreSQL database is running")
        logger.info("3. Review deployment logs")
        logger.info("4. Ensure all dependencies are in requirements.txt")
    
    return all_good

if __name__ == "__main__":
    asyncio.run(main())