"""
Create demo users for Punjab Rozgar Portal
Run this script to populate the database with demo accounts
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.database import get_database
from app.models.user import User, UserRole
from app.core.security import hash_password
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def create_demo_users():
    """Create demo users for testing"""
    
    async for session in get_database():
        try:
            print("🚀 Creating demo users for Punjab Rozgar Portal...")
            
            # Check if users already exist
            existing_users = await session.execute(
                select(User).where(User.email.in_([
                    'admin@punjabrozgar.gov.pk',
                    'employer@company.com', 
                    'jobseeker@email.com'
                ]))
            )
            if existing_users.scalars().first():
                print("✅ Demo users already exist!")
                return
            
            # Create demo users
            demo_users = [
                {
                    'email': 'admin@punjabrozgar.gov.pk',
                    'password': 'admin123',
                    'first_name': 'Admin',
                    'last_name': 'User',
                    'role': UserRole.ADMIN,
                    'is_active': True,
                    'is_verified': True
                },
                {
                    'email': 'employer@company.com',
                    'password': 'employer123',
                    'first_name': 'Employer',
                    'last_name': 'Demo',
                    'role': UserRole.EMPLOYER,
                    'is_active': True,
                    'is_verified': True
                },
                {
                    'email': 'jobseeker@email.com',
                    'password': 'jobseeker123',
                    'first_name': 'Job',
                    'last_name': 'Seeker',
                    'role': UserRole.JOB_SEEKER,
                    'is_active': True,
                    'is_verified': True
                }
            ]
            
            for user_data in demo_users:
                # Hash password
                hashed_password = hash_password(user_data['password'])
                
                # Create user
                user = User(
                    email=user_data['email'],
                    hashed_password=hashed_password,
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    role=user_data['role'],
                    is_active=user_data['is_active'],
                    is_verified=user_data['is_verified']
                )
                
                session.add(user)
                print(f"✅ Created user: {user_data['email']} ({user_data['role'].value})")
            
            await session.commit()
            print("🎉 Demo users created successfully!")
            print("\n📋 Demo Login Credentials:")
            print("👨‍💼 Admin: admin@punjabrozgar.gov.pk / admin123")
            print("🏢 Employer: employer@company.com / employer123")  
            print("👤 Job Seeker: jobseeker@email.com / jobseeker123")
            
        except Exception as e:
            print(f"❌ Error creating demo users: {str(e)}")
            await session.rollback()
            raise
        finally:
            await session.close()

if __name__ == "__main__":
    asyncio.run(create_demo_users())