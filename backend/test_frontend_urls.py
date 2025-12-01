#!/usr/bin/env python3
"""Test frontend URL structure"""

import requests

def test_frontend_urls():
    base_url = 'https://punjab-rozgar-portal1.onrender.com'
    print('🔍 Testing Frontend URL Structure')
    print('=' * 40)
    
    test_paths = [
        ('Root', ''),
        ('Index', '/index.html'),
        ('Login', '/pages/auth/login.html'),
        ('Employer Dashboard', '/pages/employer/dashboard.html'),
        ('Job Seeker Dashboard', '/pages/jobseeker/dashboard.html'),
        ('Alt Login', '/auth/login.html'),
        ('Alt Employer', '/employer/dashboard.html')
    ]
    
    working_paths = []
    for name, path in test_paths:
        try:
            url = f'{base_url}{path}'
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f'✅ {name}: 200 OK')
                working_paths.append(path or '/')
            else:
                print(f'❌ {name}: {response.status_code}')
        except Exception as e:
            print(f'❌ {name}: ERROR - {str(e)[:30]}...')
    
    print(f'\n📍 Working paths: {working_paths}')
    return working_paths

if __name__ == "__main__":
    test_frontend_urls()