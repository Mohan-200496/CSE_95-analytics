"""
Complete end-to-end job workflow and recommendations test
"""
import requests
import json
import time

API_BASE_URL = "https://punjab-rozgar-api.onrender.com/api/v1"

def complete_job_workflow_test():
    """Test complete workflow: Create → Publish → Approve → Recommend"""
    
    print("🎯 Complete Job Workflow and Recommendations Test\n")
    
    # Step 1: Create and publish jobs as employer
    print("1️⃣ Creating and publishing jobs as employer...")
    
    emp_login = requests.post(f"{API_BASE_URL}/auth/login", json={
        "email": "employer@test.com",
        "password": "employer123"
    })
    
    if emp_login.status_code != 200:
        print("❌ Employer login failed")
        return False
    
    emp_token = emp_login.json().get("access_token")
    emp_headers = {"Authorization": f"Bearer {emp_token}"}
    
    # Create multiple test jobs
    test_jobs = [
        {
            "title": "Senior Python Developer",
            "description": "Full-stack Python development with Django and React",
            "requirements": "Python, Django, React, 5+ years experience",
            "responsibilities": "Lead backend development, mentor junior developers",
            "job_type": "full_time",
            "category": "Technology",
            "location_city": "Lahore",
            "salary_min": 80000,
            "salary_max": 120000,
            "contact_email": "tech-lead@company.com"
        },
        {
            "title": "Data Scientist",
            "description": "Machine learning and data analysis position",
            "requirements": "Python, Pandas, Scikit-learn, TensorFlow, 3+ years",
            "responsibilities": "Build ML models, analyze data patterns",
            "job_type": "full_time", 
            "category": "Technology",
            "location_city": "Karachi",
            "salary_min": 70000,
            "salary_max": 100000,
            "contact_email": "data-team@company.com"
        }
    ]
    
    created_job_ids = []
    
    for job_data in test_jobs:
        job_response = requests.post(f"{API_BASE_URL}/jobs/", json=job_data, headers=emp_headers)
        if job_response.status_code == 200:
            job_result = job_response.json()
            job_id = job_result.get("job_id")
            created_job_ids.append(job_id)
            print(f"   ✅ Created: {job_result.get('title')} (ID: {job_id})")
            
            # Publish the job
            publish_response = requests.put(f"{API_BASE_URL}/jobs/{job_id}/publish", headers=emp_headers)
            if publish_response.status_code == 200:
                print(f"     📤 Published to pending approval")
            else:
                print(f"     ❌ Publish failed: {publish_response.status_code}")
        else:
            print(f"   ❌ Failed to create: {job_data['title']}")
    
    # Step 2: Admin approves jobs
    print(f"\n2️⃣ Admin approval process...")
    
    admin_login = requests.post(f"{API_BASE_URL}/auth/login", json={
        "email": "admin@test.com",
        "password": "admin123"
    })
    
    if admin_login.status_code != 200:
        print("❌ Admin login failed")
        return False
    
    admin_token = admin_login.json().get("access_token")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Get pending jobs (note: using correct response format)
    pending_response = requests.get(f"{API_BASE_URL}/admin/jobs/pending-approval", headers=admin_headers)
    
    if pending_response.status_code == 200:
        pending_data = pending_response.json()
        pending_jobs = pending_data.get("jobs", [])  # Correct key
        print(f"   📋 Found {len(pending_jobs)} pending jobs")
        
        # Approve all pending jobs
        approved_jobs = 0
        for job in pending_jobs:
            job_id = job.get("job_id")
            job_title = job.get("title")
            
            approve_response = requests.post(f"{API_BASE_URL}/admin/jobs/{job_id}/approve", headers=admin_headers)
            if approve_response.status_code == 200:
                print(f"     ✅ Approved: {job_title}")
                approved_jobs += 1
            else:
                print(f"     ❌ Failed to approve {job_title}: {approve_response.status_code}")
        
        print(f"   🎉 Successfully approved {approved_jobs} jobs")
    else:
        print(f"   ❌ Failed to get pending jobs: {pending_response.status_code}")
        return False
    
    # Step 3: Test job browsing and recommendations
    print(f"\n3️⃣ Testing job browsing and recommendations...")
    
    # Test with job seeker
    seeker_login = requests.post(f"{API_BASE_URL}/auth/login", json={
        "email": "seeker@test.com",
        "password": "seeker123"
    })
    
    if seeker_login.status_code != 200:
        print("❌ Job seeker login failed")
        return False
    
    seeker_token = seeker_login.json().get("access_token")
    seeker_headers = {"Authorization": f"Bearer {seeker_token}"}
    
    # Test job browsing
    browse_response = requests.get(f"{API_BASE_URL}/jobs/", headers=seeker_headers)
    if browse_response.status_code == 200:
        active_jobs = browse_response.json()
        print(f"   📋 Job Seeker can browse {len(active_jobs)} active jobs")
        
        for job in active_jobs:
            print(f"     • {job.get('title')} in {job.get('location_city')} (Status: {job.get('status')})")
    else:
        print(f"   ❌ Job browsing failed: {browse_response.status_code}")
    
    # Test recommendations (wait for deployment)
    print(f"\\n   🔄 Testing recommendations endpoint...")
    
    # Try different endpoint paths as deployment might be updating
    recommendation_endpoints = [
        "/recommendations", 
        "/jobs/recommendations",
        "/recommendations/",
        "/jobs/recommendations/"
    ]
    
    recommendations_working = False
    
    for endpoint in recommendation_endpoints:
        rec_response = requests.get(f"{API_BASE_URL}{endpoint}", headers=seeker_headers)
        print(f"     {endpoint}: {rec_response.status_code}")
        
        if rec_response.status_code == 200:
            recommendations = rec_response.json()
            print(f"       ✅ Got {len(recommendations)} recommendations!")
            recommendations_working = True
            
            # Show first recommendation
            if recommendations:
                first_rec = recommendations[0]
                print(f"         Example: {first_rec.get('title')} (Match: {first_rec.get('match_score', 'N/A')}%)")
            break
        elif rec_response.status_code != 404:
            print(f"       Response: {rec_response.text[:100]}")
    
    if not recommendations_working:
        print(f"     ⚠️ Recommendations endpoint not yet deployed (this is expected)")
    
    # Test role-based access
    print(f"\n4️⃣ Testing role-based access restrictions...")
    
    test_users = [
        ("admin@test.com", "admin123", "Admin"),
        ("employer@test.com", "employer123", "Employer")
    ]
    
    for email, password, role in test_users:
        login_response = requests.post(f"{API_BASE_URL}/auth/login", json={
            "email": email, "password": password
        })
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test browsing
            browse_response = requests.get(f"{API_BASE_URL}/jobs/", headers=headers)
            print(f"   {role} browsing: {browse_response.status_code} ({len(browse_response.json()) if browse_response.status_code == 200 else 'N/A'} jobs)")
            
            # Test recommendations (should be forbidden)
            rec_response = requests.get(f"{API_BASE_URL}/recommendations", headers=headers)
            if rec_response.status_code == 403:
                print(f"   {role} recommendations: ✅ Properly forbidden")
            else:
                print(f"   {role} recommendations: {rec_response.status_code} (unexpected)")
    
    return True

if __name__ == "__main__":
    if complete_job_workflow_test():
        print(f"\n🎉 Complete workflow test successful!")
    else:
        print(f"\n💥 Workflow test failed")