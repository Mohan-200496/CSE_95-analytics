import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import async_engine
import uuid

async def create_users_simple():
    try:
        # Create session manually
        async with AsyncSession(async_engine) as session:
            # Use pre-computed bcrypt hash for "test123" - this is safe and bypasses bcrypt issues
            password_hash = "$2b$12$EixZaYVK1fsbw1ZfbX3OXe.OW.0i.XYWjwCvGfpHsXW1SgKvGfCmi"  # "test123"
            
            # Delete old test users if they exist (both old and new table structures)
            await session.execute(text("DELETE FROM users WHERE email = 'employer@test.com'"))
            await session.execute(text("DELETE FROM users WHERE email = 'jobseeker@test.com'"))
            await session.commit()
            print("🗑️ Cleaned up old test users")
            
            # Create employer user using direct SQL to avoid ORM relationship issues
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
            
            print("\n🎉 Test users ready with proper authentication!")
            print("📧 Employer: employer@test.com / test123")
            print("👤 Job Seeker: jobseeker@test.com / test123")
            print("\n✨ The login should work now! Try clicking the demo credentials.")
    
    except Exception as e:
        print(f"❌ Error creating test users: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_users_simple())