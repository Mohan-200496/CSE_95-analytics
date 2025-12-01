#!/usr/bin/env python3
"""
Check what enum values the database expects
"""

import asyncio
import asyncpg
from backend.app.core.config import settings

async def check_database_enums():
    """Check what enum values the database actually expects"""
    print("🔍 Checking Database Enum Values")
    print("=" * 50)
    
    try:
        # Connect to database
        conn = await asyncpg.connect(settings.DATABASE_URL)
        
        # Check userrole enum
        print("1. Checking userrole enum values...")
        userrole_query = """
            SELECT enumlabel 
            FROM pg_enum 
            WHERE enumtypid = (
                SELECT oid 
                FROM pg_type 
                WHERE typname = 'userrole'
            )
            ORDER BY enumsortorder;
        """
        userrole_values = await conn.fetch(userrole_query)
        print("   ✅ userrole enum values:")
        for value in userrole_values:
            print(f"      - '{value['enumlabel']}'")
        
        print()
        
        # Check jobtype enum
        print("2. Checking jobtype enum values...")
        jobtype_query = """
            SELECT enumlabel 
            FROM pg_enum 
            WHERE enumtypid = (
                SELECT oid 
                FROM pg_type 
                WHERE typname = 'jobtype'
            )
            ORDER BY enumsortorder;
        """
        jobtype_values = await conn.fetch(jobtype_query)
        print("   ✅ jobtype enum values:")
        for value in jobtype_values:
            print(f"      - '{value['enumlabel']}'")
        
        print()
        
        # Check all enum types
        print("3. All enum types in database:")
        enum_types_query = """
            SELECT typname 
            FROM pg_type 
            WHERE typcategory = 'E'
            ORDER BY typname;
        """
        enum_types = await conn.fetch(enum_types_query)
        for enum_type in enum_types:
            print(f"   - {enum_type['typname']}")
        
        await conn.close()
        
        print()
        print("=" * 50)
        print("🎯 Next: Update Python enums to match database values")
        
    except Exception as e:
        print(f"❌ Error checking enums: {e}")

if __name__ == "__main__":
    asyncio.run(check_database_enums())