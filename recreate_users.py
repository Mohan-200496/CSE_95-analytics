"""
Recreate users with proper registration schema
"""
import requests
import json

API_BASE_URL = "https://punjab-rozgar-api.onrender.com/api/v1"

def recreate_users():
    """Recreate test users with correct schema"""
    
    print("🔧 Recreating Users with Correct Schema\n")
    
    # Create admin user
    print("1️⃣ Creating admin user...")
    admin_data = {
        "email": "admin@test.com",
        "password": "admin123",
        "first_name": "Admin",
        "last_name": "User",
        "role": "job_seeker",  # Create as job_seeker first
        "city": "Lahore"
    }
    
    admin_reg = requests.post(f"{API_BASE_URL}/auth/register", json=admin_data)
    if admin_reg.status_code == 200:
        print("   ✅ Admin user created")
        admin_result = admin_reg.json()
        admin_user_id = admin_result.get("user", {}).get("user_id")
        print(f"   Admin User ID: {admin_user_id}")
    else:
        print(f"   ❌ Admin creation failed: {admin_reg.status_code}")
        print(f"   Response: {admin_reg.text}")
        return False
    
    # Create employer user
    print("\n2️⃣ Creating employer user...")
    employer_data = {
        "email": "employer@test.com", 
        "password": "employer123",
        "first_name": "Test",
        "last_name": "Employer",
        "role": "employer",
        "city": "Lahore"
    }
    
    emp_reg = requests.post(f"{API_BASE_URL}/auth/register", json=employer_data)
    if emp_reg.status_code == 200:
        print("   ✅ Employer user created")
        emp_result = emp_reg.json()
        emp_user_id = emp_result.get("user", {}).get("user_id")
        print(f"   Employer User ID: {emp_user_id}")
    else:
        print(f"   ❌ Employer creation failed: {emp_reg.status_code}")
        print(f"   Response: {emp_reg.text}")
        return False
    
    # Create job seeker user
    print("\n3️⃣ Creating job seeker user...")
    seeker_data = {
        "email": "seeker@test.com",
        "password": "seeker123", 
        "first_name": "Test",
        "last_name": "Seeker",
        "role": "job_seeker",
        "city": "Karachi"
    }
    
    seeker_reg = requests.post(f"{API_BASE_URL}/auth/register", json=seeker_data)
    if seeker_reg.status_code == 200:
        print("   ✅ Job seeker user created")
        seeker_result = seeker_reg.json()
        seeker_user_id = seeker_result.get("user", {}).get("user_id")
        print(f"   Job Seeker User ID: {seeker_user_id}")
    else:
        print(f"   ❌ Job seeker creation failed: {seeker_reg.status_code}")
        print(f"   Response: {seeker_reg.text}")
        return False
    
    # Promote admin user to admin role
    print(f"\n4️⃣ Promoting admin user to admin role...")
    
    # First login as the admin user
    admin_login = requests.post(f"{API_BASE_URL}/auth/login", json={
        "email": "admin@test.com",
        "password": "admin123"
    })
    
    if admin_login.status_code == 200:
        admin_token = admin_login.json().get("access_token")
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Call initial admin setup
        setup_response = requests.post(
            f"{API_BASE_URL}/admin/initial-admin-setup",
            headers=admin_headers
        )
        
        if setup_response.status_code == 200:
            print("   ✅ Admin role promoted successfully")
        else:
            print(f"   ❌ Admin promotion failed: {setup_response.status_code}")
            print(f"   Response: {setup_response.text}")
    else:
        print(f"   ❌ Admin login for promotion failed: {admin_login.status_code}")
    
    print("\n5️⃣ Testing all logins...")
    
    users = [
        ("admin@test.com", "admin123", "Admin"),
        ("employer@test.com", "employer123", "Employer"),
        ("seeker@test.com", "seeker123", "Job Seeker")
    ]
    
    for email, password, name in users:
        login_test = requests.post(f"{API_BASE_URL}/auth/login", json={
            "email": email, 
            "password": password
        })
        
        if login_test.status_code == 200:
            user_data = login_test.json()
            user_info = user_data.get("user", {})
            print(f"   ✅ {name}: Role = {user_info.get('role')}, ID = {user_info.get('user_id')}")
        else:
            print(f"   ❌ {name}: Login failed ({login_test.status_code})")
    
    return True

if __name__ == "__main__":
    if recreate_users():
        print("\n🎉 All users recreated successfully!")
        print("\nCredentials:")
        print("  Admin:    admin@test.com / admin123")
        print("  Employer: employer@test.com / employer123")
        print("  Seeker:   seeker@test.com / seeker123")
    else:
        print("\n💥 User recreation failed!")