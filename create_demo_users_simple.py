"""
Create demo users directly in the database using simple script
"""
import asyncio
import os

# Set environment variable for database
os.environ['DATABASE_URL'] = 'postgresql://postgres.gdcrvcvpqzoxsttbecza:EL5kW8V2HLIp!0W@aws-0-us-west-1.pooler.supabase.com:6543/postgres'

async def create_demo_users():
    """Create demo users using raw SQL to avoid model import issues"""
    
    try:
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy import text
        from passlib.context import CryptContext
        from datetime import datetime
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Create async engine
        async_engine = create_async_engine(
            "postgresql+asyncpg://postgres.gdcrvcvpqzoxsttbecza:EL5kW8V2HLIp!0W@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
        )
        
        async with AsyncSession(async_engine) as session:
            # Check if users already exist
            result = await session.execute(
                text("SELECT email FROM users WHERE email = 'admin@test.com'")
            )
            if result.scalar():
                print("✅ Demo users already exist!")
                return
                
            print("🚀 Creating demo users...")
            
            # Create demo users with raw SQL
            now = datetime.utcnow().isoformat()
            
            await session.execute(text("""
                INSERT INTO users (user_id, email, hashed_password, first_name, last_name, phone, role, status, email_verified, created_at, updated_at)
                VALUES 
                ('admin_demo_001', 'admin@test.com', :admin_hash, 'Admin', 'User', '+1234567890', 'admin', 'active', true, :now, :now),
                ('employer_demo_001', 'employer@test.com', :employer_hash, 'Test', 'Employer', '+1234567891', 'employer', 'active', true, :now, :now),
                ('jobseeker_demo_001', 'jobseeker@email.com', :jobseeker_hash, 'Test', 'JobSeeker', '+1234567892', 'job_seeker', 'active', true, :now, :now)
            """), {
                'admin_hash': pwd_context.hash("admin123"),
                'employer_hash': pwd_context.hash("employer123"),
                'jobseeker_hash': pwd_context.hash("jobseeker123"),
                'now': now
            })
            
            await session.commit()
            
            print("✅ Demo users created successfully!")
            print("📋 Login credentials:")
            print("  • Admin: admin@test.com / admin123")
            print("  • Employer: employer@test.com / employer123")
            print("  • Job Seeker: jobseeker@email.com / jobseeker123")
            
    except Exception as e:
        print(f"❌ Error creating demo users: {e}")
        return False
        
    return True

if __name__ == "__main__":
    asyncio.run(create_demo_users())