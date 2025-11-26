"""
Direct database job activation for testing (temporary solution)
"""
import requests
import json

API_BASE_URL = "https://punjab-rozgar-api.onrender.com/api/v1"

def activate_pending_jobs_for_testing():
    """Try to approve pending jobs through admin endpoints"""
    
    print("🛠️  Activating Pending Jobs for Testing\n")
    
    # Method 1: Try to use employer to publish + direct approval
    # Login as employer first to see jobs
    
    print("1️⃣ Employer job management...")
    emp_login = requests.post(f"{API_BASE_URL}/auth/login", json={
        "email": "employer@test.com",
        "password": "employer123"
    })
    
    if emp_login.status_code == 200:
        emp_token = emp_login.json().get("access_token")
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        
        # Get employer's jobs
        my_jobs_response = requests.get(f"{API_BASE_URL}/jobs/my-jobs", headers=emp_headers)
        if my_jobs_response.status_code == 200:
            my_jobs = my_jobs_response.json()
            print(f"   Employer has {len(my_jobs)} jobs")
            
            for job in my_jobs:
                print(f"     Job: {job.get('title')} - Status: {job.get('status')}")
                
                # If job is draft, publish it
                if job.get('status') == 'draft':
                    job_id = job.get('job_id')
                    publish_response = requests.put(f"{API_BASE_URL}/jobs/{job_id}/publish", headers=emp_headers)
                    if publish_response.status_code == 200:
                        print(f"       ✅ Published job {job_id}")
                    else:
                        print(f"       ❌ Failed to publish {job_id}: {publish_response.status_code}")
    
    # Method 2: Create a simple job activation endpoint for testing
    # For now, let's try the admin route again with a different approach
    
    print(f"\n2️⃣ Testing admin login variations...")
    
    # Try the existing admin users
    admin_emails = ["admin@test.com", "newadmin@test.com"]
    
    for admin_email in admin_emails:
        admin_login = requests.post(f"{API_BASE_URL}/auth/login", json={
            "email": admin_email,
            "password": "admin123"
        })
        
        if admin_login.status_code == 200:
            admin_data = admin_login.json()
            user_info = admin_data.get("user", {})
            print(f"   Trying admin: {admin_email}")
            print(f"     Role: {user_info.get('role')}")
            print(f"     User ID: {user_info.get('user_id')}")
            
            # If this user has admin role, try to approve jobs
            if user_info.get('role') == 'admin':
                admin_token = admin_data.get("access_token")
                admin_headers = {"Authorization": f"Bearer {admin_token}"}
                
                print(f"   🔑 Found admin access with {admin_email}")
                
                # Try simple admin endpoint first
                stats_response = requests.get(f"{API_BASE_URL}/admin/stats", headers=admin_headers)
                print(f"     Admin stats endpoint: {stats_response.status_code}")
                
                # Now try pending jobs
                pending_response = requests.get(f"{API_BASE_URL}/admin/jobs/pending-approval", headers=admin_headers)
                print(f"     Pending jobs endpoint: {pending_response.status_code}")
                
                if pending_response.status_code == 200:
                    pending_jobs = pending_response.json()
                    print(f"     📋 Found {len(pending_jobs)} pending jobs")
                    
                    # Approve each pending job
                    for job in pending_jobs:
                        job_id = job.get('job_id')
                        approve_response = requests.post(f"{API_BASE_URL}/admin/jobs/{job_id}/approve", headers=admin_headers)
                        
                        if approve_response.status_code == 200:
                            print(f"       ✅ Approved job: {job.get('title')}")
                        else:
                            print(f"       ❌ Failed to approve {job_id}: {approve_response.status_code}")
                            print(f"         Error: {approve_response.text}")
                    
                    return True  # Success
                else:
                    print(f"     ❌ Pending jobs failed: {pending_response.text}")
            
            break  # Found working admin
    
    return False

if __name__ == "__main__":
    if activate_pending_jobs_for_testing():
        print("\n🎉 Jobs activated successfully!")
    else:
        print("\n💥 Failed to activate jobs")