import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.core.database import async_engine
from app.core.security import hash_password

async def create_test_users():
    try:
        # Create session manually
        async with AsyncSession(async_engine) as session:
            # Check if employer exists
            result = await session.execute(text("SELECT id FROM users WHERE email = 'employer@test.com'"))
            employer_exists = result.fetchone()
            
            if employer_exists:
                print("⚠️  Employer test user already exists")
            else:
                # Create employer user directly with SQL
                await session.execute(text("""
                    INSERT INTO users (email, password_hash, user_type, full_name, is_active, created_at, updated_at)
                    VALUES (:email, :password_hash, :user_type, :full_name, :is_active, datetime('now'), datetime('now'))
                """), {
                    'email': 'employer@test.com',
                    'password_hash': hash_password("test123"),
                    'user_type': 'employer',
                    'full_name': 'Test Employer',
                    'is_active': True
                })
                
                # Get the user ID
                result = await session.execute(text("SELECT id FROM users WHERE email = 'employer@test.com'"))
                user_id = result.fetchone()[0]
                
                # Create company for employer
                await session.execute(text("""
                    INSERT INTO companies (user_id, company_name, industry, company_size, location, description, created_at, updated_at)
                    VALUES (:user_id, :company_name, :industry, :company_size, :location, :description, datetime('now'), datetime('now'))
                """), {
                    'user_id': user_id,
                    'company_name': 'Test Company',
                    'industry': 'Technology',
                    'company_size': '50-100',
                    'location': 'Chandigarh',
                    'description': 'A test company for demonstrations'
                })
                
                print("✅ Employer user created")
            
            # Check if jobseeker exists
            result = await session.execute(text("SELECT id FROM users WHERE email = 'jobseeker@test.com'"))
            jobseeker_exists = result.fetchone()
            
            if jobseeker_exists:
                print("⚠️  Job seeker test user already exists")
            else:
                # Create job seeker user directly with SQL
                await session.execute(text("""
                    INSERT INTO users (email, password_hash, user_type, full_name, is_active, created_at, updated_at)
                    VALUES (:email, :password_hash, :user_type, :full_name, :is_active, datetime('now'), datetime('now'))
                """), {
                    'email': 'jobseeker@test.com',
                    'password_hash': hash_password("test123"),
                    'user_type': 'jobseeker',
                    'full_name': 'Test Job Seeker',
                    'is_active': True
                })
                
                print("✅ Job seeker user created")
            
            await session.commit()
            
            print("\n🎉 Test users ready!")
            print("📧 Employer: employer@test.com / test123")
            print("👤 Job Seeker: jobseeker@test.com / test123")
    
    except Exception as e:
        print(f"❌ Error creating test users: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_test_users())