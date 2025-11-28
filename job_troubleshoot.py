#!/usr/bin/env python3
"""
Job Troubleshooting Script for Punjab Rozgar Portal
Helps diagnose and fix job posting issues
"""

import requests
import json

def login_as_employer():
    """Login as employer to check their jobs"""
    login_data = {
        "email": "employer@test.com", 
        "password": "employer123"
    }
    
    response = requests.post(
        "https://punjab-rozgar-api.onrender.com/api/v1/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"❌ Employer login failed: {response.status_code} - {response.text}")
        return None

def check_employer_jobs(token):
    """Check all jobs posted by the employer"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try different possible endpoints
    endpoints_to_try = [
        "https://punjab-rozgar-api.onrender.com/api/v1/jobs/employer",
        "https://punjab-rozgar-api.onrender.com/api/v1/employer/jobs",
        "https://punjab-rozgar-api.onrender.com/api/v1/jobs/my-jobs"
    ]
    
    for endpoint in endpoints_to_try:
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"📋 Employer Jobs from {endpoint}:")
            print(f"   Total jobs: {len(data.get('jobs', []))}")
            
            for job in data.get('jobs', []):
                status = job.get('status', 'unknown')
                print(f"   • {job.get('title', 'No Title')} (Status: {status})")
            return data
        else:
            print(f"❌ {endpoint}: {response.status_code}")
    
    return None
    """Login as admin to get access token"""
    login_data = {
        "email": "admin@test.com", 
        "password": "admin123"
    }
    
    response = requests.post(
        "https://punjab-rozgar-api.onrender.com/api/v1/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"❌ Admin login failed: {response.status_code} - {response.text}")
        return None

def check_pending_jobs(token):
    """Check for jobs pending approval"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        "https://punjab-rozgar-api.onrender.com/api/v1/admin/jobs/pending-approval",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"📋 Pending Jobs: {data['total_count']}")
        
        if data['total_count'] > 0:
            for job in data['jobs']:
                print(f"  • {job['title']} by {job['employer_name']} (ID: {job['job_id']})")
        return data
    else:
        print(f"❌ Failed to get pending jobs: {response.status_code}")
        return None

def approve_all_pending_jobs(token):
    """Approve all pending jobs"""
    # First get pending jobs
    pending = check_pending_jobs(token)
    
    if not pending or pending['total_count'] == 0:
        print("✅ No pending jobs to approve")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    for job in pending['jobs']:
        job_id = job['job_id']
        print(f"🔄 Approving job: {job['title']}")
        
        # Approve the job
        response = requests.post(
            f"https://punjab-rozgar-api.onrender.com/api/v1/admin/jobs/{job_id}/approve",
            headers=headers
        )
        
        if response.status_code == 200:
            print(f"✅ Approved: {job['title']}")
        else:
            print(f"❌ Failed to approve {job['title']}: {response.status_code}")

def check_all_jobs():
    """Check all published jobs (no auth required)"""
    response = requests.get("https://punjab-rozgar-api.onrender.com/api/v1/jobs/")
    
    if response.status_code == 200:
        data = response.json()
        print(f"🌐 Published Jobs: {len(data.get('jobs', []))}")
        
        for job in data.get('jobs', []):
            print(f"  • {job['title']} by {job['employer_name']} (Status: {job.get('status', 'unknown')})")
        return data
    else:
        print(f"❌ Failed to get published jobs: {response.status_code}")
        return None

def main():
    print("🔍 Punjab Rozgar Portal - Job Troubleshooting")
    print("=" * 50)
    
    # Check published jobs first
    print("\n1. Checking published jobs...")
    published_jobs = check_all_jobs()
    
    # Login as employer to check their posted jobs
    print("\n2. Checking employer's posted jobs...")
    employer_token = login_as_employer()
    if employer_token:
        employer_jobs = check_employer_jobs(employer_token)
    
    # Login as admin
    print("\n3. Logging in as admin...")
    admin_token = login_as_admin()
    
    if not admin_token:
        print("❌ Cannot proceed without admin access")
        return
    
    # Check pending jobs
    print("\n4. Checking pending jobs...")
    pending_jobs = check_pending_jobs(admin_token)
    
    # Auto-approve if there are pending jobs
    if pending_jobs and pending_jobs['total_count'] > 0:
        print("\n5. Auto-approving pending jobs...")
        approve_all_pending_jobs(admin_token)
        
        print("\n6. Checking published jobs again...")
        check_all_jobs()
    else:
        print("\n✅ No pending jobs found")
    
    print("\n📋 Troubleshooting Summary:")
    print("• If your job was found in employer jobs: Check the status")
    print("• If your job was found in pending: It's now approved!")
    print("• If your job was found in published: Check your job search filters")  
    print("• If your job wasn't found anywhere: Try posting again")

if __name__ == "__main__":
    main()