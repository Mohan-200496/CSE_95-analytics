"""
Comprehensive test of role-based functionality and job approval workflow
"""
import asyncio
import aiohttp

API_BASE_URL = "https://punjab-rozgar-api.onrender.com/api/v1"

async def test_role_functionality():
    """Test all role-based functionality"""
    
    print("🧪 Testing Punjab Rozgar Portal Role-Based Functionality\n")
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Login with different roles
        print("1️⃣ Testing Role-Based Authentication:")
        roles_to_test = [
            {"email": "admin@punjabrozgar.gov.pk", "password": "admin123", "expected": "admin"},
            {"email": "employer@company.com", "password": "employer123", "expected": "employer"},
            {"email": "jobseeker@email.com", "password": "jobseeker123", "expected": "job_seeker"}
        ]
        
        for user in roles_to_test:
            try:
                async with session.post(f"{API_BASE_URL}/auth/login", json={
                    "email": user["email"], "password": user["password"]
                }) as response:
                    if response.status == 200:
                        result = await response.json()
                        actual_role = result.get("user", {}).get("role")
                        print(f"   ✅ {user['email']}: {actual_role} (expected: {user['expected']})")
                    else:
                        print(f"   ❌ {user['email']}: Login failed")
            except Exception as e:
                print(f"   ❌ {user['email']}: Error - {e}")
        
        # Test 2: Admin functionality - get pending jobs
        print("\n2️⃣ Testing Admin Job Approval Functionality:")
        try:
            # Login as admin first
            admin_login = await session.post(f"{API_BASE_URL}/auth/login", json={
                "email": "admin@punjabrozgar.gov.pk", "password": "admin123"
            })
            if admin_login.status == 200:
                admin_data = await admin_login.json()
                admin_token = admin_data.get("access_token")
                
                # Test pending jobs endpoint
                headers = {"Authorization": f"Bearer {admin_token}"}
                async with session.get(f"{API_BASE_URL}/admin/jobs/pending-approval", headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        job_count = len(result.get("jobs", []))
                        print(f"   ✅ Admin can access pending jobs: {job_count} jobs found")
                    else:
                        print(f"   ⚠️  Pending jobs endpoint: {response.status}")
                
                # Test admin stats
                async with session.get(f"{API_BASE_URL}/admin/stats", headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"   ✅ Admin stats accessible: {result.get('total_users', 0)} users")
                    else:
                        print(f"   ❌ Admin stats failed: {response.status}")
        except Exception as e:
            print(f"   ❌ Admin functionality test error: {e}")
        
        # Test 3: Employer functionality
        print("\n3️⃣ Testing Employer Job Management:")
        try:
            # Login as employer
            emp_login = await session.post(f"{API_BASE_URL}/auth/login", json={
                "email": "employer@company.com", "password": "employer123"
            })
            if emp_login.status == 200:
                emp_data = await emp_login.json()
                emp_token = emp_data.get("access_token")
                headers = {"Authorization": f"Bearer {emp_token}"}
                
                # Test job creation
                test_job = {
                    "title": "Test Software Developer Position",
                    "description": "Test job description for role testing",
                    "requirements": "Testing requirements",
                    "responsibilities": "Testing responsibilities",
                    "job_type": "full_time",
                    "category": "Technology",
                    "location_city": "Lahore",
                    "salary_min": 50000,
                    "salary_max": 80000,
                    "experience_min": 2,
                    "experience_max": 5,
                    "contact_email": "hr@company.com"
                }
                
                async with session.post(f"{API_BASE_URL}/jobs/", json=test_job, headers=headers) as response:
                    if response.status == 200:
                        job_result = await response.json()
                        job_id = job_result.get("job_id")
                        print(f"   ✅ Employer can create jobs: {job_id}")
                        
                        # Test job publishing (should set to pending approval)
                        if job_id:
                            async with session.put(f"{API_BASE_URL}/jobs/{job_id}/publish", headers=headers) as pub_response:
                                if pub_response.status == 200:
                                    pub_result = await pub_response.json()
                                    status = pub_result.get("status")
                                    print(f"   ✅ Job published for approval: Status = {status}")
                                else:
                                    print(f"   ⚠️  Job publish failed: {pub_response.status}")
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Job creation failed: {response.status} - {error_text[:100]}")
        except Exception as e:
            print(f"   ❌ Employer functionality test error: {e}")
        
        # Test 4: Job seeker restrictions
        print("\n4️⃣ Testing Job Seeker Access Controls:")
        try:
            # Login as job seeker
            js_login = await session.post(f"{API_BASE_URL}/auth/login", json={
                "email": "jobseeker@email.com", "password": "jobseeker123"
            })
            if js_login.status == 200:
                js_data = await js_login.json()
                js_token = js_data.get("access_token")
                headers = {"Authorization": f"Bearer {js_token}"}
                
                # Test that job seeker can't access admin endpoints
                async with session.get(f"{API_BASE_URL}/admin/stats", headers=headers) as response:
                    if response.status == 403:
                        print("   ✅ Job seeker correctly blocked from admin endpoints")
                    else:
                        print(f"   ⚠️  Job seeker admin access: {response.status}")
                
                # Test that job seeker CAN access public job endpoints
                async with session.get(f"{API_BASE_URL}/jobs/", headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"   ✅ Job seeker can browse jobs: {len(result)} jobs available")
                    else:
                        print(f"   ❌ Job seeker job browse failed: {response.status}")
        except Exception as e:
            print(f"   ❌ Job seeker test error: {e}")
        
        print(f"\n🎯 Role-Based Functionality Test Complete!")
        print(f"\n🌐 Test your portal with role-based access at:")
        print(f"   https://punjab-rozgar-portal1.onrender.com")
        print(f"\n📋 Login Credentials:")
        print(f"   👨‍💼 Admin: admin@punjabrozgar.gov.pk / admin123")
        print(f"   🏢 Employer: employer@company.com / employer123")  
        print(f"   👤 Job Seeker: jobseeker@email.com / jobseeker123")

if __name__ == "__main__":
    asyncio.run(test_role_functionality())