import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import async_engine
from app.models.user import User
from app.models.company import Company
from app.core.security import hash_password

async def create_test_users():
    try:
        # Create session manually
        async with AsyncSession(async_engine) as session:
            # Check if users already exist
            result = await session.execute(select(User).where(User.email == "employer@test.com"))
            if result.scalar_one_or_none():
                print("⚠️  Employer test user already exists")
            else:
                # Create employer
                employer_user = User(
                    email="employer@test.com",
                    password_hash=hash_password("test123"),
                    user_type="employer",
                    full_name="Test Employer",
                    is_active=True
                )
                session.add(employer_user)
                await session.flush()  # Get the ID
                
                # Create company for employer
                company = Company(
                    user_id=employer_user.id,
                    company_name="Test Company",
                    industry="Technology",
                    company_size="50-100",
                    location="Chandigarh",
                    description="A test company for demonstrations"
                )
                session.add(company)
                print("✅ Employer user created")
            
            # Check jobseeker
            result = await session.execute(select(User).where(User.email == "jobseeker@test.com"))
            if result.scalar_one_or_none():
                print("⚠️  Job seeker test user already exists")
            else:
                # Create job seeker
                jobseeker_user = User(
                    email="jobseeker@test.com",
                    password_hash=hash_password("test123"),
                    user_type="jobseeker",
                    full_name="Test Job Seeker",
                    is_active=True
                )
                session.add(jobseeker_user)
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