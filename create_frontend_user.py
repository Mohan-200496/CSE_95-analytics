"""
Create the missing employer@company.com user that frontend is looking for
"""
import requests

API_BASE_URL = "https://punjab-rozgar-api.onrender.com/api/v1"

def create_missing_employer():
    """Create the employer@company.com user that frontend expects"""
    
    print("🔧 Creating Missing Frontend Employer User\n")
    
    # Create the employer user with the email frontend expects
    employer_data = {
        "email": "employer@company.com",
        "password": "employer123", 
        "first_name": "Frontend",
        "last_name": "Employer",
        "role": "employer",
        "city": "Lahore"
    }
    
    reg_response = requests.post(f"{API_BASE_URL}/auth/register", json=employer_data)
    
    if reg_response.status_code == 200:
        result = reg_response.json()
        user_info = result.get("user", {})
        print("✅ Created employer@company.com user")
        print(f"   User ID: {user_info.get('user_id')}")
        print(f"   Role: {user_info.get('role')}")
        
        # Test login immediately
        login_response = requests.post(f"{API_BASE_URL}/auth/login", json={
            "email": "employer@company.com",
            "password": "employer123"
        })
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            login_user = login_data.get("user", {})
            print("✅ Login test successful")
            print(f"   Logged in as: {login_user.get('first_name')} {login_user.get('last_name')}")
            print(f"   Token: {login_data.get('access_token')[:20]}...")
            return True
        else:
            print(f"❌ Login test failed: {login_response.status_code}")
            print(f"   Error: {login_response.text}")
            
    elif reg_response.status_code == 400:
        # User might already exist
        error_data = reg_response.json()
        if "already registered" in error_data.get("detail", "").lower():
            print("ℹ️ User already exists, testing login...")
            
            login_response = requests.post(f"{API_BASE_URL}/auth/login", json={
                "email": "employer@company.com",
                "password": "employer123"
            })
            
            if login_response.status_code == 200:
                print("✅ Existing user login successful")
                return True
            else:
                print(f"❌ Existing user login failed: {login_response.status_code}")
        else:
            print(f"❌ Registration failed: {error_data}")
    else:
        print(f"❌ Registration failed: {reg_response.status_code}")
        print(f"   Response: {reg_response.text}")
    
    return False

if __name__ == "__main__":
    if create_missing_employer():
        print(f"\n🎉 Frontend employer user is ready!")
        print(f"   Frontend can now login with: employer@company.com / employer123")
    else:
        print(f"\n💥 Failed to setup frontend employer user")