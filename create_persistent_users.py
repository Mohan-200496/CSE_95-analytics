import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import async_engine
import uuid

async def create_persistent_users():
    try:
        # Create session manually
        async with AsyncSession(async_engine) as session:
            # Use pre-computed bcrypt hash for "test123" 
            password_hash = "$2b$12$EixZaYVK1fsbw1ZfbX3OXe.OW.0i.XYWjwCvGfpHsXW1SgKvGfCmi"  # "test123"
            
            # Check if users already exist first
            result = await session.execute(text("SELECT COUNT(*) FROM users WHERE email IN ('employer@test.com', 'jobseeker@test.com')"))
            count = result.scalar()
            
            if count > 0:
                print("✅ Test users already exist in database")
                return
            
            print("🔧 Creating new test users...")
            
            # Create employer user using direct SQL 
            employer_user_id = f"emp_{uuid.uuid4().hex[:12]}"
            await session.execute(text("""
                INSERT INTO users (
                    user_id, email, hashed_password, role, status,
                    first_name, last_name, city, state,
                    created_at, updated_at, email_verified, phone_verified
                ) VALUES (
                    :user_id, :email, :hashed_password, :role, :status,
                    :first_name, :last_name, :city, :state,
                    datetime('now'), datetime('now'), :email_verified, :phone_verified
                )
            """), {
                'user_id': employer_user_id,
                'email': 'employer@test.com',
                'hashed_password': password_hash,
                'role': 'employer',
                'status': 'active',
                'first_name': 'Test',
                'last_name': 'Employer',
                'city': 'Chandigarh',
                'state': 'Punjab',
                'email_verified': True,
                'phone_verified': False
            })
            
            print("✅ Employer user created")
            
            # Create job seeker user using direct SQL
            jobseeker_user_id = f"js_{uuid.uuid4().hex[:12]}"
            await session.execute(text("""
                INSERT INTO users (
                    user_id, email, hashed_password, role, status,
                    first_name, last_name, city, state,
                    created_at, updated_at, email_verified, phone_verified
                ) VALUES (
                    :user_id, :email, :hashed_password, :role, :status,
                    :first_name, :last_name, :city, :state,
                    datetime('now'), datetime('now'), :email_verified, :phone_verified
                )
            """), {
                'user_id': jobseeker_user_id,
                'email': 'jobseeker@test.com',
                'hashed_password': password_hash,
                'role': 'job_seeker',
                'status': 'active',
                'first_name': 'Test',
                'last_name': 'JobSeeker',
                'city': 'Ludhiana',
                'state': 'Punjab',
                'email_verified': True,
                'phone_verified': False
            })
            
            print("✅ Job seeker user created")
            
            await session.commit()
            
            print("\n🎉 Test users are ready and persistent!")
            print("📧 Employer: employer@test.com / test123")
            print("👤 Job Seeker: jobseeker@test.com / test123")
            
            # Verify users exist
            result = await session.execute(text("SELECT email, role FROM users WHERE email IN ('employer@test.com', 'jobseeker@test.com')"))
            users = result.fetchall()
            print(f"\n✅ Verified {len(users)} users in database:")
            for user in users:
                print(f"   - {user[0]} ({user[1]})")
    
    except Exception as e:
        print(f"❌ Error creating test users: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_persistent_users())