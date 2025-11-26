"""
Test job recommendation functionality for different user roles
"""
import requests
import json

API_BASE_URL = "https://punjab-rozgar-api.onrender.com/api/v1"

def test_job_recommendations():
    """Test job recommendations for different user roles"""
    
    print("🎯 Testing Job Recommendation Functionality\n")
    
    # First, let's create some test jobs as employer
    print("1️⃣ Setting up test jobs as employer...")
    emp_login = requests.post(f"{API_BASE_URL}/auth/login", json={
        "email": "employer@test.com",
        "password": "employer123"
    })
    
    if emp_login.status_code != 200:
        print("❌ Employer login failed!")
        return
    
    emp_token = emp_login.json().get("access_token")
    emp_headers = {"Authorization": f"Bearer {emp_token}"}
    
    # Create a few different types of jobs
    test_jobs = [
        {
            "title": "Software Engineer",
            "description": "Python development position",
            "requirements": "Python, Django, REST APIs",
            "responsibilities": "Develop web applications",
            "job_type": "full_time",
            "category": "Technology",
            "location_city": "Lahore",
            "salary_min": 60000,
            "salary_max": 80000,
            "contact_email": "hr@company.com"
        },
        {
            "title": "Data Analyst",
            "description": "Data analysis and reporting",
            "requirements": "SQL, Excel, Python",
            "responsibilities": "Analyze business data",
            "job_type": "full_time", 
            "category": "Technology",
            "location_city": "Karachi",
            "salary_min": 45000,
            "salary_max": 60000,
            "contact_email": "hr@company.com"
        }
    ]
    
    created_jobs = []
    for job_data in test_jobs:
        job_response = requests.post(f"{API_BASE_URL}/jobs/", json=job_data, headers=emp_headers)
        if job_response.status_code == 200:
            job_result = job_response.json()
            created_jobs.append(job_result)
            print(f"   ✅ Created job: {job_result.get('title')} (ID: {job_result.get('job_id')})")
        else:
            print(f"   ❌ Failed to create job: {job_data['title']}")
    
    # Now test job recommendations for different roles
    print(f"\n2️⃣ Testing job recommendations for different roles...")
    
    # Test users
    test_users = [
        {
            "email": "admin@test.com",
            "password": "admin123", 
            "role": "admin",
            "name": "Admin"
        },
        {
            "email": "employer@test.com",
            "password": "employer123",
            "role": "employer", 
            "name": "Employer"
        },
        {
            "email": "seeker@test.com",
            "password": "seeker123",
            "role": "job_seeker",
            "name": "Job Seeker"
        }
    ]
    
    for user in test_users:
        print(f"\n   Testing {user['name']} ({user['role']}):")
        
        # Login as this user
        login_response = requests.post(f"{API_BASE_URL}/auth/login", json={
            "email": user["email"],
            "password": user["password"]
        })
        
        if login_response.status_code != 200:
            print(f"     ❌ Login failed for {user['name']}")
            continue
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to get job recommendations
        rec_response = requests.get(f"{API_BASE_URL}/jobs/recommendations", headers=headers)
        
        if rec_response.status_code == 200:
            recommendations = rec_response.json()
            print(f"     ✅ Got {len(recommendations)} recommendations")
            
            # Check if recommendations are appropriate for this role
            if user['role'] == 'admin':
                print(f"     ⚠️  Admin should NOT get job recommendations (business rule)")
            elif user['role'] == 'employer':
                print(f"     ⚠️  Employer should NOT get job recommendations (business rule)")
            elif user['role'] == 'job_seeker':
                print(f"     ✅ Job seeker should get recommendations (correct)")
                
            # Show some recommendation details
            for i, job in enumerate(recommendations[:2]):  # Show first 2
                print(f"       Job {i+1}: {job.get('title')} in {job.get('location_city')}")
                
        else:
            print(f"     ❌ Recommendations failed: {rec_response.status_code}")
            if rec_response.status_code == 403:
                print(f"     ℹ️  Forbidden - might be correct for {user['role']}")
    
    # Test browsing all jobs (should work for job seekers, restricted for others)
    print(f"\n3️⃣ Testing job browsing for different roles...")
    
    for user in test_users:
        print(f"\n   Testing job browsing for {user['name']} ({user['role']}):")
        
        login_response = requests.post(f"{API_BASE_URL}/auth/login", json={
            "email": user["email"], 
            "password": user["password"]
        })
        
        if login_response.status_code != 200:
            continue
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to browse all jobs
        browse_response = requests.get(f"{API_BASE_URL}/jobs/", headers=headers)
        
        if browse_response.status_code == 200:
            jobs = browse_response.json()
            print(f"     ✅ Can browse {len(jobs)} jobs")
            
            # Check job statuses visible to this role
            statuses = [job.get('status') for job in jobs]
            unique_statuses = list(set(statuses))
            print(f"     Job statuses visible: {unique_statuses}")
            
        else:
            print(f"     ❌ Browse failed: {browse_response.status_code}")

if __name__ == "__main__":
    test_job_recommendations()