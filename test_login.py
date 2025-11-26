"""
Test login functionality with the created demo users
"""
import asyncio
import aiohttp
import json

# API base URL for production
API_BASE_URL = "https://punjab-rozgar-api.onrender.com/api/v1"

async def test_login():
    """Test login with demo users"""
    
    test_users = [
        {
            'email': 'admin@punjabrozgar.gov.pk',
            'password': 'admin123',
            'description': '👨‍💼 Admin User'
        },
        {
            'email': 'employer@company.com',
            'password': 'employer123',
            'description': '🏢 Employer User'
        },
        {
            'email': 'jobseeker@email.com',
            'password': 'jobseeker123',
            'description': '👤 Job Seeker User'
        }
    ]
    
    print("🔐 Testing login functionality...")
    
    async with aiohttp.ClientSession() as session:
        for user_data in test_users:
            try:
                # Test login
                login_url = f"{API_BASE_URL}/auth/login"
                login_payload = {
                    'email': user_data['email'],
                    'password': user_data['password']
                }
                
                async with session.post(login_url, json=login_payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ {user_data['description']}: Login successful!")
                        print(f"   Token received: {result.get('access_token', 'N/A')[:50]}...")
                        print(f"   User role: {result.get('user', {}).get('role', 'N/A')}")
                    else:
                        result = await response.json() if response.content_type == 'application/json' else await response.text()
                        print(f"❌ {user_data['description']}: Login failed!")
                        print(f"   Status: {response.status}")
                        print(f"   Error: {result}")
                        
            except Exception as e:
                print(f"❌ Error testing login for {user_data['description']}: {str(e)}")
    
    print("\n🎯 Login test complete!")
    print("\n🌐 You can now test these credentials at:")
    print("https://punjab-rozgar-portal1.onrender.com")

if __name__ == "__main__":
    asyncio.run(test_login())