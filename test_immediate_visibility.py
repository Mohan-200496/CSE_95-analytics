"""
Test the immediate job visibility after creation
"""
import asyncio
import aiohttp
import time

API_BASE_URL = "https://punjab-rozgar-api.onrender.com/api/v1"

async def test_immediate_job_visibility():
    """Test that jobs are immediately visible after creation"""
    
    print("🧪 Testing Immediate Job Visibility\n")
    
    async with aiohttp.ClientSession() as session:
        
        # Login as employer
        emp_login = await session.post(f"{API_BASE_URL}/auth/login", json={
            "email": "employer@company.com", 
            "password": "employer123"
        })
        
        if emp_login.status != 200:
            print("❌ Employer login failed!")
            return
            
        emp_data = await emp_login.json()
        emp_token = emp_data.get("access_token")
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        
        # Check current job count
        print("1️⃣ Checking initial job count:")
        initial_response = await session.get(f"{API_BASE_URL}/jobs/my-jobs", headers=emp_headers)
        if initial_response.status == 200:
            initial_jobs = await initial_response.json()
            print(f"   Initial jobs: {len(initial_jobs)}")
        else:
            print(f"   ❌ Failed to get initial jobs: {initial_response.status}")
            return
        
        # Create a new job with unique title
        timestamp = int(time.time())
        test_job = {
            "title": f"Immediate Test Job {timestamp}",
            "description": "Testing immediate visibility after creation",
            "requirements": "Testing requirements",
            "responsibilities": "Testing responsibilities",
            "job_type": "full_time",
            "category": "Technology",
            "location_city": "Lahore",
            "salary_min": 50000,
            "salary_max": 75000,
            "contact_email": "test@company.com"
        }
        
        print("\n2️⃣ Creating new job:")
        job_response = await session.post(f"{API_BASE_URL}/jobs/", json=test_job, headers=emp_headers)
        
        if job_response.status == 200:
            job_data = await job_response.json()
            job_id = job_data.get("job_id")
            print(f"   ✅ Job created: {job_id}")
        else:
            error = await job_response.text()
            print(f"   ❌ Job creation failed: {job_response.status}")
            print(f"   Error: {error}")
            return
        
        # Immediately check if job appears
        print("\n3️⃣ Checking job visibility immediately after creation:")
        
        for attempt in range(3):
            print(f"   Attempt {attempt + 1}:")
            
            # Check my-jobs
            my_jobs_response = await session.get(f"{API_BASE_URL}/jobs/my-jobs", headers=emp_headers)
            if my_jobs_response.status == 200:
                my_jobs = await my_jobs_response.json()
                found_job = any(job.get("job_id") == job_id for job in my_jobs)
                print(f"     My-jobs: {len(my_jobs)} total, new job found: {found_job}")
                
                if found_job:
                    print("   ✅ SUCCESS: Job is immediately visible!")
                    break
            else:
                print(f"     ❌ My-jobs failed: {my_jobs_response.status}")
            
            if attempt < 2:  # Don't sleep on last attempt
                await asyncio.sleep(2)
        
        # Check stats
        print("\n4️⃣ Checking job statistics:")
        stats_response = await session.get(f"{API_BASE_URL}/jobs/my-stats", headers=emp_headers)
        if stats_response.status == 200:
            stats = await stats_response.json()
            print(f"   Total jobs: {stats.get('total_jobs', 0)}")
            print(f"   Draft jobs: {stats.get('draft_jobs', 0)}")
        else:
            print(f"   ❌ Stats failed: {stats_response.status}")

if __name__ == "__main__":
    asyncio.run(test_immediate_job_visibility())