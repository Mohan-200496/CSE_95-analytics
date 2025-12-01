#!/usr/bin/env python3
"""
Check actual database schema and test job creation via API
"""

import sqlite3
import requests
import json

def check_jobs_table_schema():
    """Check the actual jobs table schema"""
    print("📋 Jobs Table Schema")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('dev_punjab_rozgar.db')
        cursor = conn.cursor()
        
        # Get table schema
        cursor.execute("PRAGMA table_info(jobs);")
        columns = cursor.fetchall()
        
        print("Jobs table columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
        
        # Get existing job data
        cursor.execute("SELECT * FROM jobs LIMIT 1;")
        job = cursor.fetchone()
        if job:
            print(f"\nExample job data:")
            for i, col in enumerate(columns):
                value = job[i] if i < len(job) else "NULL"
                print(f"  {col[1]}: {value}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_api_endpoints():
    """Test job creation via API"""
    print("\n🧪 Testing Job Creation API")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test job listing
    try:
        response = requests.get(f"{base_url}/api/v1/jobs/", timeout=5)
        print(f"Job listing: {response.status_code}")
        if response.status_code == 200:
            jobs = response.json()
            print(f"  📊 Found {len(jobs)} jobs")
            if jobs:
                print(f"  📋 First job: {jobs[0].get('title', 'N/A')}")
        else:
            print(f"  ❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Job listing failed: {e}")
    
    # Test job creation
    job_data = {
        "title": "API Test Developer",
        "description": "Testing job creation via API",
        "requirements": "Testing skills",
        "job_type": "full_time",
        "experience_level": "mid",
        "company_name": "API Test Company",
        "contact_email": "test@apitest.com",
        "salary_min": 60000,
        "salary_max": 90000
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/jobs/test-create",
            json=job_data,
            timeout=10
        )
        print(f"Job creation: {response.status_code}")
        print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Job creation failed: {e}")

if __name__ == "__main__":
    check_jobs_table_schema()
    test_api_endpoints()