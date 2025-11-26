"""
Promote admin and then test complete workflow
"""
import requests

API_BASE_URL = "https://punjab-rozgar-api.onrender.com/api/v1"

def promote_and_test():
    """Promote admin user and test workflow"""
    
    print("🔧 Promoting Admin and Testing Workflow\n")
    
    # Step 1: Promote admin
    print("1️⃣ Promoting admin user...")
    
    # Login as the user first 
    admin_login = requests.post(f"{API_BASE_URL}/auth/login", json={
        "email": "admin@test.com",
        "password": "admin123"
    })
    
    if admin_login.status_code != 200:
        print("❌ Initial admin login failed")
        return False
    
    token = admin_login.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Call promotion endpoint with query parameter
    promote_response = requests.post(f"{API_BASE_URL}/admin/initial-admin-setup?email=admin@test.com", headers=headers)
    
    print(f"Promotion result: {promote_response.status_code}")
    if promote_response.status_code == 200:
        result = promote_response.json()
        print(f"✅ Admin promoted: {result}")
    else:
        print(f"❌ Promotion failed: {promote_response.text}")
        return False
    
    # Step 2: Create and publish jobs
    print(f"\n2️⃣ Creating jobs as employer...")
    
    emp_login = requests.post(f"{API_BASE_URL}/auth/login", json={
        "email": "employer@test.com", 
        "password": "employer123"
    })
    
    if emp_login.status_code == 200:
        emp_token = emp_login.json().get("access_token")
        emp_headers = {"Authorization": f"Bearer {emp_token}"}
        
        # Create a job
        job_data = {
            "title": "Full Stack Developer",
            "description": "Full stack development with modern technologies",
            "requirements": "React, Node.js, Python, 3+ years experience",
            "responsibilities": "Develop web applications end-to-end",
            "job_type": "full_time",
            "category": "Technology",
            "location_city": "Islamabad",
            "salary_min": 60000,
            "salary_max": 90000,
            "contact_email": "hr@techcompany.com"
        }
        
        job_response = requests.post(f"{API_BASE_URL}/jobs/", json=job_data, headers=emp_headers)
        if job_response.status_code == 200:
            job_result = job_response.json()
            job_id = job_result.get("job_id")
            print(f"✅ Created job: {job_id}")
            
            # Publish it
            publish_response = requests.put(f"{API_BASE_URL}/jobs/{job_id}/publish", headers=emp_headers)
            if publish_response.status_code == 200:
                print(f"✅ Published job to pending approval")
            else:
                print(f"❌ Publish failed: {publish_response.status_code}")
        else:
            print(f"❌ Job creation failed: {job_response.status_code}")
    
    # Step 3: Approve as admin 
    print(f"\n3️⃣ Admin approval...")
    
    # Login as admin again to get fresh token with admin role
    admin_login2 = requests.post(f"{API_BASE_URL}/auth/login", json={
        "email": "admin@test.com",
        "password": "admin123"
    })
    
    if admin_login2.status_code == 200:
        admin_token = admin_login2.json().get("access_token")
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        admin_user = admin_login2.json().get("user", {})
        
        print(f"Admin role: {admin_user.get('role')}")
        
        # Get pending jobs
        pending_response = requests.get(f"{API_BASE_URL}/admin/jobs/pending-approval", headers=admin_headers)
        print(f"Pending jobs: {pending_response.status_code}")
        
        if pending_response.status_code == 200:
            pending_data = pending_response.json()
            pending_jobs = pending_data.get("jobs", [])
            print(f"Found {len(pending_jobs)} pending jobs")
            
            # Approve first job
            if pending_jobs:
                first_job = pending_jobs[0]
                job_id = first_job.get("job_id")
                
                approve_response = requests.post(f"{API_BASE_URL}/admin/jobs/{job_id}/approve", headers=admin_headers)
                print(f"Approval: {approve_response.status_code}")
                
                if approve_response.status_code == 200:
                    result = approve_response.json()
                    print(f"✅ Job approved! Status: {result.get('status')}")
                    
                    return True  # Success!
                else:
                    print(f"❌ Approval failed: {approve_response.text}")
        else:
            print(f"❌ Pending jobs failed: {pending_response.text}")
    
    return False

def test_final_recommendations():
    """Test job browsing and recommendations"""
    
    print(f"\n4️⃣ Testing Job Browsing and Recommendations\n")
    
    # Login as job seeker
    seeker_login = requests.post(f"{API_BASE_URL}/auth/login", json={
        "email": "seeker@test.com",
        "password": "seeker123"
    })
    
    if seeker_login.status_code == 200:
        seeker_token = seeker_login.json().get("access_token")
        seeker_headers = {"Authorization": f"Bearer {seeker_token}"}
        
        # Test job browsing
        browse_response = requests.get(f"{API_BASE_URL}/jobs/", headers=seeker_headers)
        print(f"Job browsing: {browse_response.status_code}")
        
        if browse_response.status_code == 200:
            jobs = browse_response.json()
            print(f"✅ Can browse {len(jobs)} active jobs")
            
            for job in jobs[:2]:  # Show first 2
                print(f"  • {job.get('title')} in {job.get('location_city')} (Status: {job.get('status')})")
        
        # Test recommendations
        print(f"\\nTesting recommendations...")
        rec_response = requests.get(f"{API_BASE_URL}/recommendations", headers=seeker_headers)
        print(f"Recommendations: {rec_response.status_code}")
        
        if rec_response.status_code == 200:
            recommendations = rec_response.json()
            print(f"✅ Got {len(recommendations)} recommendations!")
            
            if recommendations:
                first_rec = recommendations[0]
                print(f"  Example: {first_rec.get('title')} (Match: {first_rec.get('match_score')}%)")
        elif rec_response.status_code == 404:
            print("⚠️ Recommendations endpoint not yet deployed")
        else:
            print(f"❌ Recommendations error: {rec_response.text[:100]}")

if __name__ == "__main__":
    if promote_and_test():
        print(f"\n🎉 Workflow completed successfully!")
        test_final_recommendations()
    else:
        print(f"\n💥 Workflow failed")