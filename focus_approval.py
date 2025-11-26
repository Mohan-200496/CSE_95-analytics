"""
Focus on job approval only, skip admin stats
"""
import requests

API_BASE_URL = "https://punjab-rozgar-api.onrender.com/api/v1"

def focus_on_job_approval():
    """Focus only on job approval workflow"""
    
    print("🎯 Focused Job Approval Test\n")
    
    # Login as admin
    admin_login = requests.post(f"{API_BASE_URL}/auth/login", json={
        "email": "admin@test.com",
        "password": "admin123"
    })
    
    if admin_login.status_code != 200:
        print("❌ Admin login failed")
        return False
    
    admin_token = admin_login.json().get("access_token")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    user_info = admin_login.json().get("user", {})
    
    print(f"✅ Admin logged in: {user_info.get('role')}")
    
    # Get pending jobs
    print("📋 Checking pending jobs...")
    pending_response = requests.get(f"{API_BASE_URL}/admin/jobs/pending-approval", headers=admin_headers)
    
    print(f"Pending jobs endpoint: {pending_response.status_code}")
    
    if pending_response.status_code == 200:
        pending_data = pending_response.json()
        pending_jobs = pending_data.get("jobs", [])
        total_count = pending_data.get("total_count", 0)
        
        print(f"✅ Found {len(pending_jobs)} pending jobs (total: {total_count})")
        
        # Show pending jobs
        for i, job in enumerate(pending_jobs):
            print(f"  {i+1}. {job.get('title')} (ID: {job.get('job_id')}, Status: {job.get('status')})")
        
        # Approve all pending jobs
        if pending_jobs:
            print(f"\\n🚀 Approving jobs...")
            for job in pending_jobs:
                job_id = job.get("job_id") 
                job_title = job.get("title")
                
                approve_response = requests.post(f"{API_BASE_URL}/admin/jobs/{job_id}/approve", headers=admin_headers)
                print(f"  Approving {job_title}: {approve_response.status_code}")
                
                if approve_response.status_code == 200:
                    result = approve_response.json()
                    print(f"    ✅ Success! New status: {result.get('status')}")
                else:
                    print(f"    ❌ Error: {approve_response.text}")
            
            return True
        else:
            print("ℹ️ No pending jobs to approve")
            return True
    else:
        print(f"❌ Failed: {pending_response.text}")
        return False

def test_job_browsing_after_approval():
    """Test job browsing after approval"""
    
    print(f"\\n📋 Testing Job Browsing After Approval\\n")
    
    # Test as job seeker
    seeker_login = requests.post(f"{API_BASE_URL}/auth/login", json={
        "email": "seeker@test.com",
        "password": "seeker123"
    })
    
    if seeker_login.status_code != 200:
        print("❌ Job seeker login failed")
        return
    
    seeker_token = seeker_login.json().get("access_token")
    seeker_headers = {"Authorization": f"Bearer {seeker_token}"}
    
    # Browse active jobs
    browse_response = requests.get(f"{API_BASE_URL}/jobs/", headers=seeker_headers)
    
    print(f"Job browsing: {browse_response.status_code}")
    
    if browse_response.status_code == 200:
        jobs = browse_response.json()
        print(f"✅ Job seeker can see {len(jobs)} active jobs:")
        
        for job in jobs:
            print(f"  • {job.get('title')} in {job.get('location_city')}")
            print(f"    Status: {job.get('status')}, Salary: ${job.get('salary_min', 0):,} - ${job.get('salary_max', 0):,}")
    else:
        print(f"❌ Error: {browse_response.text}")

if __name__ == "__main__":
    if focus_on_job_approval():
        print(f"\\n🎉 Job approval successful!")
        test_job_browsing_after_approval()
    else:
        print(f"\\n💥 Job approval failed")