"""
Cloud Database Migration Script for Punjab Rozgar Portal
Migrates from SQLite to PostgreSQL with data preservation
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.core.database import Base
from app.models.user import User, UserProfile, UserPreferences, UserVerification
from app.models.job import Job, JobApplication, SavedJob, JobAlert, JobView, JobCategory
from app.models.analytics import AnalyticsEvent, PageView, UserSession, JobInteraction
from app.models.admin import AdminUser, SystemLog, JobModerationLog

async def setup_cloud_database():
    """Set up cloud database with proper schema"""
    
    # Get database URL from environment
    database_url = os.getenv("CLOUD_DATABASE_URL")
    if not database_url:
        print("❌ CLOUD_DATABASE_URL environment variable not set!")
        print("Set it like: export CLOUD_DATABASE_URL='postgresql://user:pass@host:5432/db'")
        return False
    
    print("🌐 Setting up cloud database...")
    print(f"📍 Database URL: {database_url.split('@')[0]}@****")
    
    try:
        # Create async engine for PostgreSQL
        async_engine = create_async_engine(
            database_url.replace("postgresql://", "postgresql+asyncpg://"),
            pool_size=10,
            max_overflow=20,
            echo=False
        )
        
        # Create all tables
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Database schema created successfully!")
        
        # Test connection
        async with AsyncSession(async_engine) as session:
            result = await session.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"📊 Database version: {version}")
        
        await async_engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {str(e)}")
        return False

async def migrate_data_to_cloud():
    """Migrate existing data from SQLite to cloud database"""
    
    sqlite_path = "punjab_rozgar.db"
    if not os.path.exists(sqlite_path):
        print(f"ℹ️  No local SQLite database found at {sqlite_path}")
        return True
    
    cloud_db_url = os.getenv("CLOUD_DATABASE_URL")
    if not cloud_db_url:
        print("❌ CLOUD_DATABASE_URL not set!")
        return False
    
    print("🔄 Migrating data from SQLite to cloud database...")
    
    try:
        # Source: SQLite
        sqlite_engine = create_engine(f"sqlite:///{sqlite_path}")
        
        # Target: Cloud PostgreSQL
        postgres_engine = create_engine(cloud_db_url)
        
        # Migration queries
        migration_tables = [
            "users",
            "user_profiles", 
            "user_preferences",
            "jobs",
            "job_applications",
            "saved_jobs",
            "analytics_events",
            "page_views",
            "user_sessions"
        ]
        
        total_migrated = 0
        
        for table in migration_tables:
            try:
                # Read from SQLite
                with sqlite_engine.connect() as sqlite_conn:
                    result = sqlite_conn.execute(text(f"SELECT * FROM {table}"))
                    rows = result.fetchall()
                    columns = result.keys()
                
                if not rows:
                    print(f"  📊 {table}: No data to migrate")
                    continue
                
                # Write to PostgreSQL
                with postgres_engine.connect() as postgres_conn:
                    # Build insert statement
                    col_names = ", ".join(columns)
                    placeholders = ", ".join([f":{col}" for col in columns])
                    insert_sql = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"
                    
                    # Convert rows to dictionaries
                    data = [dict(zip(columns, row)) for row in rows]
                    
                    # Execute batch insert
                    postgres_conn.execute(text(insert_sql), data)
                    postgres_conn.commit()
                    
                    total_migrated += len(rows)
                    print(f"  ✅ {table}: Migrated {len(rows)} records")
                    
            except Exception as e:
                print(f"  ⚠️  {table}: Migration failed - {str(e)}")
                continue
        
        print(f"🎉 Migration completed! Total records migrated: {total_migrated}")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

def update_env_file():
    """Update .env file with cloud database configuration"""
    
    env_path = Path("backend/.env")
    cloud_db_url = os.getenv("CLOUD_DATABASE_URL")
    
    if not cloud_db_url:
        print("❌ CLOUD_DATABASE_URL not set!")
        return False
    
    print("📝 Updating .env file...")
    
    # Read existing .env or create new one
    env_lines = []
    if env_path.exists():
        with open(env_path, 'r') as f:
            env_lines = f.readlines()
    
    # Update DATABASE_URL
    updated = False
    for i, line in enumerate(env_lines):
        if line.startswith('DATABASE_URL='):
            env_lines[i] = f'DATABASE_URL={cloud_db_url}\n'
            updated = True
            break
    
    if not updated:
        env_lines.append(f'DATABASE_URL={cloud_db_url}\n')
    
    # Add cloud-specific settings
    cloud_settings = [
        'DATABASE_POOL_SIZE=10\n',
        'DATABASE_MAX_OVERFLOW=20\n',
        'DATABASE_CONNECT_TIMEOUT=30\n'
    ]
    
    for setting in cloud_settings:
        key = setting.split('=')[0]
        if not any(line.startswith(f'{key}=') for line in env_lines):
            env_lines.append(setting)
    
    # Write updated .env
    env_path.parent.mkdir(exist_ok=True)
    with open(env_path, 'w') as f:
        f.writelines(env_lines)
    
    print(f"✅ .env file updated at {env_path}")
    return True

async def create_demo_data():
    """Create demo users in cloud database"""
    
    cloud_db_url = os.getenv("CLOUD_DATABASE_URL")
    if not cloud_db_url:
        return False
    
    print("👥 Creating demo users in cloud database...")
    
    try:
        async_engine = create_async_engine(
            cloud_db_url.replace("postgresql://", "postgresql+asyncpg://"),
            pool_size=10,
            max_overflow=20
        )
        
        async with AsyncSession(async_engine) as session:
            from app.core.security import hash_password
            from app.models.user import UserRole
            
            # Check if demo users already exist
            existing_user = await session.execute(
                text("SELECT email FROM users WHERE email = 'admin@test.com'")
            )
            
            if existing_user.scalar():
                print("✅ Demo users already exist in cloud database")
                await async_engine.dispose()
                return True
            
            # Create demo users
            demo_users = [
                {
                    'user_id': 'admin_user_001',
                    'email': 'admin@test.com',
                    'hashed_password': hash_password('admin123'),
                    'first_name': 'Admin',
                    'last_name': 'User',
                    'role': UserRole.ADMIN.value,
                    'status': 'active'
                },
                {
                    'user_id': 'employer_user_001',
                    'email': 'employer@test.com', 
                    'hashed_password': hash_password('employer123'),
                    'first_name': 'Employer',
                    'last_name': 'Demo',
                    'role': UserRole.EMPLOYER.value,
                    'status': 'active',
                    'company_name': 'Demo Company Ltd'
                },
                {
                    'user_id': 'jobseeker_user_001',
                    'email': 'jobseeker@email.com',
                    'hashed_password': hash_password('jobseeker123'),
                    'first_name': 'Job',
                    'last_name': 'Seeker',
                    'role': UserRole.JOB_SEEKER.value,
                    'status': 'active'
                }
            ]
            
            for user_data in demo_users:
                # Insert user
                insert_query = text("""
                    INSERT INTO users (user_id, email, hashed_password, first_name, last_name, role, status, company_name, created_at, updated_at)
                    VALUES (:user_id, :email, :hashed_password, :first_name, :last_name, :role, :status, :company_name, NOW(), NOW())
                """)
                
                await session.execute(insert_query, {
                    **user_data,
                    'company_name': user_data.get('company_name')
                })
                
                print(f"  ✅ Created user: {user_data['email']}")
            
            await session.commit()
            await async_engine.dispose()
            
            print("🎉 Demo users created successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Failed to create demo users: {str(e)}")
        return False

async def main():
    """Main migration workflow"""
    
    print("🚀 Punjab Rozgar Portal - Cloud Database Setup")
    print("=" * 60)
    
    # Check environment variable
    if not os.getenv("CLOUD_DATABASE_URL"):
        print("\n❌ Missing CLOUD_DATABASE_URL environment variable!")
        print("\n📋 Setup Instructions:")
        print("1. Create a cloud PostgreSQL database (Supabase, Render, Neon, etc.)")
        print("2. Set environment variable:")
        print("   export CLOUD_DATABASE_URL='postgresql://user:pass@host:5432/db'")
        print("3. Run this script again")
        return
    
    # Step 1: Setup cloud database schema
    print("\n1️⃣  Setting up cloud database schema...")
    if not await setup_cloud_database():
        return
    
    # Step 2: Migrate existing data (if any)
    print("\n2️⃣  Migrating existing data...")
    if not await migrate_data_to_cloud():
        return
    
    # Step 3: Update configuration
    print("\n3️⃣  Updating configuration...")
    if not update_env_file():
        return
    
    # Step 4: Create demo data
    print("\n4️⃣  Creating demo users...")
    if not await create_demo_data():
        return
    
    print("\n🎉 Cloud database setup completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Update your deployment environment variables")
    print("2. Restart your application")
    print("3. Test login with demo accounts:")
    print("   • Admin: admin@test.com / admin123")
    print("   • Employer: employer@test.com / employer123")
    print("   • Job Seeker: jobseeker@email.com / jobseeker123")

if __name__ == "__main__":
    asyncio.run(main())