"""
Test job recommendations with role-based access
"""
import requests
import json

API_BASE_URL = "https://punjab-rozgar-api.onrender.com/api/v1"

def test_job_recommendations_focused():
    """Test job recommendations after ensuring we have active jobs"""
    
    print("🎯 Testing Job Recommendations (Focused)\n")
    
    # Step 1: Create and publish a job as employer
    print("1️⃣ Setting up test job...")
    
    emp_login = requests.post(f"{API_BASE_URL}/auth/login", json={
        "email": "employer@test.com",
        "password": "employer123"
    })
    
    if emp_login.status_code != 200:
        print("❌ Employer login failed")
        return
    
    emp_token = emp_login.json().get("access_token")
    emp_headers = {"Authorization": f"Bearer {emp_token}"}
    
    # Create a job
    job_data = {
        "title": "Python Developer Recommendations Test",
        "description": "Backend development with Django and FastAPI",
        "requirements": "Python, Django, FastAPI, 3+ years experience",
        "responsibilities": "Develop APIs and backend services",
        "job_type": "full_time",
        "category": "Technology",
        "location_city": "Karachi",
        "salary_min": 60000,
        "salary_max": 85000,
        "contact_email": "tech@company.com"
    }
    
    job_response = requests.post(f"{API_BASE_URL}/jobs/", json=job_data, headers=emp_headers)
    if job_response.status_code == 200:
        job_result = job_response.json()
        job_id = job_result.get("job_id")
        print(f"   ✅ Job created: {job_id} (Status: {job_result.get('status')})")
        
        # Publish the job
        publish_response = requests.put(f"{API_BASE_URL}/jobs/{job_id}/publish", headers=emp_headers)
        if publish_response.status_code == 200:
            print(f"   ✅ Job published to pending_approval")
        else:
            print(f"   ❌ Publish failed: {publish_response.status_code}")
    
    # Step 2: Manually approve job by updating status (simulate admin approval)
    # For testing, let's check if we can find any active jobs first
    
    print(f"\n2️⃣ Checking available active jobs...")
    
    # Try to browse jobs without auth first
    browse_response = requests.get(f"{API_BASE_URL}/jobs/?only_active=false&limit=50")
    if browse_response.status_code == 200:
        all_jobs = browse_response.json()
        print(f"   📊 Total jobs in system: {len(all_jobs)}")
        
        # Show job statuses
        statuses = {}
        for job in all_jobs:
            status = job.get('status', 'unknown')
            statuses[status] = statuses.get(status, 0) + 1
        
        print(f"   Job status breakdown: {statuses}")
    
    # Step 3: Test recommendations for different user types
    print(f"\n3️⃣ Testing recommendations for different users...")
    
    test_users = [
        ("admin@test.com", "admin123", "Admin"),
        ("employer@test.com", "employer123", "Employer"),
        ("seeker@test.com", "seeker123", "Job Seeker")
    ]
    
    for email, password, name in test_users:
        print(f"\n   Testing {name}:")
        
        login_response = requests.post(f"{API_BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        })
        
        if login_response.status_code != 200:
            print(f"     ❌ Login failed")
            continue
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        user_info = login_response.json().get("user", {})
        role = user_info.get("role")
        
        print(f"     Role: {role}")
        
        # Test job recommendations
        rec_response = requests.get(f"{API_BASE_URL}/recommendations", headers=headers)
        
        print(f"     Recommendations: {rec_response.status_code}")
        
        if rec_response.status_code == 200:
            recommendations = rec_response.json()
            print(f"     ✅ Got {len(recommendations)} recommendations")
            
            # Show first recommendation
            if recommendations:
                first_rec = recommendations[0]
                print(f"       Example: {first_rec.get('title')} in {first_rec.get('location_city')}")
                print(f"       Match Score: {first_rec.get('match_score', 'N/A')}")
                
        elif rec_response.status_code == 403:
            print(f"     🚫 Access forbidden (expected for {role})")
            
        else:
            print(f"     ❌ Recommendations failed: {rec_response.status_code}")
            print(f"       Error: {rec_response.text}")
        
        # Test regular job browsing
        browse_response = requests.get(f"{API_BASE_URL}/jobs/", headers=headers)
        if browse_response.status_code == 200:
            jobs = browse_response.json()
            print(f"     📋 Can browse {len(jobs)} jobs")
        else:
            print(f"     ❌ Browse failed: {browse_response.status_code}")

if __name__ == "__main__":
    test_job_recommendations_focused()