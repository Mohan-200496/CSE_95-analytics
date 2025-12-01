"""
Monitor deployment and test job creation functionality
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

async def monitor_deployment():
    """Monitor deployment status and test functionality"""
    
    api_base = "https://punjab-rozgar-api.onrender.com"
    
    print("🚀 MONITORING DEPLOYMENT STATUS")
    print("=" * 50)
    
    max_attempts = 10
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        print(f"\n⏱️  Attempt {attempt}/{max_attempts} - {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test API health
                async with session.get(f"{api_base}/health", timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status == 200:
                        health_data = await response.json()
                        print(f"✅ API Health: {health_data.get('status', 'unknown')}")
                        print(f"   Version: {health_data.get('version', 'unknown')}")
                        
                        # Test job creation if API is healthy
                        print("\n🧪 Testing job creation...")
                        
                        job_data = {
                            "title": "Deployment Test Job",
                            "description": "Testing job creation after deployment fix",
                            "job_type": "full_time",
                            "category": "Technology", 
                            "location_city": "Chandigarh",
                            "salary_min": 50000,
                            "salary_max": 80000
                        }
                        
                        async with session.post(
                            f"{api_base}/api/v1/jobs/test-create",
                            json=job_data,
                            headers={'Content-Type': 'application/json'},
                            timeout=aiohttp.ClientTimeout(total=20)
                        ) as job_response:
                            
                            if job_response.status == 200:
                                job_result = await job_response.json()
                                print("🎉 JOB CREATION SUCCESS!")
                                print(f"   Job ID: {job_result.get('job_id')}")
                                print(f"   Title: {job_result.get('title')}")
                                print(f"   Type: {job_result.get('job_type')}")
                                print(f"   Status: {job_result.get('status')}")
                                
                                print("\n✅ DEPLOYMENT SUCCESSFUL - Job creation working!")
                                print("🌐 Test URLs:")
                                print("   Frontend: https://punjab-rozgar-portal.onrender.com/test-job-creation.html")
                                print("   API Health: https://punjab-rozgar-api.onrender.com/health")
                                return True
                            else:
                                error_text = await job_response.text()
                                print(f"❌ Job creation failed: {job_response.status}")
                                print(f"   Error: {error_text}")
                                
                    else:
                        print(f"❌ API Health check failed: {response.status}")
                        
        except asyncio.TimeoutError:
            print("⏱️  Request timed out - API may still be starting up")
        except Exception as e:
            print(f"❌ Connection error: {str(e)}")
            
        if attempt < max_attempts:
            print("   ⏳ Waiting 30 seconds before next attempt...")
            await asyncio.sleep(30)
    
    print("\n❌ Deployment monitoring failed - manual check required")
    return False

if __name__ == "__main__":
    asyncio.run(monitor_deployment())