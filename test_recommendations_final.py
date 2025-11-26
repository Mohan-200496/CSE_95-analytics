"""
Test the fixed recommendations endpoint
"""
import requests

API_BASE_URL = "https://punjab-rozgar-api.onrender.com/api/v1"

def test_recommendations_endpoint():
    """Test the recommendations endpoint after the fix"""
    
    print("🎯 Testing Fixed Recommendations Endpoint\n")
    
    # Login as job seeker
    login_response = requests.post(f"{API_BASE_URL}/auth/login", json={
        "email": "seeker@test.com",
        "password": "seeker123"
    })
    
    if login_response.status_code != 200:
        print("❌ Job seeker login failed")
        return
    
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    user_info = login_response.json().get("user", {})
    
    print(f"✅ Logged in as: {user_info.get('first_name')} {user_info.get('last_name')}")
    print(f"   Role: {user_info.get('role')}")
    print(f"   User ID: {user_info.get('user_id')}")
    
    # Test recommendations
    print(f"\\n🔍 Testing recommendations endpoint...")
    
    rec_response = requests.get(f"{API_BASE_URL}/recommendations", headers=headers)
    
    print(f"Status: {rec_response.status_code}")
    
    if rec_response.status_code == 200:
        recommendations = rec_response.json()
        print(f"✅ SUCCESS! Got {len(recommendations)} recommendations")
        
        # Show recommendation details
        for i, job in enumerate(recommendations):
            print(f"\\n📋 Recommendation {i+1}:")
            print(f"   Title: {job.get('title')}")
            print(f"   Company: {job.get('company_name', 'Unknown')}")
            print(f"   Location: {job.get('location_city')}, {job.get('location_state')}")
            print(f"   Salary: ${job.get('salary_min', 0):,} - ${job.get('salary_max', 0):,}")
            print(f"   Match Score: {job.get('match_score', 'N/A')}%")
            print(f"   Job Type: {job.get('job_type', 'Unknown')}")
            print(f"   Remote: {job.get('remote_allowed', False)}")
            
        return True
        
    elif rec_response.status_code == 403:
        print("🚫 Access forbidden (this shouldn't happen for job seekers)")
        print(f"Response: {rec_response.text}")
        
    else:
        print(f"❌ Error: {rec_response.status_code}")
        print(f"Response: {rec_response.text}")
        
    return False

def test_role_based_access():
    """Test that other roles are properly blocked"""
    
    print(f"\\n🔒 Testing Role-Based Access Control\\n")
    
    test_users = [
        ("admin@test.com", "admin123", "Admin"),
        ("employer@test.com", "employer123", "Employer")
    ]
    
    for email, password, role in test_users:
        login_response = requests.post(f"{API_BASE_URL}/auth/login", json={
            "email": email, "password": password
        })
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            rec_response = requests.get(f"{API_BASE_URL}/recommendations", headers=headers)
            
            print(f"{role} recommendations: ", end="")
            if rec_response.status_code == 403:
                print("✅ Properly forbidden")
            else:
                print(f"❌ Unexpected: {rec_response.status_code}")

if __name__ == "__main__":
    if test_recommendations_endpoint():
        test_role_based_access()
        print(f"\\n🎉 Recommendations system is fully functional!")
    else:
        print(f"\\n💥 Recommendations system needs more fixes")