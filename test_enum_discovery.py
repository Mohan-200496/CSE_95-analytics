#!/usr/bin/env python3
"""
Test what enum values are actually in the production database
"""

import requests
import json

# API base URL
BASE_URL = "https://cse-95-analytics.onrender.com"

def test_enum_discovery():
    """Try to discover what enum values are accepted"""
    print("🔍 Production Enum Value Discovery")
    print("=" * 40)
    
    # Test different possible UserRole values
    test_roles = [
        'job_seeker', 'jobseeker', 'admin', 'moderator', 
        'ADMIN', 'JOBSEEKER', 'EMPLOYER', 'employer'
    ]
    
    for role in test_roles:
        print(f"\n🧪 Testing UserRole: '{role}'")
        
        # Try to create a user with this role first
        user_data = {
            "email": f"test_{role}@test.com",
            "password": "Test123!@#",
            "first_name": "Test",
            "last_name": "User",
            "role": role,
            "phone": "1234567890"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/v1/auth/register", 
                                   json=user_data, 
                                   timeout=30)
            print(f"   Register Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"   ✅ UserRole '{role}' is VALID")
                else:
                    print(f"   ❌ UserRole '{role}' failed: {result.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ UserRole '{role}' failed with status {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error testing UserRole '{role}': {e}")
    
    print(f"\n🔍 Production Database Enum Investigation Complete")

if __name__ == "__main__":
    test_enum_discovery()