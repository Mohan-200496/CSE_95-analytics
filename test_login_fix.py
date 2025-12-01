#!/usr/bin/env python3
"""
Quick login test after fixing user roles
"""

import requests
import json

def test_login():
    """Test login with fixed user data"""
    
    print("🧪 Testing Punjab Rozgar Portal Login")
    print("=" * 50)
    
    # Test employer login
    login_data = {
        "email": "employer@test.com",
        "password": "employer123"
    }
    
    print(f"Testing login: {login_data['email']}")
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Login response status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            token_data = response.json()
            print(f"✅ Access token received: {token_data.get('access_token', 'N/A')[:50]}...")
            print(f"✅ User role: {token_data.get('user', {}).get('role', 'N/A')}")
        else:
            print("❌ Login failed!")
            
    except Exception as e:
        print(f"❌ Login test error: {e}")

if __name__ == "__main__":
    test_login()