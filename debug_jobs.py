"""
Debug job creation and employer_id issue
"""
import asyncio
import aiohttp

API_BASE_URL = "https://punjab-rozgar-api.onrender.com/api/v1"

async def debug_job_creation():
    """Debug job creation and employer ID assignment"""
    
    print("🔍 Debugging Job Creation & Employer ID Assignment\n")
    
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
        employer_user = emp_data.get("user", {})
        employer_id = employer_user.get("id") or employer_user.get("user_id")
        
        print(f"✅ Employer logged in:")
        print(f"   Email: {employer_user.get('email')}")
        print(f"   User ID: {employer_user.get('user_id')}")
        print(f"   Internal ID: {employer_user.get('id')}")
        print(f"   Role: {employer_user.get('role')}")
        
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        
        # Create a simple test job
        test_job = {
            "title": "Debug Test Job",
            "description": "Test job for debugging employer ID assignment",
            "requirements": "Testing only",
            "responsibilities": "Debug testing",
            "job_type": "full_time",
            "category": "Technology",
            "location_city": "Lahore",
            "salary_min": 50000,
            "salary_max": 80000,
            "contact_email": "test@company.com"
        }
        
        # Create job
        job_response = await session.post(f"{API_BASE_URL}/jobs/", json=test_job, headers=emp_headers)
        
        if job_response.status == 200:
            job_data = await job_response.json()
            job_id = job_data.get("job_id")
            print(f"\n✅ Job created successfully:")
            print(f"   Job ID: {job_id}")
            print(f"   Title: {job_data.get('title')}")
            print(f"   Status: {job_data.get('status')}")
            print(f"   Employer ID in response: {job_data.get('employer_id')}")
        else:
            error_text = await job_response.text()
            print(f"\n❌ Job creation failed: {job_response.status}")
            print(f"   Error: {error_text}")
            return
        
        # Check my-jobs endpoint
        print(f"\n🔍 Checking my-jobs endpoint:")
        my_jobs_response = await session.get(f"{API_BASE_URL}/jobs/my-jobs", headers=emp_headers)
        
        if my_jobs_response.status == 200:
            my_jobs = await my_jobs_response.json()
            print(f"✅ My-jobs endpoint works: {len(my_jobs)} jobs found")
            for job in my_jobs:
                print(f"   - {job.get('title')}: {job.get('status')} (employer_id: {job.get('employer_id')})")
        else:
            error_text = await my_jobs_response.text()
            print(f"❌ My-jobs failed: {my_jobs_response.status}")
            print(f"   Error: {error_text}")
        
        # Check all jobs with employer filter
        print(f"\n🔍 Checking jobs with employer_id filter:")
        all_jobs_response = await session.get(f"{API_BASE_URL}/jobs/?employer_id={employer_id}&only_active=false", headers=emp_headers)
        
        if all_jobs_response.status == 200:
            all_jobs = await all_jobs_response.json()
            print(f"✅ Employer filter works: {len(all_jobs)} jobs found")
            for job in all_jobs:
                print(f"   - {job.get('title')}: {job.get('status')}")
        else:
            error_text = await all_jobs_response.text()
            print(f"❌ Employer filter failed: {all_jobs_response.status}")
            print(f"   Error: {error_text}")

if __name__ == "__main__":
    asyncio.run(debug_job_creation())