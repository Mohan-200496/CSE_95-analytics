"""
Production Database Migration Script
Ensures cloud PostgreSQL database has all required columns
"""

import asyncio
import os
import asyncpg
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database URL from environment (Render sets this automatically)
database_url = os.getenv("DATABASE_URL")
if not database_url:
    logger.error("DATABASE_URL environment variable not set!")
    exit(1)

# Convert postgres:// to postgresql:// for asyncpg
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# Add asyncpg support
if "?" not in database_url:
    database_url += "?prepared_statement_cache_size=0"
else:
    database_url += "&prepared_statement_cache_size=0"

async def migrate_database():
    """Migrate production database to match local schema"""
    logger.info("🚀 Starting production database migration...")
    
    # Create async engine
    engine = create_async_engine(database_url, echo=True)
    
    try:
        async with engine.begin() as conn:
            logger.info("📊 Connected to production database")
            
            # Get current table schema
            result = await conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'jobs'
                ORDER BY ordinal_position
            """))
            
            existing_columns = {row[0]: row[1] for row in result}
            logger.info(f"📋 Existing columns: {list(existing_columns.keys())}")
            
            # Required columns that might be missing
            required_columns = {
                'resume_required': 'BOOLEAN DEFAULT true',
                'application_url': 'TEXT',
                'contact_email': 'VARCHAR(200)',
                'contact_phone': 'VARCHAR(20)',
                'status': 'VARCHAR(50) DEFAULT \'active\'',
                'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'published_at': 'TIMESTAMP',
                'expires_at': 'TIMESTAMP',
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
            for column, definition in required_columns.items():
                if column not in existing_columns:
                    logger.info(f"➕ Adding column: {column}")
                    await conn.execute(text(f"""
                        ALTER TABLE jobs ADD COLUMN {column} {definition}
                    """))
                    logger.info(f"✅ Added {column}")
                else:
                    logger.info(f"✅ Column {column} already exists")
            
            # Create indexes for better performance
            indexes_to_create = [
                "CREATE INDEX IF NOT EXISTS idx_jobs_resume_required ON jobs(resume_required)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_featured ON jobs(featured)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_urgent ON jobs(urgent)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_government_scheme ON jobs(government_scheme)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_views_count ON jobs(views_count)",
                "CREATE INDEX IF NOT EXISTS idx_jobs_expires_at ON jobs(expires_at)",
            ]
            
            logger.info("🔍 Creating performance indexes...")
            for index_sql in indexes_to_create:
                try:
                    await conn.execute(text(index_sql))
                    logger.info(f"✅ Created index: {index_sql.split('idx_')[1].split(' ON')[0]}")
                except Exception as e:
                    logger.info(f"ℹ️  Index might already exist: {e}")
            
            # Verify migration
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'jobs'
                ORDER BY ordinal_position
            """))
            
            final_columns = [row[0] for row in result]
            logger.info(f"📊 Final column count: {len(final_columns)}")
            logger.info(f"📋 All columns: {final_columns}")
            
            # Test query to ensure it works
            await conn.execute(text("""
                SELECT COUNT(*) as job_count FROM jobs
            """))
            
            logger.info("🎉 Migration completed successfully!")
            logger.info("✅ Production database is now synchronized with local schema")
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate_database())