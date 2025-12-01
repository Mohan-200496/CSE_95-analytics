"""
Test job creation with proper enum handling
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings
from app.models.job import Job, JobType, JobStatus, EmployerType
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_create_job():
    """Test creating a job with proper enum handling"""
    settings = get_settings()
    
    try:
        if 'sqlite' in settings.DATABASE_URL:
            db_url = settings.DATABASE_URL.replace('sqlite:///', 'sqlite+aiosqlite:///')
        else:
            db_url = settings.DATABASE_URL
            
        engine = create_async_engine(db_url, echo=True)  # Enable SQL logging
        
        async with AsyncSession(engine) as session:
            logger.info("🧪 Testing job creation with enum values...")
            
            # Create a test job with proper enum values
            test_job = Job(
                job_id="test_job_" + str(int(asyncio.get_event_loop().time())),
                title="Test Software Developer",
                description="Test job description",
                location_city="Chandigarh",
                category="Technology",
                employer_id="test_employer_123",
                employer_name="Test Company",
                job_type=JobType.FULL_TIME,  # Use enum directly
                status=JobStatus.ACTIVE,     # Use enum directly
                employer_type=EmployerType.PRIVATE,  # Use enum directly
                salary_min=50000,
                salary_max=80000
            )
            
            logger.info(f"Creating job with:")
            logger.info(f"  job_type: {test_job.job_type} (value: {test_job.job_type.value})")
            logger.info(f"  status: {test_job.status} (value: {test_job.status.value})")
            logger.info(f"  employer_type: {test_job.employer_type} (value: {test_job.employer_type.value})")
            
            session.add(test_job)
            await session.commit()
            await session.refresh(test_job)
            
            logger.info(f"✅ Job created successfully: {test_job.job_id}")
            
            # Query it back to verify
            from sqlalchemy import select
            result = await session.execute(select(Job).where(Job.job_id == test_job.job_id))
            retrieved_job = result.scalar_one_or_none()
            
            if retrieved_job:
                logger.info(f"✅ Job retrieved successfully:")
                logger.info(f"  job_type: {retrieved_job.job_type}")
                logger.info(f"  status: {retrieved_job.status}")
                logger.info(f"  employer_type: {retrieved_job.employer_type}")
            else:
                logger.error("❌ Could not retrieve created job")
                
        await engine.dispose()
        
    except Exception as e:
        logger.error(f"❌ Error creating test job: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_create_job())