#!/usr/bin/env python3
"""
Comprehensive test of job creation functionality
"""

import requests
import json
import time
import sqlite3

def wait_for_server():
    """Wait for server to be ready"""
    print("⏳ Waiting for server to start...")
    for i in range(10):
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server is ready!")
                return True
        except:
            time.sleep(1)
            print(f"   Waiting... ({i+1}/10)")
    return False

def test_health_endpoint():
    """Test health endpoint"""
    print("\n📊 Testing Health Endpoint")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_job_listing():
    """Test job listing endpoint"""
    print("\n📋 Testing Job Listing")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:8000/api/v1/jobs/", timeout=5)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            jobs = response.json()
            print(f"✅ Found {len(jobs)} jobs")
            for i, job in enumerate(jobs[:3]):  # Show first 3 jobs
                print(f"  {i+1}. {job.get('title', 'N/A')} - {job.get('company_name', 'N/A')}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Job listing failed: {e}")
        return False

def test_job_creation():
    """Test job creation via API"""
    print("\n🆕 Testing Job Creation")
    print("=" * 40)
    
    # Test job data
    job_data = {
        "title": "Senior Full Stack Developer",
        "description": "We are looking for an experienced full stack developer to join our team. You will work on exciting projects using modern technologies.",
        "requirements": "5+ years experience with Python, React, PostgreSQL. Experience with FastAPI preferred.",
        "job_type": "full_time",
        "experience_level": "senior",
        "company_name": "Punjab Tech Solutions",
        "contact_email": "careers@punjabtechsolutions.com",
        "salary_min": 80000,
        "salary_max": 120000,
        "location": "Chandigarh, Punjab"
    }
    
    try:
        # Test the no-auth endpoint first
        print("Testing no-auth endpoint...")
        response = requests.post(
            "http://localhost:8000/api/v1/jobs/test-create",
            json=job_data,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:300]}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Job created successfully!")
                job_id = result.get('job_id')
                print(f"   Job ID: {job_id}")
                return job_id
            else:
                print(f"❌ Job creation failed: {result.get('message', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error {response.status_code}")
            
        return None
        
    except Exception as e:
        print(f"❌ Job creation request failed: {e}")
        return None

def verify_job_in_database(job_id=None):
    """Verify job was saved to database"""
    print("\n💾 Verifying Database")
    print("=" * 40)
    
    try:
        # Check which database file has data
        db_files = ['dev_punjab_rozgar.db', 'punjab_rozgar.db']
        active_db = None
        
        for db_file in db_files:
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM jobs")
                count = cursor.fetchone()[0]
                if count > 0:
                    active_db = db_file
                    break
                conn.close()
            except:
                continue
        
        if not active_db:
            print("❌ No active database found")
            return False
        
        print(f"📁 Using database: {active_db}")
        
        conn = sqlite3.connect(active_db)
        cursor = conn.cursor()
        
        # Get total job count
        cursor.execute("SELECT COUNT(*) FROM jobs")
        total_jobs = cursor.fetchone()[0]
        print(f"📊 Total jobs in database: {total_jobs}")
        
        # Get recent jobs
        cursor.execute("""
            SELECT job_id, title, company_name, job_type, created_at 
            FROM jobs 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        recent_jobs = cursor.fetchall()
        print(f"📋 Recent jobs:")
        for job in recent_jobs:
            print(f"  - {job[1]} ({job[2]}) - {job[3]} - {job[0]}")
        
        # If we have a specific job_id to check
        if job_id:
            cursor.execute("SELECT title FROM jobs WHERE job_id = ?", (job_id,))
            job = cursor.fetchone()
            if job:
                print(f"✅ Newly created job found: {job[0]}")
            else:
                print(f"❌ Job {job_id} not found in database")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

def test_job_visibility():
    """Test that jobs appear in listings after creation"""
    print("\n👀 Testing Job Visibility")
    print("=" * 40)
    
    try:
        # Get initial count
        response = requests.get("http://localhost:8000/api/v1/jobs/", timeout=5)
        if response.status_code != 200:
            print(f"❌ Failed to get job listing: {response.status_code}")
            return False
        
        initial_jobs = response.json()
        initial_count = len(initial_jobs)
        print(f"📊 Jobs before creation: {initial_count}")
        
        # Create a test job
        job_id = test_job_creation()
        if not job_id:
            return False
        
        # Wait a moment for database sync
        time.sleep(2)
        
        # Get updated count
        response = requests.get("http://localhost:8000/api/v1/jobs/", timeout=5)
        if response.status_code != 200:
            print(f"❌ Failed to get updated job listing: {response.status_code}")
            return False
        
        updated_jobs = response.json()
        updated_count = len(updated_jobs)
        print(f"📊 Jobs after creation: {updated_count}")
        
        if updated_count > initial_count:
            print("✅ Job visibility confirmed - new job appears in listing!")
            
            # Find our job
            for job in updated_jobs:
                if job.get('job_id') == job_id:
                    print(f"✅ Found our job: {job.get('title')}")
                    break
            else:
                print("⚠️ Job count increased but our specific job not found")
            
            return True
        else:
            print("❌ Job count did not increase")
            return False
            
    except Exception as e:
        print(f"❌ Visibility test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all tests"""
    print("🧪 COMPREHENSIVE JOB CREATION TEST")
    print("=" * 50)
    
    # Wait for server
    if not wait_for_server():
        print("❌ Server not available")
        return False
    
    # Run tests
    tests = [
        ("Health Check", test_health_endpoint),
        ("Job Listing", test_job_listing),
        ("Database Verification", lambda: verify_job_in_database()),
        ("Job Visibility", test_job_visibility)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📈 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - JOB CREATION IS WORKING!")
    elif passed > total // 2:
        print("⚠️ MOSTLY WORKING - Some issues to investigate")
    else:
        print("❌ MAJOR ISSUES - Job creation needs attention")
    
    return passed == total

if __name__ == "__main__":
    run_comprehensive_test()