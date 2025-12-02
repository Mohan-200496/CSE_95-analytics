#!/usr/bin/env python3
"""
Quick test to verify job creation and visibility in dashboards
"""

import requests
import json
import time

API_BASE_URL = "https://punjab-rozgar-api.onrender.com/api/v1"

def test_job_creation_and_visibility():
    """Test job creation and check if it appears in both dashboards"""
    
    print("🧪 Testing Job Creation and Dashboard Visibility")
    print("=" * 60)
    
    # Step 1: Login as employer
    print("\n1️⃣ Logging in as employer...")
    
    login_data = {
        "email": "employer@test.com",
        "password": "test123"
    }
    
    try:
        login_response = requests.post(f"{API_BASE_URL}/auth/login", json=login_data)
        if login_response.status_code == 200:
            login_result = login_response.json()
            emp_token = login_result.get("access_token")
            emp_headers = {"Authorization": f"Bearer {emp_token}"}
            print("   ✅ Employer logged in successfully")
        else:
            print(f"   ❌ Employer login failed: {login_response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Employer login error: {e}")
        return
    
    # Step 2: Create a new job
    print("\n2️⃣ Creating a new job...")
    
    timestamp = int(time.time())
    test_job = {
        "title": f"Dashboard Test Job {timestamp}",
        "description": "Test job to verify dashboard visibility",
        "requirements": "Testing requirements",
        "responsibilities": "Testing responsibilities",
        "job_type": "full_time",
        "category": "Technology",
        "location_city": "Chandigarh",
        "salary_min": 50000,
        "salary_max": 75000,
        "contact_email": "test@company.com"
    }
    
    try:
        create_response = requests.post(f"{API_BASE_URL}/jobs/", json=test_job, headers=emp_headers)
        if create_response.status_code == 200:
            job_result = create_response.json()
            job_id = job_result.get("job_id")
            print(f"   ✅ Job created successfully! ID: {job_id}")
        else:
            print(f"   ❌ Job creation failed: {create_response.status_code}")
            print(f"   Response: {create_response.text}")
            return
    except Exception as e:
        print(f"   ❌ Job creation error: {e}")
        return
    
    # Step 3: Check if job appears in employer's my-jobs
    print("\n3️⃣ Checking employer dashboard (my-jobs)...")
    
    try:
        my_jobs_response = requests.get(f"{API_BASE_URL}/jobs/my-jobs", headers=emp_headers)
        if my_jobs_response.status_code == 200:
            my_jobs = my_jobs_response.json()
            found_job = any(job.get("job_id") == job_id for job in my_jobs)
            print(f"   📊 Total employer jobs: {len(my_jobs)}")
            if found_job:
                print("   ✅ Job appears in employer dashboard")
            else:
                print("   ❌ Job NOT found in employer dashboard")
                print(f"   🔍 Looking for job_id: {job_id}")
                for job in my_jobs[:3]:
                    print(f"      Found: {job.get('job_id')} - {job.get('title')}")
        else:
            print(f"   ❌ My-jobs endpoint failed: {my_jobs_response.status_code}")
    except Exception as e:
        print(f"   ❌ My-jobs check error: {e}")
    
    # Step 4: Check if job appears in public jobs list
    print("\n4️⃣ Checking public jobs endpoint...")
    
    try:
        public_jobs_response = requests.get(f"{API_BASE_URL}/jobs/")
        if public_jobs_response.status_code == 200:
            public_jobs = public_jobs_response.json()
            found_job = any(job.get("job_id") == job_id for job in public_jobs)
            print(f"   📊 Total public jobs: {len(public_jobs)}")
            if found_job:
                print("   ✅ Job appears in public jobs list")
            else:
                print("   ❌ Job NOT found in public jobs list")
        else:
            print(f"   ❌ Public jobs endpoint failed: {public_jobs_response.status_code}")
    except Exception as e:
        print(f"   ❌ Public jobs check error: {e}")
    
    # Step 5: Try to login as admin and check admin dashboard
    print("\n5️⃣ Checking admin dashboard...")
    
    admin_login_data = {
        "email": "admin@test.com", 
        "password": "admin123"
    }
    
    try:
        admin_login_response = requests.post(f"{API_BASE_URL}/auth/login", json=admin_login_data)
        if admin_login_response.status_code == 200:
            admin_result = admin_login_response.json()
            admin_token = admin_result.get("access_token")
            admin_headers = {"Authorization": f"Bearer {admin_token}"}
            print("   ✅ Admin logged in successfully")
            
            # Check admin jobs endpoint
            admin_jobs_response = requests.get(f"{API_BASE_URL}/admin/jobs", headers=admin_headers)
            if admin_jobs_response.status_code == 200:
                admin_jobs = admin_jobs_response.json()
                found_job = any(job.get("job_id") == job_id for job in admin_jobs)
                print(f"   📊 Total admin jobs: {len(admin_jobs)}")
                if found_job:
                    print("   ✅ Job appears in admin dashboard")
                else:
                    print("   ❌ Job NOT found in admin dashboard")
            else:
                print(f"   ❌ Admin jobs endpoint failed: {admin_jobs_response.status_code}")
                print(f"   Response: {admin_jobs_response.text}")
        else:
            print(f"   ❌ Admin login failed: {admin_jobs_response.status_code}")
    except Exception as e:
        print(f"   ❌ Admin check error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")

if __name__ == "__main__":
    test_job_creation_and_visibility()