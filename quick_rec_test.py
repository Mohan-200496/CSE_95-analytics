"""
Simple test to check if the recommendations endpoint is working at all
"""
import requests

API_BASE_URL = "https://punjab-rozgar-api.onrender.com/api/v1"

def quick_recommendations_test():
    """Quick test of recommendations endpoint routing"""
    
    print("🔍 Quick Recommendations Test\n")
    
    # Login as job seeker
    login_response = requests.post(f"{API_BASE_URL}/auth/login", json={
        "email": "seeker@test.com",
        "password": "seeker123"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Job seeker logged in")
    
    # Test different recommendation endpoints
    endpoints = [
        "/jobs/recommendations",
        "/jobs/recommendations/",
        "/recommendations",
        "/recommendations/"
    ]
    
    for endpoint in endpoints:
        print(f"\n🧪 Testing endpoint: {endpoint}")
        response = requests.get(f"{API_BASE_URL}{endpoint}", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 404:
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS - Got {len(data) if isinstance(data, list) else 'non-list'} results")
            else:
                print(f"   Response: {response.text[:200]}")

if __name__ == "__main__":
    quick_recommendations_test()