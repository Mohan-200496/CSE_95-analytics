"""
Database migration script to ensure all job columns exist
Run this to update the database schema for existing deployments
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.sql import text
from app.core.config import get_settings
from app.models.job import Job
from app.core.database import Base

settings = get_settings()

async def check_and_add_missing_columns():
    """Check and add any missing columns to the jobs table"""
    
    # Create async engine
    if settings.DATABASE_URL.startswith("sqlite"):
        # For SQLite, use aiosqlite
        database_url = settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
    else:
        # For PostgreSQL, use asyncpg
        database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    
    engine = create_async_engine(database_url)
    
    try:
        async with engine.begin() as conn:
            # Check if resume_required column exists
            if settings.DATABASE_URL.startswith("sqlite"):
                # SQLite query to check column existence
                result = await conn.execute(text("PRAGMA table_info(jobs)"))
                columns = result.fetchall()
                column_names = [row[1] for row in columns]
                
                if 'resume_required' not in column_names:
                    print("Adding missing resume_required column...")
                    await conn.execute(text("ALTER TABLE jobs ADD COLUMN resume_required BOOLEAN DEFAULT 1"))
                    print("✅ Added resume_required column")
                else:
                    print("✅ resume_required column already exists")
                    
            else:
                # PostgreSQL query to check column existence
                result = await conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='jobs' AND column_name='resume_required'
                """))
                exists = result.fetchone()
                
                if not exists:
                    print("Adding missing resume_required column...")
                    await conn.execute(text("ALTER TABLE jobs ADD COLUMN resume_required BOOLEAN DEFAULT true"))
                    print("✅ Added resume_required column")
                else:
                    print("✅ resume_required column already exists")
            
            # Check for other potentially missing columns
            missing_columns = []
            expected_columns = [
                'resume_required', 'meta_description', 'featured', 'urgent',
                'government_scheme', 'reservation_category', 'age_limit_min',
                'age_limit_max', 'benefits', 'working_hours', 'interview_process',
                'additional_info'
            ]
            
            if settings.DATABASE_URL.startswith("sqlite"):
                for col in expected_columns:
                    if col not in column_names:
                        missing_columns.append(col)
            else:
                for col in expected_columns:
                    result = await conn.execute(text(f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name='jobs' AND column_name='{col}'
                    """))
                    exists = result.fetchone()
                    if not exists:
                        missing_columns.append(col)
            
            # Add missing columns with appropriate defaults
            column_definitions = {
                'meta_description': 'TEXT',
                'featured': 'BOOLEAN DEFAULT false',
                'urgent': 'BOOLEAN DEFAULT false', 
                'government_scheme': 'TEXT',
                'reservation_category': 'TEXT',
                'age_limit_min': 'INTEGER',
                'age_limit_max': 'INTEGER',
                'benefits': 'TEXT',
                'working_hours': 'TEXT',
                'interview_process': 'TEXT',
                'additional_info': 'TEXT'
            }
            
            for col in missing_columns:
                if col in column_definitions:
                    print(f"Adding missing {col} column...")
                    await conn.execute(text(f"ALTER TABLE jobs ADD COLUMN {col} {column_definitions[col]}"))
                    print(f"✅ Added {col} column")
            
            if not missing_columns:
                print("✅ All expected columns exist")
                
        print("🎉 Database schema check completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        raise
    finally:
        await engine.dispose()

async def recreate_tables_if_needed():
    """Recreate tables if there are major schema issues"""
    
    if settings.DATABASE_URL.startswith("sqlite"):
        database_url = settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
    else:
        database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    
    engine = create_async_engine(database_url)
    
    try:
        # Create all tables (will only create missing ones)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Ensured all tables exist")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    print("🔧 Starting database schema migration...")
    
    # First ensure all tables exist
    asyncio.run(recreate_tables_if_needed())
    
    # Then check and add missing columns
    asyncio.run(check_and_add_missing_columns())
    
    print("✅ Migration completed!")