#!/usr/bin/env python3
import requests

login_data = {'email': 'employer@test.com', 'password': 'test123'}
response = requests.post('http://127.0.0.1:8000/api/v1/auth/login', json=login_data)
print(f'Login status: {response.status_code}')
if response.status_code == 200:
    print('✅ Login successful!')
else:
    print('❌ Login failed')
    print(f'Response: {response.text}')