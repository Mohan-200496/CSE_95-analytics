#!/usr/bin/env python3
import requests
import json

print('🔄 Creating test users via API...')

# Test users data
users = [
    {
        'email': 'employer@test.com',
        'password': 'employer123',
        'first_name': 'Test',
        'last_name': 'Employer', 
        'phone': '+1234567890',
        'role': 'employer',
        'city': 'Chandigarh'
    },
    {
        'email': 'jobseeker@test.com',
        'password': 'jobseeker123',
        'first_name': 'Test',
        'last_name': 'Jobseeker', 
        'phone': '+1234567891',
        'role': 'job_seeker',
        'city': 'Ludhiana'
    },
    {
        'email': 'admin@test.com',
        'password': 'admin123',
        'first_name': 'Test',
        'last_name': 'Admin', 
        'phone': '+1234567892',
        'role': 'job_seeker',
        'city': 'Amritsar'
    }
]

for user_data in users:
    try:
        response = requests.post('http://127.0.0.1:8000/api/v1/auth/register', json=user_data)
        if response.status_code == 201:
            print(f'✅ {user_data["email"]} registered successfully!')
        elif response.status_code == 409:
            print(f'ℹ️ {user_data["email"]} already exists')
        else:
            print(f'❌ {user_data["email"]} registration failed: {response.status_code}')
    except Exception as e:
        print(f'❌ Error registering {user_data["email"]}: {e}')

# Test login for employer
print('\n🔐 Testing employer login...')
try:
    login_response = requests.post('http://127.0.0.1:8000/api/v1/auth/login', 
                                 json={'email': 'employer@test.com', 'password': 'employer123'})
    if login_response.status_code == 200:
        print('✅ Employer login successful!')
    else:
        print(f'❌ Employer login failed: {login_response.status_code}')
except Exception as e:
    print(f'❌ Login test error: {e}')

print('\n✅ User creation process completed!')