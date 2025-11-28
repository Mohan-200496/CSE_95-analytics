"""
Simple demo account creation script using raw SQL
This bypasses potential SQLAlchemy model issues
"""

import requests
import json

def create_demo_accounts_via_registration():
    """Create demo accounts using the registration endpoint"""
    
    base_url = "https://punjab-rozgar-api.onrender.com/api/v1"
    
    # Demo accounts to create
    demo_accounts = [
        {
            "email": "admin@test.com",
            "password": "admin123", 
            "first_name": "Admin",
            "last_name": "User",
            "phone": "+1234567890",
            "user_type": "admin"
        },
        {
            "email": "employer@test.com",
            "password": "employer123",
            "first_name": "Test", 
            "last_name": "Employer",
            "phone": "+1234567891",
            "user_type": "employer"
        },
        {
            "email": "jobseeker@email.com",
            "password": "jobseeker123",
            "first_name": "Test",
            "last_name": "JobSeeker", 
            "phone": "+1234567892",
            "user_type": "jobseeker"
        }
    ]
    
    print("🚀 Creating demo accounts via registration endpoint...")
    
    for account in demo_accounts:
        try:
            print(f"Creating {account['user_type']}: {account['email']}")
            
            response = requests.post(
                f"{base_url}/auth/register",
                json=account,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ {account['email']} created successfully")
            elif response.status_code == 422:
                # Check if it's because user already exists
                error_data = response.json()
                if "already exists" in str(error_data).lower():
                    print(f"ℹ️ {account['email']} already exists")
                else:
                    print(f"❌ {account['email']} validation error: {error_data}")
            else:
                print(f"❌ {account['email']} failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error creating {account['email']}: {e}")
    
    print("\n🎉 Demo account creation completed!")
    print("📋 Try logging in with:")
    print("   👨‍💼 Admin: admin@test.com / admin123")
    print("   🏢 Employer: employer@test.com / employer123")
    print("   👤 Job Seeker: jobseeker@email.com / jobseeker123")

if __name__ == "__main__":
    create_demo_accounts_via_registration()