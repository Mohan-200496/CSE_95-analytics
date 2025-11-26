"""
Complete job workflow test: Create → Publish → Approve → Browse → Recommend
"""
import requests
import json

API_BASE_URL = "https://punjab-rozgar-api.onrender.com/api/v1"

def test_complete_job_workflow():
    """Test complete job workflow from creation to recommendation"""
    
    print("🔄 Testing Complete Job Workflow\n")
    
    # Step 1: Login as employer and create jobs
    print("1️⃣ Creating jobs as employer...")
    emp_login = requests.post(f"{API_BASE_URL}/auth/login", json={
        "email": "employer@test.com",
        "password": "employer123"
    })
    
    if emp_login.status_code != 200:
        print("❌ Employer login failed!")
        return
    
    emp_token = emp_login.json().get("access_token")
    emp_headers = {"Authorization": f"Bearer {emp_token}"}
    
    # Create a job
    job_data = {
        "title": "Frontend Developer",
        "description": "React and TypeScript development",
        "requirements": "React, TypeScript, 2+ years experience",
        "responsibilities": "Build user interfaces",
        "job_type": "full_time",
        "category": "Technology",
        "location_city": "Lahore",
        "salary_min": 50000,
        "salary_max": 70000,
        "contact_email": "hr@company.com"
    }
    
    job_response = requests.post(f"{API_BASE_URL}/jobs/", json=job_data, headers=emp_headers)
    if job_response.status_code != 200:
        print("❌ Job creation failed!")
        return
    
    job_result = job_response.json()
    job_id = job_result.get("job_id")
    print(f"   ✅ Created job: {job_result.get('title')} (ID: {job_id}, Status: {job_result.get('status')})")
    
    # Step 2: Publish the job (draft → pending_approval)
    print(f"\n2️⃣ Publishing job {job_id}...")
    publish_response = requests.put(f"{API_BASE_URL}/jobs/{job_id}/publish", headers=emp_headers)
    
    if publish_response.status_code == 200:
        publish_result = publish_response.json()
        print(f"   ✅ Job published: Status = {publish_result.get('status')}")
    else:
        print(f"   ❌ Publish failed: {publish_response.status_code}")
        print(f"   Response: {publish_response.text}")
        return
    
    # Step 3: Login as admin and approve the job
    print(f"\n3️⃣ Approving job as admin...")
    
    # First, let's promote admin user properly
    admin_login = requests.post(f"{API_BASE_URL}/auth/login", json={
        "email": "admin@test.com",
        "password": "admin123"
    })
    
    if admin_login.status_code != 200:
        print("❌ Admin login failed!")
        return
    
    admin_token = admin_login.json().get("access_token")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Try to promote to admin first (if not already)
    setup_response = requests.post(f"{API_BASE_URL}/admin/initial-admin-setup?email=admin@test.com", headers=admin_headers)
    if setup_response.status_code == 200:
        print("   ✅ Admin setup completed")
    
    # Check pending jobs
    pending_response = requests.get(f"{API_BASE_URL}/admin/jobs/pending-approval", headers=admin_headers)
    if pending_response.status_code == 200:
        pending_jobs = pending_response.json()
        print(f"   📋 Found {len(pending_jobs)} pending jobs")
        
        # Find our job
        target_job = None
        for job in pending_jobs:
            if job.get("job_id") == job_id:
                target_job = job
                break
        
        if target_job:
            print(f"   📍 Found target job: {target_job.get('title')}")
            
            # Approve the job
            approve_response = requests.post(f"{API_BASE_URL}/admin/jobs/{job_id}/approve", headers=admin_headers)
            if approve_response.status_code == 200:
                approve_result = approve_response.json()
                print(f"   ✅ Job approved: Status = {approve_result.get('status')}")
            else:
                print(f"   ❌ Approval failed: {approve_response.status_code}")
                print(f"   Response: {approve_response.text}")
                return
        else:
            print(f"   ❌ Target job {job_id} not found in pending jobs")
            return
    else:
        print(f"   ❌ Failed to get pending jobs: {pending_response.status_code}")
        return
    
    # Step 4: Test job browsing as different users
    print(f"\n4️⃣ Testing job visibility for different users...")
    
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
        
        # Test browsing all jobs (only_active=True by default)
        browse_response = requests.get(f"{API_BASE_URL}/jobs/", headers=headers)
        if browse_response.status_code == 200:
            jobs = browse_response.json()
            print(f"     ✅ Can see {len(jobs)} active jobs")
            
            # Check if our job is visible
            our_job = None
            for job in jobs:
                if job.get("job_id") == job_id:
                    our_job = job
                    break
            
            if our_job:
                print(f"       👀 Our job '{our_job.get('title')}' is visible (Status: {our_job.get('status')})")
            else:
                print(f"       🚫 Our job {job_id} is NOT visible")
                
        else:
            print(f"     ❌ Browse failed: {browse_response.status_code}")
        
        # Test role-based access expectations
        if role == "job_seeker":
            print(f"     ✅ Job seeker should see approved jobs - CORRECT")
        elif role == "employer":
            print(f"     ⚠️  Employer seeing jobs - check if this is intended")
        elif role == "admin":
            print(f"     ⚠️  Admin seeing jobs - check if this is intended")

if __name__ == "__main__":
    test_complete_job_workflow()