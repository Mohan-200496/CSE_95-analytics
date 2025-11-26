"""
Check available users and admin status
"""
import requests
import json

API_BASE_URL = "https://punjab-rozgar-api.onrender.com/api/v1"

def check_users_and_login():
    """Check what users exist and test login"""
    
    print("🔍 Checking User Status and Login\n")
    
    # Try to login as admin first
    print("1️⃣ Testing admin login...")
    admin_login = requests.post(f"{API_BASE_URL}/auth/login", json={
        "email": "admin@test.com", 
        "password": "admin123"
    })
    
    if admin_login.status_code == 200:
        admin_data = admin_login.json()
        admin_token = admin_data.get("access_token")
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        print("✅ Admin login successful")
        
        # Check if there's an admin endpoint to list users
        print("\n2️⃣ Checking admin capabilities...")
        
        # Try to see pending jobs (admin function)
        pending_jobs = requests.get(f"{API_BASE_URL}/admin/jobs/pending-approval", headers=admin_headers)
        if pending_jobs.status_code == 200:
            jobs = pending_jobs.json()
            print(f"   Pending jobs: {len(jobs)}")
        else:
            print(f"   Pending jobs failed: {pending_jobs.status_code}")
            
    else:
        print(f"❌ Admin login failed: {admin_login.status_code}")
        print(f"Response: {admin_login.text}")
    
    # Try different employer email variations
    print("\n3️⃣ Testing employer login variations...")
    
    employer_emails = [
        "employer@company.com",
        "employer@test.com", 
        "emp@test.com",
        "employer@example.com"
    ]
    
    for email in employer_emails:
        print(f"   Trying: {email}")
        emp_login = requests.post(f"{API_BASE_URL}/auth/login", json={
            "email": email, 
            "password": "employer123"
        })
        
        if emp_login.status_code == 200:
            print(f"   ✅ SUCCESS with {email}")
            emp_data = emp_login.json()
            user_info = emp_data.get("user", {})
            print(f"   User ID: {user_info.get('user_id')}")
            print(f"   Role: {user_info.get('role')}")
            print(f"   Name: {user_info.get('full_name')}")
            return email  # Return working email
        else:
            print(f"   ❌ Failed: {emp_login.status_code}")
    
    # Try to create a new employer if none work
    print("\n4️⃣ Creating new employer...")
    new_employer = {
        "email": "newemployer@test.com",
        "password": "employer123",
        "full_name": "Test Employer",
        "role": "employer",
        "company_name": "Test Company",
        "company_description": "Test company for testing"
    }
    
    reg_response = requests.post(f"{API_BASE_URL}/auth/register", json=new_employer)
    if reg_response.status_code == 200:
        print("   ✅ New employer created successfully")
        return "newemployer@test.com"
    else:
        print(f"   ❌ Registration failed: {reg_response.status_code}")
        print(f"   Response: {reg_response.text}")
    
    return None

if __name__ == "__main__":
    working_email = check_users_and_login()
    if working_email:
        print(f"\n🎉 Working employer email: {working_email}")
    else:
        print("\n💥 No working employer found!")