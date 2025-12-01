"""
Quick API test to debug 403 errors
"""

import requests
import json

API_BASE_URL = "https://punjab-rozgar-api.onrender.com/api/v1"

def test_jobs_endpoint():
    """Test the jobs endpoint directly"""
    
    print("🔍 Testing Jobs Endpoint for 403 Errors")
    print("=" * 50)
    
    # Test without authentication
    print("\n1. Testing without authentication...")
    try:
        response = requests.get(f"{API_BASE_URL}/jobs/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 403:
            print(f"   Error: {response.text}")
            print("   ⚠️  403 Forbidden - this shouldn't happen for public endpoint")
        elif response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: Found {len(data)} jobs")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test recent jobs endpoint
    print("\n2. Testing recent jobs endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/jobs/recent", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 403:
            print(f"   Error: {response.text}")
        elif response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data}")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test with authentication
    print("\n3. Testing with authentication...")
    try:
        # Login first
        login_response = requests.post(f"{API_BASE_URL}/auth/login", 
                                     json={
                                         "email": "employer@test.com", 
                                         "password": "employer123"
                                     },
                                     timeout=10)
        
        if login_response.status_code == 200:
            token = login_response.json().get('access_token')
            headers = {'Authorization': f'Bearer {token}'}
            
            # Test jobs endpoint with auth
            auth_response = requests.get(f"{API_BASE_URL}/jobs/", headers=headers, timeout=10)
            print(f"   Status with auth: {auth_response.status_code}")
            
            if auth_response.status_code == 403:
                print(f"   Error: {auth_response.text}")
                print("   ⚠️  403 Forbidden even with valid token")
            elif auth_response.status_code == 200:
                data = auth_response.json()
                print(f"   ✅ Success: Found {len(data)} jobs")
            else:
                print(f"   Response: {auth_response.text}")
                
            # Test my-jobs endpoint
            my_jobs_response = requests.get(f"{API_BASE_URL}/jobs/my-jobs", headers=headers, timeout=10)
            print(f"   My jobs status: {my_jobs_response.status_code}")
            if my_jobs_response.status_code == 200:
                data = my_jobs_response.json()
                print(f"   ✅ My jobs: Found {len(data)} jobs")
            else:
                print(f"   My jobs error: {my_jobs_response.text}")
                
        else:
            print(f"   Login failed: {login_response.status_code} - {login_response.text}")
            
    except Exception as e:
        print(f"   ❌ Auth test error: {e}")
    
    # Test health endpoint
    print("\n4. Testing health endpoint...")
    try:
        response = requests.get("https://punjab-rozgar-api.onrender.com/health", timeout=10)
        print(f"   Health status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ API is healthy")
        else:
            print(f"   ⚠️  Health check failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")

if __name__ == "__main__":
    test_jobs_endpoint()