"""
Promote admin user to proper admin role via API
"""
import asyncio
import aiohttp
import json

# API base URL for production
API_BASE_URL = "https://punjab-rozgar-api.onrender.com/api/v1"

async def promote_admin():
    """Promote admin user using the new admin setup endpoint"""
    
    print("🚀 Promoting admin user to proper admin role...")
    
    async with aiohttp.ClientSession() as session:
        try:
            # Use the initial admin setup endpoint
            promote_url = f"{API_BASE_URL}/admin/initial-admin-setup"
            
            # Use query parameter for email
            async with session.post(f"{promote_url}?email=admin@punjabrozgar.gov.pk") as response:
                result = await response.json() if response.content_type == 'application/json' else await response.text()
                
                if response.status == 200:
                    print("✅ Admin promotion successful!")
                    print(f"   User ID: {result.get('user_id')}")
                    print(f"   New Role: {result.get('role')}")
                    print(f"   Message: {result.get('message')}")
                    
                    # Test login to verify admin role
                    await test_admin_login()
                    
                elif response.status == 403:
                    print("ℹ️  Admin users already exist - using regular promotion")
                    # Could add fallback to regular promotion here
                else:
                    print(f"❌ Promotion failed: {response.status}")
                    print(f"   Error: {result}")
                    
        except Exception as e:
            print(f"❌ Error: {str(e)}")

async def test_admin_login():
    """Test login with admin credentials to verify promotion"""
    print("\n🔍 Testing admin login...")
    
    async with aiohttp.ClientSession() as session:
        try:
            login_url = f"{API_BASE_URL}/auth/login"
            login_payload = {
                'email': 'admin@punjabrozgar.gov.pk',
                'password': 'admin123'
            }
            
            async with session.post(login_url, json=login_payload) as response:
                if response.status == 200:
                    result = await response.json()
                    role = result.get('user', {}).get('role')
                    print(f"✅ Admin login successful! Role: {role}")
                    
                    if role == 'admin':
                        print("🎉 Admin promotion completed successfully!")
                    else:
                        print(f"⚠️  Warning: Expected 'admin' role, got '{role}'")
                else:
                    result = await response.json() if response.content_type == 'application/json' else await response.text()
                    print(f"❌ Login failed: {response.status} - {result}")
                    
        except Exception as e:
            print(f"❌ Login test error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(promote_admin())