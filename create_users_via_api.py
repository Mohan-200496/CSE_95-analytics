"""
Create demo users via API calls to the production backend
"""
import asyncio
import aiohttp
import json

# API base URL for production
API_BASE_URL = "https://punjab-rozgar-api.onrender.com/api/v1"

async def create_demo_users():
    """Create demo users via API calls"""
    
    demo_users = [
        {
            'email': 'admin@punjabrozgar.gov.pk',
            'password': 'admin123',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'job_seeker'  # Will manually promote to admin later
        },
        {
            'email': 'employer@company.com',
            'password': 'employer123',
            'first_name': 'Employer',
            'last_name': 'Demo',
            'role': 'employer'
        },
        {
            'email': 'jobseeker@email.com',
            'password': 'jobseeker123',
            'first_name': 'Job',
            'last_name': 'Seeker',
            'role': 'job_seeker'
        }
    ]
    
    print("🚀 Creating demo users via API...")
    
    async with aiohttp.ClientSession() as session:
        for user_data in demo_users:
            try:
                # Register user
                register_url = f"{API_BASE_URL}/auth/register"
                
                async with session.post(register_url, json=user_data) as response:
                    if response.status == 200:
                        print(f"✅ Created user: {user_data['email']} ({user_data['role']})")
                    elif response.status == 400:
                        result = await response.json()
                        if "already exists" in result.get("message", "").lower():
                            print(f"ℹ️  User already exists: {user_data['email']}")
                        else:
                            print(f"❌ Error creating {user_data['email']}: {result.get('message', 'Unknown error')}")
                    else:
                        result = await response.json() if response.content_type == 'application/json' else await response.text()
                        print(f"❌ Failed to create {user_data['email']}: {response.status} - {result}")
                        
            except Exception as e:
                print(f"❌ Error creating user {user_data['email']}: {str(e)}")
    
    print("\n🎉 Demo user creation complete!")
    print("\n📋 Demo Login Credentials:")
    print("👨‍💼 Admin: admin@punjabrozgar.gov.pk / admin123")
    print("🏢 Employer: employer@company.com / employer123")  
    print("👤 Job Seeker: jobseeker@email.com / jobseeker123")

if __name__ == "__main__":
    asyncio.run(create_demo_users())