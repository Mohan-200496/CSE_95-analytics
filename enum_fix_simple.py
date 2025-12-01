"""
Quick enum fix using backend server
"""

import requests
import json

print("🔧 Fixing Database Enum Issues")
print("=" * 50)

API_BASE_URL = "https://punjab-rozgar-api.onrender.com/api/v1"

# Test job creation with proper enum handling
def test_job_creation():
    """Test creating a job with the test endpoint"""
    
    test_job = {
        "title": "Database Enum Test Job",
        "description": "Testing job creation after enum fixes",
        "job_type": "full-time",  # This might need conversion
        "category": "Technology", 
        "location_city": "Lahore",
        "location_state": "Punjab",
        "remote_allowed": False,
        "salary_min": 50000,
        "salary_max": 70000
    }
    
    print("1. Testing job creation with test endpoint...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/jobs/test-create",
            json=test_job,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            print(f"   ✅ Success: Job created with ID {result.get('job_id')}")
            return result.get('job_id')
        else:
            print(f"   ❌ Error: {result}")
            print(f"   Full response: {response.text}")
            
            # Try with different job_type format
            print("\n2. Trying with underscored job_type...")
            test_job['job_type'] = 'full_time'
            response2 = requests.post(
                f"{API_BASE_URL}/jobs/test-create",
                json=test_job,
                timeout=10
            )
            result2 = response2.json()
            print(f"   Status: {response2.status_code}")
            
            if response2.status_code == 200 and result2.get('success'):
                print(f"   ✅ Success: Job created with ID {result2.get('job_id')}")
                return result2.get('job_id')
            else:
                print(f"   ❌ Still failing: {result2}")
                
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    return None

# Create demo jobs
def create_demo_jobs():
    """Try to create demo jobs"""
    
    print("\n3. Creating demo jobs...")
    try:
        response = requests.get(f"{API_BASE_URL}/auth/create-demo-jobs", timeout=10)
        print(f"   Status: {response.status_code}")
        result = response.json()
        
        if 'error' in result:
            print(f"   ❌ Demo jobs failed: {result['error'][:200]}...")
        else:
            print(f"   ✅ Demo jobs: {result}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")

# Check jobs after creation
def check_jobs_after_creation():
    """Check if jobs exist after creation attempts"""
    
    print("\n4. Checking jobs after creation attempts...")
    try:
        response = requests.get(f"{API_BASE_URL}/jobs/", timeout=10)
        
        if response.status_code == 200:
            jobs = response.json()
            print(f"   ✅ Total jobs found: {len(jobs)}")
            
            if jobs:
                print("   Recent jobs:")
                for i, job in enumerate(jobs[-3:], 1):
                    print(f"   {i}. {job.get('title', 'No title')} (Status: {job.get('status', 'unknown')})")
            else:
                print("   No jobs in database")
                
        else:
            print(f"   ❌ Error checking jobs: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    job_id = test_job_creation()
    create_demo_jobs() 
    check_jobs_after_creation()
    
    print(f"\n{'='*50}")
    print("🎯 Next Steps:")
    print("1. If jobs were created successfully, refresh your browser")
    print("2. Check the employer dashboard at /pages/employer/jobs.html")
    print("3. If still no jobs appear, there may be a frontend filtering issue")
    print("4. The 403 error you saw is from recommendations, not job listing")