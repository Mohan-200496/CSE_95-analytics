import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import async_engine

async def create_test_users():
    try:
        # Create session manually
        async with AsyncSession(async_engine) as session:
            # Use a pre-generated bcrypt hash for "test123"
            password_hash = "$2b$12$EixZaYVK1fsbw1ZfbX3OXe.OW.0i.XYWjwCvGfpHsXW1SgKvGfCmi"  # "test123"
            
            # Check if employer exists
            result = await session.execute(text("SELECT id FROM users WHERE email = 'employer@test.com'"))
            employer_exists = result.fetchone()
            
            if employer_exists:
                print("⚠️  Employer test user already exists")
            else:
                # Create employer user with correct column names
                await session.execute(text("""
                    INSERT INTO users (
                        user_id, email, hashed_password, role, status, 
                        first_name, last_name, created_at, updated_at,
                        email_verified, profile_public, email_notifications
                    ) VALUES (
                        :user_id, :email, :hashed_password, :role, :status,
                        :first_name, :last_name, datetime('now'), datetime('now'),
                        :email_verified, :profile_public, :email_notifications
                    )
                """), {
                    'user_id': 'emp_test_001',
                    'email': 'employer@test.com',
                    'hashed_password': password_hash,
                    'role': 'employer',
                    'status': 'active',
                    'first_name': 'Test',
                    'last_name': 'Employer',
                    'email_verified': True,
                    'profile_public': True,
                    'email_notifications': True
                })
                
                print("✅ Employer user created")
            
            # Check if jobseeker exists
            result = await session.execute(text("SELECT id FROM users WHERE email = 'jobseeker@test.com'"))
            jobseeker_exists = result.fetchone()
            
            if jobseeker_exists:
                print("⚠️  Job seeker test user already exists")
            else:
                # Create job seeker user with correct column names
                await session.execute(text("""
                    INSERT INTO users (
                        user_id, email, hashed_password, role, status,
                        first_name, last_name, created_at, updated_at,
                        email_verified, profile_public, email_notifications
                    ) VALUES (
                        :user_id, :email, :hashed_password, :role, :status,
                        :first_name, :last_name, datetime('now'), datetime('now'),
                        :email_verified, :profile_public, :email_notifications
                    )
                """), {
                    'user_id': 'js_test_001',
                    'email': 'jobseeker@test.com',
                    'hashed_password': password_hash,
                    'role': 'jobseeker',
                    'status': 'active',
                    'first_name': 'Test',
                    'last_name': 'JobSeeker',
                    'email_verified': True,
                    'profile_public': True,
                    'email_notifications': True
                })
                
                print("✅ Job seeker user created")
            
            await session.commit()
            
            print("\n🎉 Test users ready!")
            print("📧 Employer: employer@test.com / test123")
            print("👤 Job Seeker: jobseeker@test.com / test123")
            print("\n🚀 Now you can:")
            print("1. Open http://localhost:3000/pages/auth/login.html")
            print("2. Login with employer@test.com / test123")
            print("3. Test the enhanced job posting workflow!")
            print("   - Try different application methods (online/email/offline)")
            print("   - Toggle resume requirements")
            print("   - See how the application UI adapts to your choices")
    
    except Exception as e:
        print(f"❌ Error creating test users: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_test_users())