#!/usr/bin/env python3
"""
Quick script to test and fix enum issues in production
"""

import requests
import json

def test_production_job_creation():
    """Test job creation with the production API"""
    print("🧪 Testing Production Job Creation")
    print("=" * 40)
    
    # Production API URL
    api_base = "https://punjab-rozgar-api.onrender.com/api/v1"
    
    # Test different enum value formats
    test_cases = [
        {
            "title": "Test Job - Snake Case",
            "description": "Testing with snake_case enum values",
            "job_type": "full_time",
            "category": "Technology",
            "location_city": "Chandigarh",
            "requirements": "Testing enum compatibility",
            "company_name": "Test Company",
            "contact_email": "test@example.com",
            "salary_min": 50000,
            "salary_max": 75000
        },
        {
            "title": "Test Job - Upper Case",
            "description": "Testing with UPPER_CASE enum values",
            "job_type": "FULL_TIME",
            "category": "Engineering",
            "location_city": "Lahore",
            "requirements": "Testing enum compatibility",
            "company_name": "Test Company Upper",
            "contact_email": "test2@example.com",
            "salary_min": 50000,
            "salary_max": 75000
        },
        {
            "title": "Test Job - Kebab Case",
            "description": "Testing with kebab-case enum values",
            "job_type": "full-time",
            "category": "Marketing",
            "location_city": "Multan",
            "requirements": "Testing enum compatibility", 
            "company_name": "Test Company Kebab",
            "contact_email": "test3@example.com",
            "salary_min": 50000,
            "salary_max": 75000
        }
    ]
    
    # Test the no-auth endpoint first
    for i, test_data in enumerate(test_cases, 1):
        print(f"\n🔍 Test Case {i}: {test_data['job_type']}")
        try:
            response = requests.post(
                f"{api_base}/jobs/test-create",
                json=test_data,
                timeout=30
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"   ✅ Success: {result.get('message', 'Job created')}")
                    if 'job_id' in result:
                        print(f"   📋 Job ID: {result['job_id']}")
                else:
                    print(f"   ❌ Failed: {result.get('message', 'Unknown error')}")
                    # Print more details for debugging
                    if 'error' in result:
                        print(f"   🔍 Error details: {result['error'][:300]}...")
            else:
                print(f"   ❌ HTTP Error: {response.text[:200]}")
                
            # Always print the full response for debugging
            print(f"   🔍 Full response: {response.text[:500]}...")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Test getting jobs
    print(f"\n📋 Testing Job Listing...")
    try:
        response = requests.get(f"{api_base}/jobs/", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            jobs = response.json()
            print(f"   📊 Found {len(jobs)} jobs")
            
            if jobs:
                print("   📋 Recent jobs:")
                for job in jobs[:3]:
                    print(f"      - {job.get('title', 'N/A')} ({job.get('job_type', 'N/A')})")
        else:
            print(f"   ❌ Error: {response.text[:100]}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")

def check_api_health():
    """Check if the production API is healthy"""
    print("\n🏥 Checking API Health...")
    
    try:
        response = requests.get(
            "https://punjab-rozgar-api.onrender.com/health",
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            health = response.json()
            print(f"   ✅ API Status: {health.get('status', 'unknown')}")
        else:
            print(f"   ❌ Health check failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Health check exception: {e}")

def show_enum_values():
    """Show the expected enum values from Python models"""
    print("\n📖 Expected Enum Values:")
    print("=" * 30)
    
    # These should match the Python model definitions
    enum_values = {
        "JobType": ["full_time", "part_time", "contract", "temporary", "internship", "freelance"],
        "JobStatus": ["draft", "pending_approval", "active", "paused", "closed", "expired"],
        "UserRole": ["job_seeker", "employer", "admin", "moderator"],
        "AccountStatus": ["active", "inactive", "suspended", "pending_verification"],
        "EmployerType": ["government", "public_sector", "private", "ngo", "startup"]
    }
    
    for enum_name, values in enum_values.items():
        print(f"   {enum_name}: {', '.join(values)}")

if __name__ == "__main__":
    print("🔧 Production Enum Testing & Debugging")
    print("=" * 50)
    
    check_api_health()
    show_enum_values()
    test_production_job_creation()
    
    print("\n💡 Next Steps:")
    print("1. If tests fail, the production database needs enum fixes")
    print("2. Run the enum fix script on the production database")
    print("3. Redeploy the backend with any necessary updates")
    print("4. Test again to verify the fix")