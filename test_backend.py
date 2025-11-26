"""
Test backend deployment and check available endpoints
"""
import asyncio
import aiohttp

async def test_backend():
    """Test backend connectivity and endpoints"""
    
    API_BASE_URL = "https://punjab-rozgar-api.onrender.com/api/v1"
    
    async with aiohttp.ClientSession() as session:
        # Test health check
        print("🔍 Testing backend connectivity...")
        try:
            async with session.get("https://punjab-rozgar-api.onrender.com/health") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Backend health: {result}")
                else:
                    print(f"⚠️  Health check status: {response.status}")
        except Exception as e:
            print(f"❌ Health check error: {e}")
        
        # Test auth endpoints
        print("\n🔍 Testing auth endpoints...")
        try:
            async with session.get(f"{API_BASE_URL}/auth/") as response:
                print(f"Auth endpoint status: {response.status}")
        except Exception as e:
            print(f"Auth endpoint error: {e}")
        
        # Test admin endpoints
        print("\n🔍 Testing admin endpoints...")
        try:
            async with session.get(f"{API_BASE_URL}/admin/stats") as response:
                print(f"Admin stats endpoint status: {response.status}")
        except Exception as e:
            print(f"Admin stats endpoint error: {e}")
            
        # Test the initial admin setup endpoint
        print("\n🔍 Testing initial admin setup endpoint...")
        try:
            async with session.post(f"{API_BASE_URL}/admin/initial-admin-setup?email=test@example.com") as response:
                result = await response.text()
                print(f"Initial admin setup status: {response.status}")
                print(f"Response: {result[:200]}...")
        except Exception as e:
            print(f"Initial admin setup error: {e}")

if __name__ == "__main__":
    asyncio.run(test_backend())