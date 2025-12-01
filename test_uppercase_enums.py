#!/usr/bin/env python3
"""
Updated production enum testing with UPPERCASE values
"""

import requests
import json

# API base URL
BASE_URL = "https://cse-95-analytics.onrender.com"

def test_production_uppercase():
    """Test job creation with UPPERCASE enum values"""
    print("🔧 Production UPPERCASE Enum Testing")
    print("=" * 50)
    
    # Check API health first
    print("🏥 Checking API Health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print(f"   Status: {response.status_code}")
            print("   ✅ API Status: healthy")
        else:
            print(f"   ❌ API Health failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ API Health error: {e}")
        return
    
    # Test cases with UPPERCASE values to match production database
    test_cases = [
        {
            "title": "Test Job - FULL_TIME",
            "description": "Testing with FULL_TIME enum value",
            "job_type": "FULL_TIME",
            "category": "Technology", 
            "location_city": "Chandigarh",
            "requirements": "Testing uppercase enum compatibility",
            "company_name": "Test Company",
            "contact_email": "test@example.com",
            "salary_min": 50000,
            "salary_max": 75000
        },
        {
            "title": "Test Job - PART_TIME",
            "description": "Testing with PART_TIME enum value",
            "job_type": "PART_TIME",
            "category": "Engineering",
            "location_city": "Lahore", 
            "requirements": "Testing uppercase enum compatibility",
            "company_name": "Test Company PT",
            "contact_email": "test_pt@example.com",
            "salary_min": 30000,
            "salary_max": 50000
        },
        {
            "title": "Test Job - CONTRACT",
            "description": "Testing with CONTRACT enum value", 
            "job_type": "CONTRACT",
            "category": "Marketing",
            "location_city": "Multan",
            "requirements": "Testing uppercase enum compatibility",
            "company_name": "Test Company Contract",
            "contact_email": "test_contract@example.com",
            "salary_min": 60000,
            "salary_max": 80000
        }
    ]
    
    print("\n🧪 Testing Production Job Creation with UPPERCASE Values")
    print("=" * 60)
    
    success_count = 0
    
    for i, test_data in enumerate(test_cases, 1):
        print(f"\n🔍 Test Case {i}: {test_data['job_type']}")
        
        try:
            # Test the no-auth endpoint
            response = requests.post(f"{BASE_URL}/api/v1/jobs/create-no-auth", 
                                   json=test_data, 
                                   timeout=30)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"   ✅ Success: Job created with ID {result.get('job_id', 'Unknown')}")
                    success_count += 1
                else:
                    print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
                    
            elif response.status_code == 422:
                print(f"   ❌ Validation Error: {response.json()}")
            else:
                try:
                    error_data = response.json()
                    print(f"   ❌ Failed: {error_data}")
                except:
                    print(f"   ❌ Failed: {response.text}")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test job listing
    print(f"\n📋 Testing Job Listing...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/jobs/", timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            jobs = response.json()
            print(f"   📊 Found {len(jobs)} jobs")
            if jobs:
                print(f"   📋 Recent job: {jobs[0].get('title', 'Unknown')}")
        else:
            print(f"   ❌ Listing failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Listing error: {e}")
    
    print(f"\n💡 Summary:")
    print(f"   ✅ Successful job creations: {success_count}/{len(test_cases)}")
    if success_count == len(test_cases):
        print("   🎉 All tests passed! UPPERCASE enum values work correctly.")
    else:
        print("   ⚠️  Some tests failed. Check logs for details.")

if __name__ == "__main__":
    test_production_uppercase()