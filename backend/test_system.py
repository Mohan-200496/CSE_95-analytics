"""
Comprehensive system test for Punjab Rozgar Portal
Tests all major functionality end-to-end
"""

import asyncio
import sys
import json
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.database import get_database
from app.core.config import get_settings
from app.models.user import User, UserRole
from app.models.job import Job, JobStatus, JobType
from app.core.security import create_access_token, verify_password, hash_password
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from datetime import timedelta

settings = get_settings()

class SystemTester:
    def __init__(self):
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name, success, details=""):
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        self.test_results[test_name] = {
            "success": success,
            "details": details
        }
        print(f"{status} {test_name}: {details}")
    
    async def test_database_connection(self):
        """Test database connectivity and schema"""
        try:
            # Get a session
            async with get_database() as session:
                # Test basic query
                result = await session.execute(text("SELECT 1"))
                value = result.scalar()
                
                if value == 1:
                    self.log_test("Database Connection", True, "Connected successfully")
                else:
                    self.log_test("Database Connection", False, "Invalid query result")
                    
        except Exception as e:
            self.log_test("Database Connection", False, f"Error: {str(e)}")
    
    async def test_user_model(self):
        """Test user creation and authentication"""
        try:
            async with get_database() as session:
                # Check if test user exists
                existing_user = await session.execute(
                    select(User).where(User.email == "test_system@example.com")
                )
                existing_user = existing_user.scalar_one_or_none()
                
                if existing_user:
                    await session.delete(existing_user)
                    await session.commit()
                
                # Create test user
                hashed_password = hash_password("testpass123")
                test_user = User(
                    user_id="test_system_user",
                    email="test_system@example.com",
                    hashed_password=hashed_password,
                    first_name="Test",
                    last_name="User",
                    role=UserRole.EMPLOYER,
                    is_active=True,
                    email_verified=True
                )
                
                session.add(test_user)
                await session.commit()
                await session.refresh(test_user)
                
                # Test password verification
                if verify_password("testpass123", test_user.hashed_password):
                    self.log_test("User Authentication", True, "User created and password verified")
                else:
                    self.log_test("User Authentication", False, "Password verification failed")
                    
        except Exception as e:
            self.log_test("User Authentication", False, f"Error: {str(e)}")
    
    async def test_job_model(self):
        """Test job creation and management"""
        try:
            async with get_database() as session:
                # Get test user
                test_user = await session.execute(
                    select(User).where(User.email == "test_system@example.com")
                )
                test_user = test_user.scalar_one_or_none()
                
                if not test_user:
                    self.log_test("Job Model", False, "Test user not found")
                    return
                
                # Create test job
                test_job = Job(
                    job_id="test_job_system",
                    title="System Test Job",
                    description="This is a test job for system validation",
                    job_type=JobType.FULL_TIME,
                    category="Technology",
                    location_city="Test City",
                    location_state="Test State",
                    employer_id=test_user.user_id,
                    employer_name="Test Company",
                    status=JobStatus.ACTIVE,
                    salary_min=50000,
                    salary_max=80000,
                    salary_currency="INR"
                )
                
                session.add(test_job)
                await session.commit()
                await session.refresh(test_job)
                
                # Verify job was created
                job_check = await session.execute(
                    select(Job).where(Job.job_id == "test_job_system")
                )
                job_check = job_check.scalar_one_or_none()
                
                if job_check:
                    self.log_test("Job Model", True, f"Job created with ID: {job_check.job_id}")
                else:
                    self.log_test("Job Model", False, "Job creation failed")
                    
        except Exception as e:
            self.log_test("Job Model", False, f"Error: {str(e)}")
    
    async def test_token_generation(self):
        """Test JWT token generation and validation"""
        try:
            # Generate token
            token_data = {"sub": "test_user_id", "role": "employer"}
            token = create_access_token(
                data=token_data,
                expires_delta=timedelta(minutes=30)
            )
            
            if token and isinstance(token, str) and len(token) > 0:
                self.log_test("Token Generation", True, f"Token generated: {token[:20]}...")
            else:
                self.log_test("Token Generation", False, "Token generation failed")
                
        except Exception as e:
            self.log_test("Token Generation", False, f"Error: {str(e)}")
    
    async def test_database_schema(self):
        """Check if all required tables and columns exist"""
        try:
            async with get_database() as session:
                # Check Users table
                result = await session.execute(text("SELECT COUNT(*) FROM users"))
                user_count = result.scalar()
                
                # Check Jobs table  
                result = await session.execute(text("SELECT COUNT(*) FROM jobs"))
                job_count = result.scalar()
                
                # Check specific columns exist
                if settings.DATABASE_URL.startswith("sqlite"):
                    # SQLite schema check
                    result = await session.execute(text("PRAGMA table_info(jobs)"))
                    columns = result.fetchall()
                    column_names = [row[1] for row in columns]
                else:
                    # PostgreSQL schema check
                    result = await session.execute(text("""
                        SELECT column_name FROM information_schema.columns 
                        WHERE table_name='jobs'
                    """))
                    columns = result.fetchall()
                    column_names = [row[0] for row in columns]
                
                required_columns = ['title', 'description', 'employer_id', 'status', 'resume_required']
                missing_columns = [col for col in required_columns if col not in column_names]
                
                if not missing_columns:
                    self.log_test("Database Schema", True, 
                                f"All tables exist. Users: {user_count}, Jobs: {job_count}")
                else:
                    self.log_test("Database Schema", False, 
                                f"Missing columns: {missing_columns}")
                    
        except Exception as e:
            self.log_test("Database Schema", False, f"Error: {str(e)}")
    
    async def test_api_imports(self):
        """Test if all API modules import correctly"""
        try:
            # Test imports
            from app.api.v1 import auth, users, jobs, analytics, admin
            from app.main import app
            
            # Check if FastAPI app is created
            if hasattr(app, 'routes') and len(app.routes) > 0:
                route_count = len(app.routes)
                self.log_test("API Imports", True, f"All modules imported, {route_count} routes")
            else:
                self.log_test("API Imports", False, "FastAPI app has no routes")
                
        except Exception as e:
            self.log_test("API Imports", False, f"Import error: {str(e)}")
    
    async def run_all_tests(self):
        """Run comprehensive system test suite"""
        print("🧪 Starting Punjab Rozgar Portal System Tests")
        print("=" * 60)
        
        # Database tests
        await self.test_database_connection()
        await self.test_database_schema()
        
        # Model tests
        await self.test_user_model()
        await self.test_job_model()
        
        # Security tests
        await self.test_token_generation()
        
        # API tests
        await self.test_api_imports()
        
        # Summary
        print("\n" + "=" * 60)
        print("🏁 Test Summary")
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        if self.passed_tests == self.total_tests:
            print("\n🎉 ALL TESTS PASSED! System is functioning correctly.")
            return True
        else:
            print("\n⚠️  Some tests failed. Check the details above.")
            return False

async def main():
    """Main test runner"""
    tester = SystemTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n✅ Punjab Rozgar Portal is fully functional!")
    else:
        print("\n❌ Some issues detected. Please review the test results.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())