#!/usr/bin/env python3
"""
Test user registration and login
"""

import requests
import json

def test_registration_and_login():
    """Test complete user registration and login flow"""
    
    # Test if server is running
    try:
        response = requests.get('http://127.0.0.1:8000/')
        print(f'Server status: {response.status_code}')
        print(f'Response: {response.json()}')
    except Exception as e:
        print(f'Server connection error: {e}')
        return False
    
    # Register a new user
    print('\n📝 Registering new user...')
    register_data = {
        'email': 'newuser@test.com',
        'password': 'password123',
        'first_name': 'New',
        'last_name': 'User',
        'phone': '+1234567890',
        'role': 'EMPLOYER'
    }
    
    try:
        response = requests.post('http://127.0.0.1:8000/api/v1/auth/register', json=register_data)
        print(f'Registration status: {response.status_code}')
        print(f'Registration response: {response.json()}')
        
        if response.status_code == 201:
            print('✅ User registered successfully!')
            
            # Test login
            print('\n🔐 Testing login...')
            login_data = {'email': 'newuser@test.com', 'password': 'password123'}
            
            login_response = requests.post('http://127.0.0.1:8000/api/v1/auth/login', json=login_data)
            print(f'Login status: {login_response.status_code}')
            
            if login_response.status_code == 200:
                print('✅ Login successful!')
                login_result = login_response.json()
                user_data = login_result.get('user', {})
                print(f'User role: {user_data.get("role", "N/A")}')
                print(f'User email: {user_data.get("email", "N/A")}')
                access_token = login_result.get('access_token', 'N/A')
                print(f'Access token received: {access_token[:50]}...' if len(access_token) > 50 else f'Access token: {access_token}')
                return True
            else:
                print('❌ Login failed')
                print(f'Error: {login_response.json()}')
                return False
        else:
            print('❌ Registration failed')
            return False
            
    except Exception as e:
        print(f'Error: {e}')
        return False

if __name__ == "__main__":
    success = test_registration_and_login()
    if success:
        print('\n🎉 Registration and login test completed successfully!')
    else:
        print('\n❌ Registration and login test failed')