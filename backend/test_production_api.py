"""
Test production API health and job endpoints
"""

import asyncio
import aiohttp
import json

async def test_production_api():
    """Test various production API endpoints"""
    
    base_url = 'https://punjab-rozgar-api.onrender.com'
    
    try:
        async with aiohttp.ClientSession() as session:
            print("🧪 Testing production API endpoints...")
            
            # Test health endpoint
            try:
                async with session.get(f'{base_url}/health') as response:
                    print(f"Health check: {response.status}")
                    if response.status == 200:
                        health_data = await response.json()
                        print(f"✅ API is healthy: {health_data}")
                    else:
                        print(f"❌ Health check failed: {await response.text()}")
            except Exception as e:
                print(f"❌ Health check error: {e}")
            
            # Test jobs list endpoint
            try:
                async with session.get(f'{base_url}/api/v1/jobs/') as response:
                    print(f"Jobs list: {response.status}")
                    if response.status == 200:
                        jobs_data = await response.json()
                        print(f"✅ Jobs endpoint working, found {len(jobs_data)} jobs")
                        if jobs_data:
                            print(f"Sample job: {jobs_data[0].get('title', 'No title')}")
                    else:
                        print(f"❌ Jobs list failed: {await response.text()}")
            except Exception as e:
                print(f"❌ Jobs list error: {e}")
            
            # Test debug endpoint 
            try:
                debug_data = {
                    "title": "Debug Test Job",
                    "job_type": "full_time"
                }
                async with session.post(
                    f'{base_url}/api/v1/jobs/debug-job',
                    json=debug_data,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    print(f"Debug job creation: {response.status}")
                    debug_response = await response.text()
                    print(f"Debug response: {debug_response}")
            except Exception as e:
                print(f"❌ Debug endpoint error: {e}")
                
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_production_api())