"""
Emergency database migration script for production deployment
Run this to fix missing columns in production PostgreSQL
"""

import os
import asyncio
from sqlalchemy import create_engine, text
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def emergency_migrate():
    """Run emergency migration for production database"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        logger.info("No DATABASE_URL found - skipping migration")
        return
        
    if "sqlite" in database_url:
        logger.info("SQLite detected - skipping migration")
        return
    
    logger.info("🚨 Running emergency production migration...")
    
    # Convert postgres:// to postgresql:// if needed
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    # Create synchronous engine
    engine = create_engine(database_url)
    
    # Required columns
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
    
    try:
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                # Check existing columns
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'jobs'
                    ORDER BY ordinal_position
                """))
                
                existing_columns = {row[0] for row in result}
                logger.info(f"📋 Found existing columns: {existing_columns}")
                
                # Add missing columns
                added_count = 0
                for column, definition in required_columns.items():
                    if column not in existing_columns:
                        logger.info(f"➕ Adding missing column: {column}")
                        try:
                            conn.execute(text(f"ALTER TABLE jobs ADD COLUMN {column} {definition}"))
                            added_count += 1
                            logger.info(f"✅ Successfully added: {column}")
                        except Exception as e:
                            logger.warning(f"⚠️  Could not add {column}: {e}")
                
                # Commit transaction
                trans.commit()
                
                if added_count > 0:
                    logger.info(f"🎉 Successfully added {added_count} missing columns!")
                else:
                    logger.info("✅ All columns already exist - no migration needed")
                
                # Verify the problematic column
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'jobs' AND column_name = 'resume_required'
                """))
                
                if result.fetchone():
                    logger.info("✅ Confirmed: resume_required column now exists!")
                else:
                    logger.error("❌ resume_required column still missing!")
                    
            except Exception as e:
                trans.rollback()
                logger.error(f"❌ Migration transaction failed: {e}")
                raise
                
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise
    
    logger.info("🚀 Emergency migration completed!")

if __name__ == "__main__":
    emergency_migrate()