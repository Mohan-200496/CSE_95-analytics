#!/usr/bin/env python3
import requests
import json

print('🔄 Testing user creation with detailed error info...')

# Test user data
user_data = {
    'email': 'employer@test.com',
    'password': 'employer123',
    'first_name': 'Test',
    'last_name': 'Employer', 
    'phone': '+1234567890',
    'role': 'EMPLOYER',
    'city': 'Chandigarh'
}

try:
    response = requests.post('http://127.0.0.1:8000/api/v1/auth/register', json=user_data)
    print(f'Registration status: {response.status_code}')
    print(f'Response headers: {dict(response.headers)}')
    print(f'Response text: {response.text}')
    
    if response.status_code != 201:
        print('❌ Registration failed')
        try:
            error_data = response.json()
            print(f'Error details: {json.dumps(error_data, indent=2)}')
        except:
            print('Could not parse error JSON')
    else:
        print('✅ Registration successful!')
        result = response.json()
        print(f'User created: {result.get("user", {})}')
        
except Exception as e:
    print(f'Error: {e}')