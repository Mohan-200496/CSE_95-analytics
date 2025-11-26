"""
Debug admin authentication and pending jobs
"""
import requests
import json

API_BASE_URL = "https://punjab-rozgar-api.onrender.com/api/v1"

def debug_admin_functionality():
    """Debug admin login and job approval functionality"""
    
    print("🔧 Debugging Admin Functionality\n")
    
    # Step 1: Test admin promotion
    print("1️⃣ Testing admin promotion...")
    
    # Create a new admin user
    admin_data = {
        "email": "newadmin@test.com",
        "password": "admin123",
        "first_name": "New",
        "last_name": "Admin",
        "role": "job_seeker",  # Start as job_seeker
        "city": "Lahore"
    }
    
    reg_response = requests.post(f"{API_BASE_URL}/auth/register", json=admin_data)
    if reg_response.status_code == 200:
        print("   ✅ New admin user created")
    else:
        print(f"   ⚠️  Registration response: {reg_response.status_code}")
    
    # Promote to admin using the correct query parameter format
    promote_response = requests.post(f"{API_BASE_URL}/admin/initial-admin-setup?email=newadmin@test.com")
    
    if promote_response.status_code == 200:
        print("   ✅ Admin promotion successful")
        result = promote_response.json()
        print(f"   Admin details: {result}")
    else:
        print(f"   ❌ Admin promotion failed: {promote_response.status_code}")
        print(f"   Response: {promote_response.text}")
        return
    
    # Step 2: Login as admin and test functionality
    print(f"\n2️⃣ Testing admin login and functionality...")
    
    admin_login = requests.post(f"{API_BASE_URL}/auth/login", json={
        "email": "newadmin@test.com",
        "password": "admin123"
    })
    
    if admin_login.status_code != 200:
        print(f"   ❌ Admin login failed: {admin_login.status_code}")
        return
    
    admin_token = admin_login.json().get("access_token")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    user_info = admin_login.json().get("user", {})
    print(f"   ✅ Admin logged in successfully")
    print(f"   Role: {user_info.get('role')}")
    print(f"   User ID: {user_info.get('user_id')}")
    
    # Step 3: Test pending jobs endpoint
    print(f"\n3️⃣ Testing pending jobs endpoint...")
    
    pending_response = requests.get(f"{API_BASE_URL}/admin/jobs/pending-approval", headers=admin_headers)
    
    if pending_response.status_code == 200:
        pending_jobs = pending_response.json()
        print(f"   ✅ Pending jobs retrieved: {len(pending_jobs)} jobs")
        
        for job in pending_jobs:
            print(f"     Job: {job.get('title')} (ID: {job.get('job_id')}, Status: {job.get('status')})")
    else:
        print(f"   ❌ Pending jobs failed: {pending_response.status_code}")
        print(f"   Response: {pending_response.text}")
    
    # Step 4: Test other admin endpoints
    print(f"\n4️⃣ Testing other admin endpoints...")
    
    # Test admin stats
    stats_response = requests.get(f"{API_BASE_URL}/admin/stats", headers=admin_headers)
    if stats_response.status_code == 200:
        stats = stats_response.json()
        print(f"   ✅ Admin stats: {stats.get('total_jobs', 0)} total jobs")
    else:
        print(f"   ❌ Admin stats failed: {stats_response.status_code}")

if __name__ == "__main__":
    debug_admin_functionality()