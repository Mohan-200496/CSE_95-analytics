"""
Try to manually promote existing user to admin and test workflow
"""
import requests

API_BASE_URL = "https://punjab-rozgar-api.onrender.com/api/v1"

def test_admin_promotion_and_workflow():
    """Test manual admin promotion and job workflow"""
    
    print("🔧 Testing Admin Promotion and Job Workflow\n")
    
    # Step 1: First check what the current admin user situation is
    print("1️⃣ Checking existing admin situation...")
    
    existing_admin_login = requests.post(f"{API_BASE_URL}/auth/login", json={
        "email": "admin@test.com",
        "password": "admin123"
    })
    
    if existing_admin_login.status_code == 200:
        user_info = existing_admin_login.json().get("user", {})
        print(f"   Current admin@test.com role: {user_info.get('role')}")
        print(f"   User ID: {user_info.get('user_id')}")
        
        if user_info.get('role') == 'admin':
            print("   ✅ Already has admin role!")
            admin_token = existing_admin_login.json().get("access_token")
            admin_headers = {"Authorization": f"Bearer {admin_token}"}
            
            # Test admin functionality
            print(f"\n2️⃣ Testing admin functionality...")
            
            stats_response = requests.get(f"{API_BASE_URL}/admin/stats", headers=admin_headers)
            print(f"   Admin stats: {stats_response.status_code}")
            
            if stats_response.status_code == 200:
                stats = stats_response.json()
                print(f"     Total jobs: {stats.get('total_jobs', 0)}")
                print(f"     Active jobs: {stats.get('active_jobs', 0)}")
            
            # Check pending jobs
            pending_response = requests.get(f"{API_BASE_URL}/admin/jobs/pending-approval", headers=admin_headers)
            print(f"   Pending jobs: {pending_response.status_code}")
            
            if pending_response.status_code == 200:
                pending_jobs = pending_response.json()
                print(f"     Found {len(pending_jobs)} pending jobs")
                
                # Try to approve one job
                if len(pending_jobs) > 0:
                    test_job = pending_jobs[0]
                    job_id = test_job.get('job_id')
                    print(f"     Trying to approve: {test_job.get('title')}")
                    
                    approve_response = requests.post(f"{API_BASE_URL}/admin/jobs/{job_id}/approve", headers=admin_headers)
                    print(f"     Approval result: {approve_response.status_code}")
                    
                    if approve_response.status_code == 200:
                        result = approve_response.json()
                        print(f"       ✅ Job approved! New status: {result.get('status')}")
                        return True
                    else:
                        print(f"       ❌ Approval failed: {approve_response.text}")
                else:
                    print(f"     ℹ️ No pending jobs to approve")
            else:
                print(f"     ❌ Pending jobs error: {pending_response.text}")
        else:
            print(f"   ⚠️ admin@test.com has role '{user_info.get('role')}', not admin")
            
            # Try to use the existing user to call initial admin setup
            token = existing_admin_login.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            setup_response = requests.post(f"{API_BASE_URL}/admin/initial-admin-setup?email=admin@test.com", headers=headers)
            print(f"   Admin setup attempt: {setup_response.status_code}")
            
            if setup_response.status_code == 200:
                print(f"     ✅ Admin promotion successful!")
                return test_admin_promotion_and_workflow()  # Retry with admin role
            else:
                print(f"     ❌ Admin setup failed: {setup_response.text}")
    else:
        print(f"   ❌ admin@test.com login failed: {existing_admin_login.status_code}")
    
    return False

def quick_job_status_summary():
    """Quick summary of job statuses"""
    print(f"\n📊 Quick Job Status Summary")
    
    # Browse all jobs without auth
    browse_response = requests.get(f"{API_BASE_URL}/jobs/?only_active=false&limit=100")
    if browse_response.status_code == 200:
        jobs = browse_response.json()
        statuses = {}
        for job in jobs:
            status = job.get('status', 'unknown')
            statuses[status] = statuses.get(status, 0) + 1
        
        print(f"   Total jobs: {len(jobs)}")
        for status, count in statuses.items():
            print(f"   {status}: {count}")
    else:
        print(f"   ❌ Failed to get job summary: {browse_response.status_code}")

if __name__ == "__main__":
    quick_job_status_summary()
    
    if test_admin_promotion_and_workflow():
        print(f"\n🎉 Admin workflow is working!")
        quick_job_status_summary()  # Show updated status
    else:
        print(f"\n💥 Admin workflow failed")