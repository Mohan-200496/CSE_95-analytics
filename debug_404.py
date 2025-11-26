"""
Debug 404 error on jobs endpoint
"""
import requests

API_BASE_URL = "https://punjab-rozgar-api.onrender.com/api/v1"

def debug_jobs_endpoint():
    """Debug the jobs endpoint 404 error"""
    
    print("🔍 Debugging Jobs Endpoint 404 Error\n")
    
    # Test basic API connectivity
    print("1️⃣ Testing API connectivity...")
    try:
        response = requests.get(f"https://punjab-rozgar-api.onrender.com", timeout=10)
        print(f"   API root: {response.status_code}")
    except Exception as e:
        print(f"   ❌ API unreachable: {e}")
        return
    
    # Test jobs endpoint without auth
    print("\n2️⃣ Testing jobs endpoint without auth...")
    jobs_response = requests.get(f"{API_BASE_URL}/jobs/")
    print(f"   GET /jobs/: {jobs_response.status_code}")
    
    if jobs_response.status_code != 200:
        print(f"   Response: {jobs_response.text}")
    
    # Test with auth
    print("\n3️⃣ Testing with authentication...")
    
    # Login as employer
    login_response = requests.post(f"{API_BASE_URL}/auth/login", json={
        "email": "employer@test.com",
        "password": "employer123"
    })
    
    if login_response.status_code == 200:
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test GET jobs with auth
        auth_jobs_response = requests.get(f"{API_BASE_URL}/jobs/", headers=headers)
        print(f"   GET /jobs/ with auth: {auth_jobs_response.status_code}")
        
        # Test POST to create job
        test_job = {
            "title": "Test Job Debug",
            "description": "Testing job creation endpoint",
            "requirements": "Debug skills",
            "responsibilities": "Fix 404 errors",
            "job_type": "full_time",
            "category": "Technology",
            "location_city": "Lahore",
            "salary_min": 50000,
            "salary_max": 70000,
            "contact_email": "test@debug.com"
        }
        
        print(f"   Testing job creation...")
        create_response = requests.post(f"{API_BASE_URL}/jobs/", 
                                      json=test_job, 
                                      headers=headers)
        print(f"   POST /jobs/: {create_response.status_code}")
        
        if create_response.status_code == 200:
            result = create_response.json()
            print(f"     ✅ Job created: {result.get('job_id')}")
        else:
            print(f"     ❌ Error: {create_response.text}")
    else:
        print(f"   ❌ Login failed: {login_response.status_code}")

if __name__ == "__main__":
    debug_jobs_endpoint()