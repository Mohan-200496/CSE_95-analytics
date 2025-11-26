#!/usr/bin/env python3
"""
Final System Verification - Punjab Rozgar Portal
Tests all core functionality and role-based access
"""

import requests
import json
import time

# API Base URL
BASE_URL = "https://punjab-rozgar-api.onrender.com/api/v1"

# Test credentials
test_users = {
    "admin": {"email": "admin@test.com", "password": "admin123"},
    "employer": {"email": "employer@test.com", "password": "employer123"},
    "jobseeker": {"email": "jobseeker@test.com", "password": "jobseeker123"},
    "company": {"email": "company@test.com", "password": "company123"}
}

def make_request(method, url, headers=None, json_data=None):
    """Make HTTP request with error handling"""
    try:
        response = requests.request(method, url, headers=headers, json=json_data, timeout=30)
        return response
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return None

def test_authentication():
    """Test authentication for all user types"""
    print("🔐 Testing Authentication...")
    auth_tokens = {}
    
    for role, creds in test_users.items():
        print(f"  Testing {role} login...")
        response = make_request("POST", f"{BASE_URL}/auth/login", json_data=creds)
        
        if response and response.status_code == 200:
            data = response.json()
            auth_tokens[role] = data.get("access_token")
            user_role = data.get("user", {}).get("role", "unknown")
            print(f"    ✅ {role} login successful (role: {user_role})")
        else:
            status = response.status_code if response else "No response"
            print(f"    ❌ {role} login failed (status: {status})")
            
    return auth_tokens

def test_job_recommendations(tokens):
    """Test job recommendations - should only work for job seekers"""
    print("\n📋 Testing Job Recommendations...")
    
    for role, token in tokens.items():
        if not token:
            continue
            
        headers = {"Authorization": f"Bearer {token}"}
        response = make_request("GET", f"{BASE_URL}/recommendations", headers=headers)
        
        if role == "jobseeker":
            if response and response.status_code == 200:
                data = response.json()
                job_count = len(data.get("recommendations", []))
                print(f"    ✅ Job seeker got {job_count} recommendations")
            else:
                print(f"    ❌ Job seeker should get recommendations (status: {response.status_code if response else 'No response'})")
        else:
            if response and response.status_code == 403:
                print(f"    ✅ {role} correctly denied access to recommendations")
            else:
                status = response.status_code if response else "No response"
                print(f"    ⚠️  {role} got unexpected response (status: {status}) - should be 403")

def test_admin_functions(tokens):
    """Test admin-only functions"""
    print("\n⚙️ Testing Admin Functions...")
    
    admin_token = tokens.get("admin")
    if not admin_token:
        print("    ❌ No admin token available")
        return
        
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test pending jobs
    response = make_request("GET", f"{BASE_URL}/admin/jobs/pending", headers=headers)
    if response and response.status_code == 200:
        data = response.json()
        pending_count = len(data.get("jobs", []))
        print(f"    ✅ Admin can view {pending_count} pending jobs")
    else:
        status = response.status_code if response else "No response"
        print(f"    ❌ Admin cannot access pending jobs (status: {status})")
    
    # Test with non-admin user
    jobseeker_token = tokens.get("jobseeker")
    if jobseeker_token:
        headers = {"Authorization": f"Bearer {jobseeker_token}"}
        response = make_request("GET", f"{BASE_URL}/admin/jobs/pending", headers=headers)
        if response and response.status_code == 403:
            print("    ✅ Job seeker correctly denied admin access")
        else:
            status = response.status_code if response else "No response"
            print(f"    ⚠️  Job seeker got unexpected admin access (status: {status})")

def test_job_creation(tokens):
    """Test job creation by employers"""
    print("\n💼 Testing Job Creation...")
    
    employer_token = tokens.get("employer")
    if not employer_token:
        print("    ❌ No employer token available")
        return
        
    headers = {"Authorization": f"Bearer {employer_token}"}
    
    # Create test job
    job_data = {
        "title": "Test Software Developer",
        "description": "A test job posting for verification",
        "company_name": "Test Company",
        "location": "Test Location",
        "job_type": "full_time",
        "salary_range": "50000-70000",
        "required_skills": ["Python", "Testing"],
        "experience_level": "mid"
    }
    
    response = make_request("POST", f"{BASE_URL}/jobs/", headers=headers, json_data=job_data)
    if response and response.status_code == 201:
        data = response.json()
        print(f"    ✅ Employer created job: {data.get('title', 'Unknown')}")
        return data.get("id")
    else:
        status = response.status_code if response else "No response"
        print(f"    ❌ Job creation failed (status: {status})")
        return None

def test_api_health():
    """Test basic API health"""
    print("\n🏥 Testing API Health...")
    
    # Test health endpoint
    response = make_request("GET", f"{BASE_URL}/health")
    if response and response.status_code == 200:
        print("    ✅ API health check passed")
    else:
        status = response.status_code if response else "No response"
        print(f"    ❌ API health check failed (status: {status})")
    
    # Test root endpoint
    response = make_request("GET", f"{BASE_URL}/")
    if response and response.status_code == 200:
        print("    ✅ API root endpoint accessible")
    else:
        status = response.status_code if response else "No response"
        print(f"    ❌ API root endpoint failed (status: {status})")

def main():
    """Run complete system verification"""
    print("🚀 Punjab Rozgar Portal - Final System Verification")
    print("=" * 60)
    
    # Test API health first
    test_api_health()
    
    # Test authentication
    tokens = test_authentication()
    
    if not tokens:
        print("\n❌ No authentication tokens obtained. Stopping verification.")
        return
    
    # Test role-based access
    test_job_recommendations(tokens)
    test_admin_functions(tokens)
    test_job_creation(tokens)
    
    print("\n" + "=" * 60)
    print("🎯 Verification Complete!")
    
    # Summary
    working_auths = sum(1 for token in tokens.values() if token)
    print(f"📊 Summary: {working_auths}/{len(test_users)} authentication methods working")
    
    if working_auths == len(test_users):
        print("✅ All systems operational!")
    else:
        print("⚠️  Some issues detected - check logs above")

if __name__ == "__main__":
    main()