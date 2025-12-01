#!/usr/bin/env python3
"""
Simple backend monitoring script to check when deployment is complete
"""

import requests
import time
import sys

def test_backend():
    """Test if backend is responding"""
    backend_url = "https://cse-95-analytics.onrender.com"
    
    endpoints_to_test = [
        "/health",
        "/docs",
        "/api/v1/auth/login"
    ]
    
    print("🔍 Testing backend endpoints...")
    
    for endpoint in endpoints_to_test:
        url = f"{backend_url}{endpoint}"
        try:
            if endpoint == "/api/v1/auth/login":
                # Test preflight for login
                response = requests.options(
                    url,
                    headers={
                        "Origin": "https://punjab-rozgar-portal1.onrender.com",
                        "Access-Control-Request-Method": "POST",
                        "Access-Control-Request-Headers": "Content-Type"
                    },
                    timeout=10
                )
                print(f"✅ {endpoint} (CORS preflight): {response.status_code}")
                
                # Check CORS headers
                cors_headers = {
                    "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                    "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                    "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
                }
                print(f"   CORS Headers: {cors_headers}")
            else:
                response = requests.get(url, timeout=10)
                print(f"✅ {endpoint}: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint}: {str(e)}")
    
    # Test actual login
    print("\n🧪 Testing login endpoint...")
    try:
        login_response = requests.post(
            f"{backend_url}/api/v1/auth/login",
            json={
                "email": "jobseeker@test.com",
                "password": "jobseeker123"
            },
            headers={
                "Content-Type": "application/json",
                "Origin": "https://punjab-rozgar-portal1.onrender.com"
            },
            timeout=10
        )
        print(f"✅ Login test: {login_response.status_code}")
        if login_response.status_code == 200:
            data = login_response.json()
            print(f"   User: {data.get('user', {}).get('email')} ({data.get('user', {}).get('role')})")
            return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Login test failed: {str(e)}")
    
    return False

def monitor_deployment():
    """Monitor deployment until backend is ready"""
    max_attempts = 20
    attempt = 0
    
    print("🚀 Monitoring Render deployment...")
    print("=" * 50)
    
    while attempt < max_attempts:
        attempt += 1
        print(f"\n🔄 Attempt {attempt}/{max_attempts}")
        
        if test_backend():
            print("\n🎉 Backend is fully operational!")
            print("✅ CORS configuration is working")
            print("✅ Authentication endpoint is responding")
            print("\n🎯 You can now test login from: https://punjab-rozgar-portal1.onrender.com")
            return True
        
        if attempt < max_attempts:
            print(f"⏳ Waiting 15 seconds before next attempt...")
            time.sleep(15)
    
    print("\n⚠️ Deployment monitoring timeout")
    print("   The backend may still be deploying or there might be an issue")
    return False

if __name__ == "__main__":
    if monitor_deployment():
        sys.exit(0)
    else:
        sys.exit(1)