"""
Debug what the pending jobs response contains
"""
import requests
import json

API_BASE_URL = "https://punjab-rozgar-api.onrender.com/api/v1"

def debug_pending_jobs():
    """Debug the pending jobs response format"""
    
    print("🔍 Debugging Pending Jobs Response\n")
    
    # Login as admin
    admin_login = requests.post(f"{API_BASE_URL}/auth/login", json={
        "email": "admin@test.com",
        "password": "admin123"
    })
    
    if admin_login.status_code != 200:
        print("❌ Admin login failed")
        return
    
    admin_token = admin_login.json().get("access_token")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    user_info = admin_login.json().get("user", {})
    
    print(f"✅ Logged in as admin")
    print(f"   Role: {user_info.get('role')}")
    print(f"   User ID: {user_info.get('user_id')}")
    
    # Get pending jobs
    pending_response = requests.get(f"{API_BASE_URL}/admin/jobs/pending-approval", headers=admin_headers)
    
    print(f"\nPending jobs response:")
    print(f"   Status: {pending_response.status_code}")
    print(f"   Headers: {dict(pending_response.headers)}")
    
    if pending_response.status_code == 200:
        try:
            pending_jobs = pending_response.json()
            print(f"   Response type: {type(pending_jobs)}")
            print(f"   Response length/content: {len(pending_jobs) if isinstance(pending_jobs, (list, dict)) else 'not list/dict'}")
            print(f"   Raw response (first 500 chars): {pending_response.text[:500]}")
            
            if isinstance(pending_jobs, list) and len(pending_jobs) > 0:
                print(f"   First job keys: {list(pending_jobs[0].keys())}")
                first_job = pending_jobs[0]
                print(f"   First job: {first_job.get('title', 'No title')} (ID: {first_job.get('job_id', 'No ID')})")
            elif isinstance(pending_jobs, dict):
                print(f"   Dict keys: {list(pending_jobs.keys())}")
            
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON decode error: {e}")
            print(f"   Raw response: {pending_response.text}")
    else:
        print(f"   ❌ Error response: {pending_response.text}")

if __name__ == "__main__":
    debug_pending_jobs()