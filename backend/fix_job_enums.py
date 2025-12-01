"""
Fix existing job data enum values
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text, select, update
from app.core.config import get_settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fix_job_enums():
    """Fix enum values in existing job data"""
    settings = get_settings()
    
    try:
        if 'sqlite' in settings.DATABASE_URL:
            db_url = settings.DATABASE_URL.replace('sqlite:///', 'sqlite+aiosqlite:///')
        else:
            db_url = settings.DATABASE_URL
            
        engine = create_async_engine(db_url)
        
        async with AsyncSession(engine) as session:
            logger.info("🔧 Fixing job enum values...")
            
            # Fix job_type values
            job_type_fixes = {
                'FULL_TIME': 'full_time',
                'PART_TIME': 'part_time', 
                'CONTRACT': 'contract',
                'TEMPORARY': 'temporary',
                'INTERNSHIP': 'internship',
                'FREELANCE': 'freelance'
            }
            
            # Fix job_status values  
            status_fixes = {
                'DRAFT': 'draft',
                'PENDING_APPROVAL': 'pending_approval',
                'ACTIVE': 'active',
                'PAUSED': 'paused',
                'CLOSED': 'closed',
                'EXPIRED': 'expired'
            }
            
            # Fix employer_type values
            employer_fixes = {
                'GOVERNMENT': 'government',
                'PUBLIC_SECTOR': 'public_sector', 
                'PRIVATE': 'private',
                'NGO': 'ngo',
                'STARTUP': 'startup'
            }
            
            # Get all jobs first to see current state
            result = await session.execute(text("SELECT job_id, job_type, status, employer_type FROM jobs"))
            jobs = result.fetchall()
            
            logger.info(f"Found {len(jobs)} jobs to potentially fix")
            
            fixed_count = 0
            for job in jobs:
                job_id, job_type, status, employer_type = job
                
                # Fix job_type if needed
                if job_type in job_type_fixes.values():
                    # Already correct lowercase value
                    pass
                elif job_type in job_type_fixes.keys():
                    # Need to convert from uppercase to lowercase
                    new_type = job_type_fixes[job_type]
                    await session.execute(
                        text("UPDATE jobs SET job_type = :new_type WHERE job_id = :job_id"),
                        {"new_type": new_type, "job_id": job_id}
                    )
                    logger.info(f"Fixed job_type for {job_id}: {job_type} -> {new_type}")
                    fixed_count += 1
                    
                # Fix status if needed
                if status in status_fixes.values():
                    # Already correct lowercase value
                    pass
                elif status in status_fixes.keys():
                    # Need to convert from uppercase to lowercase
                    new_status = status_fixes[status] 
                    await session.execute(
                        text("UPDATE jobs SET status = :new_status WHERE job_id = :job_id"),
                        {"new_status": new_status, "job_id": job_id}
                    )
                    logger.info(f"Fixed status for {job_id}: {status} -> {new_status}")
                    fixed_count += 1
                    
                # Fix employer_type if needed
                if employer_type in employer_fixes.values():
                    # Already correct lowercase value
                    pass
                elif employer_type in employer_fixes.keys():
                    # Need to convert from uppercase to lowercase
                    new_employer = employer_fixes[employer_type]
                    await session.execute(
                        text("UPDATE jobs SET employer_type = :new_employer WHERE job_id = :job_id"),
                        {"new_employer": new_employer, "job_id": job_id}
                    )
                    logger.info(f"Fixed employer_type for {job_id}: {employer_type} -> {new_employer}")
                    fixed_count += 1
            
            await session.commit()
            logger.info(f"✅ Fixed {fixed_count} enum values in job data")
            
            # Verify the fixes
            result = await session.execute(text("SELECT job_id, job_type, status, employer_type FROM jobs"))
            jobs = result.fetchall()
            
            logger.info("📊 Current job data after fixes:")
            for job in jobs:
                job_id, job_type, status, employer_type = job
                logger.info(f"  {job_id}: type={job_type}, status={status}, employer={employer_type}")
                
        await engine.dispose()
        logger.info("🎉 Job enum fix completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error fixing job enums: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(fix_job_enums())