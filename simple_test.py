"""
Simple test using requests to check job creation and visibility
"""
import requests
import time
import json

API_BASE_URL = "https://punjab-rozgar-api.onrender.com/api/v1"

def test_job_creation_flow():
    """Test complete job creation and visibility flow"""
    
    print("🧪 Testing Job Creation and Visibility Flow\n")
    
    # Login as employer
    print("1️⃣ Logging in as employer...")
    emp_login = requests.post(f"{API_BASE_URL}/auth/login", json={
        "email": "employer@test.com", 
        "password": "employer123"
    })
    
    if emp_login.status_code != 200:
        print(f"❌ Employer login failed: {emp_login.status_code}")
        print(f"Response: {emp_login.text}")
        return
        
    emp_data = emp_login.json()
    emp_token = emp_data.get("access_token")
    emp_headers = {"Authorization": f"Bearer {emp_token}"}
    print("✅ Employer login successful")
    
    # Check current stats
    print("\n2️⃣ Checking initial stats...")
    initial_stats = requests.get(f"{API_BASE_URL}/jobs/my-stats", headers=emp_headers)
    if initial_stats.status_code == 200:
        stats = initial_stats.json()
        print(f"   Initial total jobs: {stats.get('total_jobs', 0)}")
        print(f"   Initial draft jobs: {stats.get('draft_jobs', 0)}")
    else:
        print(f"   ❌ Stats failed: {initial_stats.status_code}")
    
    # Check current jobs
    print("\n3️⃣ Checking initial jobs list...")
    initial_jobs = requests.get(f"{API_BASE_URL}/jobs/my-jobs", headers=emp_headers)
    if initial_jobs.status_code == 200:
        jobs = initial_jobs.json()
        print(f"   Initial jobs count: {len(jobs)}")
        for job in jobs[:3]:  # Show first 3 jobs
            print(f"     - {job.get('title', 'No title')} (ID: {job.get('job_id', 'No ID')})")
    else:
        print(f"   ❌ Jobs list failed: {initial_jobs.status_code}")
        print(f"   Response: {initial_jobs.text}")
        return
    
    # Create a new job
    timestamp = int(time.time())
    test_job = {
        "title": f"Test Job {timestamp}",
        "description": "This is a test job to verify creation and visibility",
        "requirements": "Testing requirements here",
        "responsibilities": "Testing responsibilities here",
        "job_type": "full_time",
        "category": "Technology",
        "location_city": "Lahore",
        "salary_min": 50000,
        "salary_max": 75000,
        "contact_email": "test@company.com"
    }
    
    print(f"\n4️⃣ Creating new job: '{test_job['title']}'...")
    job_response = requests.post(f"{API_BASE_URL}/jobs/", json=test_job, headers=emp_headers)
    
    if job_response.status_code == 200:
        job_data = job_response.json()
        job_id = job_data.get("job_id")
        print(f"   ✅ Job created successfully!")
        print(f"   Job ID: {job_id}")
        print(f"   Status: {job_data.get('status', 'Unknown')}")
    else:
        print(f"   ❌ Job creation failed: {job_response.status_code}")
        print(f"   Response: {job_response.text}")
        return
    
    # Immediately check if job appears
    print(f"\n5️⃣ Checking if job {job_id} appears in my-jobs...")
    updated_jobs = requests.get(f"{API_BASE_URL}/jobs/my-jobs", headers=emp_headers)
    if updated_jobs.status_code == 200:
        jobs = updated_jobs.json()
        print(f"   Total jobs now: {len(jobs)}")
        
        # Look for our job
        found_job = None
        for job in jobs:
            if job.get("job_id") == job_id:
                found_job = job
                break
        
        if found_job:
            print("   ✅ SUCCESS: New job is visible in my-jobs!")
            print(f"     Title: {found_job.get('title')}")
            print(f"     Status: {found_job.get('status')}")
        else:
            print("   ❌ PROBLEM: New job NOT found in my-jobs")
            print("   Available job IDs:")
            for job in jobs[-5:]:  # Show last 5 jobs
                print(f"     - {job.get('job_id')} - {job.get('title', 'No title')}")
    else:
        print(f"   ❌ Updated jobs list failed: {updated_jobs.status_code}")
    
    # Check updated stats
    print("\n6️⃣ Checking updated stats...")
    final_stats = requests.get(f"{API_BASE_URL}/jobs/my-stats", headers=emp_headers)
    if final_stats.status_code == 200:
        stats = final_stats.json()
        print(f"   Final total jobs: {stats.get('total_jobs', 0)}")
        print(f"   Final draft jobs: {stats.get('draft_jobs', 0)}")
    else:
        print(f"   ❌ Final stats failed: {final_stats.status_code}")
    
    print("\n🏁 Test completed!")

if __name__ == "__main__":
    test_job_creation_flow()