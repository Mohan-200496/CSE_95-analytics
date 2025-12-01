"""
Production enum fix script - Run on production to fix enum values
"""

import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fix_production_enums():
    """Fix enum values in production database"""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("❌ DATABASE_URL environment variable not set")
        return
        
    logger.info(f"🔗 Connecting to production database...")
    
    try:
        engine = create_async_engine(database_url)
        
        async with AsyncSession(engine) as session:
            # First, check current enum values in the database
            logger.info("📊 Checking current job data...")
            
            result = await session.execute(text("""
                SELECT job_id, job_type, status, employer_type 
                FROM jobs 
                LIMIT 5
            """))
            
            sample_jobs = result.fetchall()
            
            if sample_jobs:
                logger.info("Sample job data:")
                for job in sample_jobs:
                    job_id, job_type, status, employer_type = job
                    logger.info(f"  {job_id}: type={job_type}, status={status}, employer={employer_type}")
            
            # Check what enum values we have
            type_result = await session.execute(text("""
                SELECT DISTINCT job_type FROM jobs
            """))
            job_types = [row[0] for row in type_result.fetchall()]
            logger.info(f"Current job_type values: {job_types}")
            
            status_result = await session.execute(text("""
                SELECT DISTINCT status FROM jobs
            """))
            statuses = [row[0] for row in status_result.fetchall()]
            logger.info(f"Current status values: {statuses}")
            
            # Count jobs that might need fixing
            needs_fix_result = await session.execute(text("""
                SELECT COUNT(*) 
                FROM jobs 
                WHERE job_type IN ('full_time', 'part_time', 'contract', 'temporary', 'internship', 'freelance')
                   OR status IN ('draft', 'pending_approval', 'active', 'paused', 'closed', 'expired')
                   OR employer_type IN ('government', 'public_sector', 'private', 'ngo', 'startup')
            """))
            
            needs_fix_count = needs_fix_result.scalar()
            logger.info(f"Jobs with lowercase enum values that need fixing: {needs_fix_count}")
            
            if needs_fix_count > 0:
                logger.info("🔧 Converting lowercase enum values to uppercase...")
                
                # Fix job_type
                await session.execute(text("""
                    UPDATE jobs 
                    SET job_type = 'FULL_TIME' 
                    WHERE job_type = 'full_time'
                """))
                
                await session.execute(text("""
                    UPDATE jobs 
                    SET job_type = 'PART_TIME' 
                    WHERE job_type = 'part_time'
                """))
                
                await session.execute(text("""
                    UPDATE jobs 
                    SET job_type = 'CONTRACT' 
                    WHERE job_type = 'contract'
                """))
                
                await session.execute(text("""
                    UPDATE jobs 
                    SET job_type = 'TEMPORARY' 
                    WHERE job_type = 'temporary'
                """))
                
                await session.execute(text("""
                    UPDATE jobs 
                    SET job_type = 'INTERNSHIP' 
                    WHERE job_type = 'internship'
                """))
                
                await session.execute(text("""
                    UPDATE jobs 
                    SET job_type = 'FREELANCE' 
                    WHERE job_type = 'freelance'
                """))
                
                # Fix status
                await session.execute(text("""
                    UPDATE jobs 
                    SET status = 'DRAFT' 
                    WHERE status = 'draft'
                """))
                
                await session.execute(text("""
                    UPDATE jobs 
                    SET status = 'PENDING_APPROVAL' 
                    WHERE status = 'pending_approval'
                """))
                
                await session.execute(text("""
                    UPDATE jobs 
                    SET status = 'ACTIVE' 
                    WHERE status = 'active'
                """))
                
                await session.execute(text("""
                    UPDATE jobs 
                    SET status = 'PAUSED' 
                    WHERE status = 'paused'
                """))
                
                await session.execute(text("""
                    UPDATE jobs 
                    SET status = 'CLOSED' 
                    WHERE status = 'closed'
                """))
                
                await session.execute(text("""
                    UPDATE jobs 
                    SET status = 'EXPIRED' 
                    WHERE status = 'expired'
                """))
                
                # Fix employer_type
                await session.execute(text("""
                    UPDATE jobs 
                    SET employer_type = 'GOVERNMENT' 
                    WHERE employer_type = 'government'
                """))
                
                await session.execute(text("""
                    UPDATE jobs 
                    SET employer_type = 'PUBLIC_SECTOR' 
                    WHERE employer_type = 'public_sector'
                """))
                
                await session.execute(text("""
                    UPDATE jobs 
                    SET employer_type = 'PRIVATE' 
                    WHERE employer_type = 'private'
                """))
                
                await session.execute(text("""
                    UPDATE jobs 
                    SET employer_type = 'NGO' 
                    WHERE employer_type = 'ngo'
                """))
                
                await session.execute(text("""
                    UPDATE jobs 
                    SET employer_type = 'STARTUP' 
                    WHERE employer_type = 'startup'
                """))
                
                await session.commit()
                logger.info("✅ Enum values fixed successfully!")
            else:
                logger.info("ℹ️ No enum values need fixing")
            
            # Verify the fix
            logger.info("🔍 Verification - checking updated values...")
            result = await session.execute(text("""
                SELECT job_id, job_type, status, employer_type 
                FROM jobs 
                LIMIT 5
            """))
            
            sample_jobs = result.fetchall()
            
            if sample_jobs:
                logger.info("Updated job data:")
                for job in sample_jobs:
                    job_id, job_type, status, employer_type = job
                    logger.info(f"  {job_id}: type={job_type}, status={status}, employer={employer_type}")
                    
        await engine.dispose()
        logger.info("🎉 Production enum fix completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error fixing production enums: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(fix_production_enums())