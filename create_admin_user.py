#!/usr/bin/env python3
"""
Create admin user for the Punjab Rozgar Portal
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.database import get_db
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession

async def create_admin_user():
    """Create admin user with admin@test.com credentials"""
    
    try:
        # Get database session
        async for db in get_db():
            session: AsyncSession = db
            
            # Check if admin user already exists
            from sqlalchemy import select
            result = await session.execute(
                select(User).where(User.email == "admin@test.com")
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print("✓ Admin user already exists with email: admin@test.com")
                return
            
            # Create admin user
            admin_user = User(
                user_id="admin_001",
                email="admin@test.com",
                hashed_password=get_password_hash("admin123"),
                first_name="Admin",
                last_name="User",
                user_type="ADMIN",
                is_active=True,
                is_verified=True,
                created_at=datetime.utcnow()
            )
            
            session.add(admin_user)
            await session.commit()
            await session.refresh(admin_user)
            
            print("✓ Admin user created successfully!")
            print(f"  Email: admin@test.com")
            print(f"  Password: admin123")
            print(f"  User Type: ADMIN")
            print(f"  User ID: {admin_user.user_id}")
            
            break
            
    except Exception as e:
        print(f"✗ Error creating admin user: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Creating admin user...")
    success = asyncio.run(create_admin_user())
    
    if success:
        print("\n✓ Admin user creation completed!")
        print("You can now login with:")
        print("  Email: admin@test.com")
        print("  Password: admin123")
    else:
        print("\n✗ Admin user creation failed!")
        sys.exit(1)