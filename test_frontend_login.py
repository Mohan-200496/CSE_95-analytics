"""
Test login credentials to help debug frontend login issues
"""
import requests

API_BASE_URL = "https://punjab-rozgar-api.onrender.com/api/v1"

def test_login_credentials():
    """Test the exact credentials that frontend should use"""
    
    print("🔐 Testing Login Credentials for Frontend\n")
    
    test_credentials = [
        ("admin@test.com", "admin123", "Admin"),
        ("employer@test.com", "employer123", "Employer"),
        ("seeker@test.com", "seeker123", "Job Seeker")
    ]
    
    for email, password, role in test_credentials:
        print(f"Testing {role} ({email}):")
        
        # Test exactly what frontend sends
        login_data = {
            "email": email,
            "password": password
        }
        
        print(f"  📤 Sending: {login_data}")
        
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json=login_data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Cache-Control': 'no-cache'
            }
        )
        
        print(f"  📥 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            user_info = data.get("user", {})
            print(f"  ✅ SUCCESS!")
            print(f"     User ID: {user_info.get('user_id')}")
            print(f"     Role: {user_info.get('role')}")
            print(f"     Name: {user_info.get('first_name')} {user_info.get('last_name')}")
            print(f"     Token: {data.get('access_token')[:20]}...")
        else:
            try:
                error_data = response.json()
                print(f"  ❌ ERROR: {error_data.get('message', 'Unknown error')}")
                print(f"     Details: {error_data}")
            except:
                print(f"  ❌ ERROR: {response.text}")
        
        print()

def test_api_connectivity():
    """Test basic API connectivity"""
    
    print("🌐 Testing API Connectivity\n")
    
    # Test basic endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        print(f"API Root: {response.status_code}")
        if response.status_code == 200:
            print("✅ API is accessible")
        else:
            print(f"⚠️ API returned: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ API connection failed: {e}")

if __name__ == "__main__":
    test_api_connectivity()
    test_login_credentials()