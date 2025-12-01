#!/usr/bin/env python3
"""
Quick functionality test for Punjab Rozgar Portal
"""

import requests
import json

def test_api_endpoints():
    """Test key API endpoints"""
    base_url = "https://punjab-rozgar-api.onrender.com/api/v1"
    
    print("🧪 Testing Punjab Rozgar Portal API")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get("https://punjab-rozgar-api.onrender.com/health", timeout=10)
        print(f"✅ Health Check: {response.status_code}")
        if response.status_code == 200:
            print(f"   📊 Status: {response.json()}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
    
    # Test root endpoint
    try:
        response = requests.get("https://punjab-rozgar-api.onrender.com/", timeout=10)
        print(f"✅ Root Endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Root Endpoint Failed: {e}")
    
    # Test jobs listing
    try:
        response = requests.get(f"{base_url}/jobs/", timeout=10)
        print(f"✅ Jobs Listing: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   📊 Found {len(data.get('jobs', []))} jobs")
    except Exception as e:
        print(f"❌ Jobs Listing Failed: {e}")
    
    # Test authentication endpoint
    try:
        auth_data = {
            "username": "employer@test.com",
            "password": "employer123"
        }
        response = requests.post(f"{base_url}/auth/login", 
                               data=auth_data,
                               headers={"Content-Type": "application/x-www-form-urlencoded"},
                               timeout=10)
        print(f"✅ Authentication: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            print(f"   🔑 Token received: {token_data.get('access_token', 'None')[:20]}...")
            
            # Test authenticated endpoint
            token = token_data.get('access_token')
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{base_url}/jobs/my-jobs", headers=headers, timeout=10)
            print(f"✅ Authenticated Request: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Authentication Failed: {e}")
    
    print("\n🏁 API Testing Complete")

def test_frontend_pages():
    """Test if frontend pages are accessible"""
    base_url = "https://punjab-rozgar-portal1.onrender.com"
    
    pages = [
        "/",
        "/index.html",
        "/pages/auth/login.html", 
        "/pages/employer/dashboard.html",
        "/pages/jobseeker/dashboard.html"
    ]
    
    print("\n🖥️ Testing Frontend Pages")
    print("=" * 50)
    
    for page in pages:
        try:
            response = requests.get(f"{base_url}{page}", timeout=10)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {page}: {response.status_code}")
        except Exception as e:
            print(f"❌ {page}: {e}")

if __name__ == "__main__":
    test_api_endpoints()
    test_frontend_pages()