"""
Test job creation API endpoint
"""

import asyncio
import aiohttp
import json

async def test_job_creation_api():
    """Test the job creation API endpoint"""
    
    # Test job data
    job_data = {
        "title": "Senior Software Developer",
        "description": "We are looking for a senior software developer...",
        "requirements": "5+ years experience in Python",
        "responsibilities": "Develop and maintain applications",
        "job_type": "full_time",
        "category": "Technology",
        "subcategory": "Software Development",
        "location_city": "Chandigarh",
        "location_state": "Punjab",
        "remote_allowed": False,
        "salary_min": 60000,
        "salary_max": 90000,
        "salary_currency": "INR",
        "salary_period": "monthly",
        "experience_min": 5,
        "experience_max": 10,
        "education_level": "Bachelor's",
        "skills_required": ["Python", "FastAPI", "PostgreSQL"],
        "skills_preferred": ["React", "Docker"],
        "application_deadline": "2024-12-31T23:59:59",
        "application_method": "online",
        "contact_email": "hr@testcompany.com",
        "resume_required": True
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print("🧪 Testing job creation API...")
            
            # Test the create job endpoint
            async with session.post(
                'https://punjab-rozgar-api.onrender.com/api/v1/jobs/',
                json=job_data,
                headers={'Content-Type': 'application/json'}
            ) as response:
                
                print(f"Status: {response.status}")
                response_text = await response.text()
                print(f"Response: {response_text}")
                
                if response.status == 200:
                    result = json.loads(response_text)
                    print(f"✅ Job created successfully!")
                    print(f"Job ID: {result.get('job_id')}")
                    print(f"Title: {result.get('title')}")
                    print(f"Job Type: {result.get('job_type')}")
                    print(f"Status: {result.get('status')}")
                else:
                    print(f"❌ Job creation failed with status: {response.status}")
                    print(f"Error: {response_text}")
                    
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_job_creation_api())