#!/usr/bin/env python3
"""
Direct production database enum fix script.
This script connects directly to the production PostgreSQL database and fixes enum values.
"""

import asyncio
import asyncpg
import os
from urllib.parse import urlparse

# Production database URL (from environment)
DATABASE_URL = "postgresql://postgres:FcJOKvbKYYPUJLIbshONOiRBuJEzoyDl@autorack.proxy.rlwy.net:27364/railway"

async def fix_production_enums():
    """Fix enum values in the production database"""
    print("🔧 Fixing Production Database Enums")
    print("=" * 50)
    
    try:
        # Connect to the database
        print("🔌 Connecting to production database...")
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected successfully!")
        
        # Check current enum values
        print("\n📊 Checking current enum values...")
        
        # Get current userrole enum values
        result = await conn.fetch("""
            SELECT enumlabel 
            FROM pg_enum 
            JOIN pg_type ON pg_enum.enumtypid = pg_type.oid 
            WHERE pg_type.typname = 'userrole'
            ORDER BY enumlabel;
        """)
        current_userrole_values = [row['enumlabel'] for row in result]
        print(f"   Current UserRole values: {current_userrole_values}")
        
        # Get current jobtype enum values
        result = await conn.fetch("""
            SELECT enumlabel 
            FROM pg_enum 
            JOIN pg_type ON pg_enum.enumtypid = pg_type.oid 
            WHERE pg_type.typname = 'jobtype'
            ORDER BY enumlabel;
        """)
        current_jobtype_values = [row['enumlabel'] for row in result]
        print(f"   Current JobType values: {current_jobtype_values}")
        
        # Get current jobstatus enum values
        result = await conn.fetch("""
            SELECT enumlabel 
            FROM pg_enum 
            JOIN pg_type ON pg_enum.enumtypid = pg_type.oid 
            WHERE pg_type.typname = 'jobstatus'
            ORDER BY enumlabel;
        """)
        current_jobstatus_values = [row['enumlabel'] for row in result]
        print(f"   Current JobStatus values: {current_jobstatus_values}")
        
        # Get current accountstatus enum values
        result = await conn.fetch("""
            SELECT enumlabel 
            FROM pg_enum 
            JOIN pg_type ON pg_enum.enumtypid = pg_type.oid 
            WHERE pg_type.typname = 'accountstatus'
            ORDER BY enumlabel;
        """)
        current_accountstatus_values = [row['enumlabel'] for row in result]
        print(f"   Current AccountStatus values: {current_accountstatus_values}")
        
        # Get current employertype enum values
        result = await conn.fetch("""
            SELECT enumlabel 
            FROM pg_enum 
            JOIN pg_type ON pg_enum.enumtypid = pg_type.oid 
            WHERE pg_type.typname = 'employertype'
            ORDER BY enumlabel;
        """)
        current_employertype_values = [row['enumlabel'] for row in result]
        print(f"   Current EmployerType values: {current_employertype_values}")
        
        print("\n🔄 Adding missing enum values...")
        
        # Expected values based on our models
        expected_userrole = ['job_seeker', 'employer', 'admin', 'moderator']
        expected_jobtype = ['full_time', 'part_time', 'contract', 'temporary', 'internship', 'freelance']
        expected_jobstatus = ['draft', 'pending_approval', 'active', 'paused', 'closed', 'expired']
        expected_accountstatus = ['active', 'inactive', 'suspended', 'pending_verification']
        expected_employertype = ['government', 'public_sector', 'private', 'ngo', 'startup']
        
        # Add missing UserRole values
        for value in expected_userrole:
            if value not in current_userrole_values:
                try:
                    await conn.execute(f"ALTER TYPE userrole ADD VALUE '{value}';")
                    print(f"   ✅ Added UserRole: {value}")
                except Exception as e:
                    print(f"   ❌ Failed to add UserRole {value}: {e}")
        
        # Add missing JobType values
        for value in expected_jobtype:
            if value not in current_jobtype_values:
                try:
                    await conn.execute(f"ALTER TYPE jobtype ADD VALUE '{value}';")
                    print(f"   ✅ Added JobType: {value}")
                except Exception as e:
                    print(f"   ❌ Failed to add JobType {value}: {e}")
        
        # Add missing JobStatus values
        for value in expected_jobstatus:
            if value not in current_jobstatus_values:
                try:
                    await conn.execute(f"ALTER TYPE jobstatus ADD VALUE '{value}';")
                    print(f"   ✅ Added JobStatus: {value}")
                except Exception as e:
                    print(f"   ❌ Failed to add JobStatus {value}: {e}")
        
        # Add missing AccountStatus values
        for value in expected_accountstatus:
            if value not in current_accountstatus_values:
                try:
                    await conn.execute(f"ALTER TYPE accountstatus ADD VALUE '{value}';")
                    print(f"   ✅ Added AccountStatus: {value}")
                except Exception as e:
                    print(f"   ❌ Failed to add AccountStatus {value}: {e}")
        
        # Add missing EmployerType values
        for value in expected_employertype:
            if value not in current_employertype_values:
                try:
                    await conn.execute(f"ALTER TYPE employertype ADD VALUE '{value}';")
                    print(f"   ✅ Added EmployerType: {value}")
                except Exception as e:
                    print(f"   ❌ Failed to add EmployerType {value}: {e}")
        
        print("\n📊 Verifying fixes...")
        
        # Re-check enum values after fixes
        result = await conn.fetch("""
            SELECT enumlabel 
            FROM pg_enum 
            JOIN pg_type ON pg_enum.enumtypid = pg_type.oid 
            WHERE pg_type.typname = 'userrole'
            ORDER BY enumlabel;
        """)
        updated_userrole_values = [row['enumlabel'] for row in result]
        print(f"   Updated UserRole values: {updated_userrole_values}")
        
        result = await conn.fetch("""
            SELECT enumlabel 
            FROM pg_enum 
            JOIN pg_type ON pg_enum.enumtypid = pg_type.oid 
            WHERE pg_type.typname = 'jobtype'
            ORDER BY enumlabel;
        """)
        updated_jobtype_values = [row['enumlabel'] for row in result]
        print(f"   Updated JobType values: {updated_jobtype_values}")
        
        print("\n✅ Enum fix process completed!")
        
        # Close connection
        await conn.close()
        print("🔌 Database connection closed")
        
    except Exception as e:
        print(f"❌ Error fixing enums: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_production_enums())