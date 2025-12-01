"""
Simple job creation test that should work
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.models.job import Job, JobType, JobStatus, EmployerType
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def simple_job_test():
    """Create a job directly using the ORM"""
    
    try:
        settings = get_settings()
        logger.info(f"Database URL: {settings.DATABASE_URL}")
        
        async with AsyncSessionLocal() as session:
            # Create a simple job
            new_job = Job(
                job_id=f"simple_test_{uuid.uuid4().hex[:8]}",
                title="Simple Test Job",
                description="A simple test job description",
                category="Technology",
                location_city="Chandigarh",
                employer_id="test_employer_001",
                employer_name="Test Company",
                job_type=JobType.FULL_TIME,
                status=JobStatus.DRAFT,
                employer_type=EmployerType.PRIVATE
            )
            
            logger.info(f"Creating job with job_type: {new_job.job_type}")
            logger.info(f"Enum value: {new_job.job_type.value}")
            
            session.add(new_job)
            await session.commit()
            await session.refresh(new_job)
            
            logger.info(f"✅ Successfully created job: {new_job.job_id}")
            logger.info(f"Job type in database: {new_job.job_type}")
            
            return new_job.job_id
            
    except Exception as e:
        logger.error(f"❌ Error creating job: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

if __name__ == "__main__":
    result = asyncio.run(simple_job_test())
    if result:
        print(f"✅ Job creation test passed: {result}")
    else:
        print("❌ Job creation test failed")