import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import async_engine
from app.models.user import User, UserRole, AccountStatus
from app.models.company import Company
from app.core.security import hash_password
import uuid

async def create_proper_test_users():
    try:
        # Create session manually
        async with AsyncSession(async_engine) as session:
            # Delete old test users if they exist
            result = await session.execute(select(User).where(User.email == "employer@test.com"))
            existing_user = result.scalar_one_or_none()
            if existing_user:
                await session.delete(existing_user)
                print("🗑️ Removed old employer test user")
            
            result = await session.execute(select(User).where(User.email == "jobseeker@test.com"))
            existing_user = result.scalar_one_or_none()
            if existing_user:
                await session.delete(existing_user)
                print("🗑️ Removed old job seeker test user")
            
            await session.commit()
            
            # Create employer user with new model
            employer_user = User(
                user_id=f"emp_{uuid.uuid4().hex[:12]}",
                email="employer@test.com",
                hashed_password=hash_password("test123"),
                role=UserRole.EMPLOYER,
                status=AccountStatus.ACTIVE,
                first_name="Test",
                last_name="Employer",
                email_verified=True,
                phone_verified=False,
                city="Chandigarh",
                state="Punjab"
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
            print("✅ Employer user created with proper model")
            
            # Create job seeker user with new model
            jobseeker_user = User(
                user_id=f"js_{uuid.uuid4().hex[:12]}",
                email="jobseeker@test.com",
                hashed_password=hash_password("test123"),
                role=UserRole.JOB_SEEKER,
                status=AccountStatus.ACTIVE,
                first_name="Test",
                last_name="JobSeeker",
                email_verified=True,
                phone_verified=False,
                city="Ludhiana",
                state="Punjab"
            )
            session.add(jobseeker_user)
            print("✅ Job seeker user created with proper model")
            
            await session.commit()
            
            print("\n🎉 Test users ready with proper authentication!")
            print("📧 Employer: employer@test.com / test123")
            print("👤 Job Seeker: jobseeker@test.com / test123")
            print("\n🚀 Now you can:")
            print("1. Login with the demo credentials")
            print("2. Test the enhanced job posting workflow!")
    
    except Exception as e:
        print(f"❌ Error creating test users: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_proper_test_users())