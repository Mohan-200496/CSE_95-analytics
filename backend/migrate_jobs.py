"""
Add resume_required column to jobs table
Migration script for PostgreSQL database
"""
import os
import asyncio
from sqlalchemy import text, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = 'postgresql://postgres.gdcrvcvpqzoxsttbecza:EL5kW8V2HLIp!0W@aws-0-us-west-1.pooler.supabase.com:6543/postgres'

async def migrate_jobs_table():
    """Add resume_required column to jobs table if it doesn't exist"""
    
    try:
        # Create async engine
        async_engine = create_async_engine(DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"))
        
        async with AsyncSession(async_engine) as session:
            # Check if column exists
            check_column_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'jobs' 
                AND column_name = 'resume_required'
            """)
            
            result = await session.execute(check_column_query)
            column_exists = result.scalar() is not None
            
            if not column_exists:
                logger.info("Adding resume_required column to jobs table...")
                
                # Add the column
                alter_query = text("""
                    ALTER TABLE jobs 
                    ADD COLUMN resume_required BOOLEAN DEFAULT true
                """)
                
                await session.execute(alter_query)
                await session.commit()
                logger.info("✅ Successfully added resume_required column")
            else:
                logger.info("✅ resume_required column already exists")
            
            # Check for application_method column as well
            check_app_method_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'jobs' 
                AND column_name = 'application_method'
            """)
            
            result = await session.execute(check_app_method_query)
            app_method_exists = result.scalar() is not None
            
            if not app_method_exists:
                logger.info("Adding application_method column to jobs table...")
                
                alter_query = text("""
                    ALTER TABLE jobs 
                    ADD COLUMN application_method VARCHAR(20) DEFAULT 'online'
                """)
                
                await session.execute(alter_query)
                await session.commit()
                logger.info("✅ Successfully added application_method column")
            else:
                logger.info("✅ application_method column already exists")
                
            # Show current table structure
            show_columns_query = text("""
                SELECT column_name, data_type, column_default, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'jobs'
                ORDER BY ordinal_position
            """)
            
            result = await session.execute(show_columns_query)
            columns = result.fetchall()
            
            logger.info("\nCurrent jobs table structure:")
            for col in columns:
                logger.info(f"  - {col[0]} ({col[1]}) Default: {col[2]} Nullable: {col[3]}")
                
        await async_engine.dispose()
        logger.info("\n🎉 Migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(migrate_jobs_table())