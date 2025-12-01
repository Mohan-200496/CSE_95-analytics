"""
Fix database enum values for job types
"""

import asyncio
import sys
sys.path.append('backend')

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_engine
from sqlalchemy import text

async def fix_enum_values():
    """Fix the enum values in the database"""
    
    engine = get_async_engine()
    
    try:
        async with engine.begin() as conn:
            print("🔧 Checking current enum values...")
            
            # Check current enum values
            result = await conn.execute(text("""
                SELECT enumlabel 
                FROM pg_enum 
                WHERE enumtypid = (
                    SELECT oid 
                    FROM pg_type 
                    WHERE typname = 'jobtype'
                )
                ORDER BY enumsortorder;
            """))
            
            current_values = [row[0] for row in result]
            print(f"Current enum values: {current_values}")
            
            # Expected values
            expected_values = ['full_time', 'part_time', 'contract', 'temporary', 'internship', 'freelance']
            
            # Add missing values
            for value in expected_values:
                if value not in current_values:
                    print(f"Adding missing enum value: {value}")
                    await conn.execute(text(f"ALTER TYPE jobtype ADD VALUE '{value}';"))
            
            print("✅ Enum values fixed!")
            
            # Now try to create a test job
            print("\n🧪 Testing job creation...")
            
            # First, get a test user
            user_result = await conn.execute(text("""
                SELECT user_id, email, role 
                FROM users 
                WHERE role IN ('employer', 'admin') 
                LIMIT 1
            """))
            
            user_row = user_result.first()
            if not user_row:
                print("❌ No test employer/admin user found")
                return
            
            user_id, email, role = user_row
            print(f"Using test user: {email} (ID: {user_id}, Role: {role})")
            
            # Create a test job
            import uuid
            job_id = f"job_test_{uuid.uuid4().hex[:8]}"
            
            await conn.execute(text("""
                INSERT INTO jobs (
                    job_id, title, description, job_type, category, 
                    location_city, location_state, employer_id, employer_name, 
                    employer_type, status, created_at, updated_at, 
                    remote_allowed, salary_min, salary_max
                ) VALUES (
                    :job_id, :title, :description, :job_type, :category,
                    :location_city, :location_state, :employer_id, :employer_name,
                    :employer_type, :status, NOW(), NOW(),
                    :remote_allowed, :salary_min, :salary_max
                )
            """), {
                'job_id': job_id,
                'title': 'Test Job - Database Fixed',
                'description': 'This is a test job to verify the database enum fix is working.',
                'job_type': 'full_time',
                'category': 'Technology',
                'location_city': 'Lahore',
                'location_state': 'Punjab',
                'employer_id': user_id,
                'employer_name': 'Test Company',
                'employer_type': 'private',
                'status': 'active',
                'remote_allowed': False,
                'salary_min': 50000,
                'salary_max': 70000
            })
            
            print(f"✅ Test job created successfully! Job ID: {job_id}")
            
            # Verify the job was created
            job_check = await conn.execute(text("""
                SELECT job_id, title, job_type, status 
                FROM jobs 
                WHERE job_id = :job_id
            """), {'job_id': job_id})
            
            job_row = job_check.first()
            if job_row:
                print(f"✅ Job verified: {job_row[1]} (Type: {job_row[2]}, Status: {job_row[3]})")
            else:
                print("❌ Job not found after creation")
                
    except Exception as e:
        print(f"❌ Error fixing enum values: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(fix_enum_values())