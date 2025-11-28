"""
Quick script to create test users for immediate testing
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

from app.core.database import get_database_engine, get_async_session_local
from app.models.user import User, UserRole, AccountStatus
from app.core.security import hash_password
import uuid


async def create_test_users():
    """Create test users with short passwords for immediate testing"""
    
    # Create async session
    engine = get_database_engine()
    SessionLocal = get_async_session_local()
    
    async with SessionLocal() as db:
        try:
            print("Creating test users...")
            
            # Create test employer
            employer = User(
                user_id=f"user_{uuid.uuid4().hex[:12]}",
                email="employer@test.com",
                hashed_password=hash_password("test123"),
                first_name="Test",
                last_name="Employer",
                role=UserRole.EMPLOYER,
                city="Chandigarh",
                status=AccountStatus.ACTIVE
            )
            
            # Create test job seeker
            jobseeker = User(
                user_id=f"user_{uuid.uuid4().hex[:12]}",
                email="jobseeker@test.com",
                hashed_password=hash_password("test123"),
                first_name="Test",
                last_name="JobSeeker",
                role=UserRole.JOB_SEEKER,
                city="Punjab",
                status=AccountStatus.ACTIVE
            )
            
            db.add(employer)
            db.add(jobseeker)
            
            await db.commit()
            
            print("✅ Test users created successfully!")
            print("\n📧 Test Accounts:")
            print("🏢 Employer Account:")
            print("   Email: employer@test.com")
            print("   Password: test123")
            print("   Role: Employer")
            print("\n👤 Job Seeker Account:")
            print("   Email: jobseeker@test.com")  
            print("   Password: test123")
            print("   Role: Job Seeker")
            print("\n🚀 You can now login and test the enhanced job posting workflow!")
            
        except Exception as e:
            print(f"❌ Error creating test users: {e}")
            await db.rollback()


if __name__ == "__main__":
    asyncio.run(create_test_users())