"""
Initialize demo accounts in PostgreSQL database
Creates admin, employer, and job seeker demo accounts
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import AsyncSessionLocal, create_tables
from app.models.user import User
from app.models.company import Company
from app.models.admin import Admin
from app.services.auth_service import AuthService
from passlib.context import CryptContext
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_demo_accounts():
    """Create demo accounts for testing"""
    
    logger.info("🚀 Creating demo accounts in PostgreSQL database...")
    
    # Ensure tables exist
    await create_tables()
    
    async with AsyncSessionLocal() as session:
        try:
            # Check if admin already exists
            admin_exists = await session.execute(
                "SELECT email FROM users WHERE email = 'admin@test.com'"
            )
            if admin_exists.fetchone():
                logger.info("✅ Demo accounts already exist")
                return
            
            # Create Admin User
            admin_user = User(
                user_id="admin_demo_001",
                email="admin@test.com",
                password_hash=pwd_context.hash("admin123"),
                first_name="Admin",
                last_name="User", 
                phone="+1234567890",
                user_type="admin",
                is_active=True,
                is_verified=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(admin_user)
            await session.flush()
            
            # Create Admin record
            admin_record = Admin(
                user_id=admin_user.id,
                admin_level="super_admin",
                permissions=["manage_users", "manage_jobs", "view_analytics", "system_admin"],
                created_at=datetime.utcnow()
            )
            session.add(admin_record)
            
            # Create Employer User
            employer_user = User(
                user_id="employer_demo_001", 
                email="employer@test.com",
                password_hash=pwd_context.hash("employer123"),
                first_name="Test",
                last_name="Employer",
                phone="+1234567891", 
                user_type="employer",
                is_active=True,
                is_verified=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(employer_user)
            await session.flush()
            
            # Create Company for Employer
            company = Company(
                company_id="company_demo_001",
                name="Demo Tech Solutions",
                description="A demo technology company for testing",
                industry="Technology",
                location="Punjab, India",
                website="https://demo-tech.com",
                email="hr@demo-tech.com",
                phone="+91-98765-43210",
                employees_count="50-100",
                user_id=employer_user.id,
                is_verified=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(company)
            
            # Create Job Seeker User
            jobseeker_user = User(
                user_id="jobseeker_demo_001",
                email="jobseeker@email.com", 
                password_hash=pwd_context.hash("jobseeker123"),
                first_name="Test",
                last_name="JobSeeker",
                phone="+1234567892",
                user_type="jobseeker", 
                is_active=True,
                is_verified=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(jobseeker_user)
            
            # Commit all changes
            await session.commit()
            
            logger.info("✅ Demo accounts created successfully!")
            logger.info("📋 Demo Accounts:")
            logger.info("   👨‍💼 Admin: admin@test.com / admin123")
            logger.info("   🏢 Employer: employer@test.com / employer123") 
            logger.info("   👤 Job Seeker: jobseeker@email.com / jobseeker123")
            
            return True
            
        except Exception as e:
            await session.rollback()
            logger.error(f"❌ Error creating demo accounts: {e}")
            return False

async def main():
    """Main initialization function"""
    logger.info("🔧 Initializing PostgreSQL database with demo accounts...")
    
    success = await create_demo_accounts()
    
    if success:
        logger.info("🎉 Database initialization completed successfully!")
        logger.info("🌐 You can now login with demo accounts on your frontend")
    else:
        logger.error("💥 Database initialization failed")
        
    return success

if __name__ == "__main__":
    asyncio.run(main())