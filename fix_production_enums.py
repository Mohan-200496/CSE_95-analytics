#!/usr/bin/env python3
"""
Production Database Enum Fix Script
This script fixes enum value mismatches in the production PostgreSQL database
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any, Optional

# Add the backend path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

try:
    import asyncpg
    from app.core.config import get_settings
    from app.models.user import UserRole, AccountStatus
    from app.models.job import JobType, JobStatus, EmployerType
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    print("This script requires asyncpg and the backend modules")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionEnumFixer:
    """Fix enum value mismatches in production database"""
    
    def __init__(self):
        self.settings = get_settings()
        self.connection = None
    
    async def connect(self):
        """Connect to the production database"""
        try:
            # Check if we have a production database URL
            db_url = self.settings.DATABASE_URL
            if not db_url.startswith('postgresql'):
                print("❌ This script is for PostgreSQL production databases only")
                return False
            
            print(f"🔗 Connecting to production database...")
            self.connection = await asyncpg.connect(db_url)
            print("✅ Connected to production database")
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    async def check_existing_enums(self):
        """Check what enum types and values currently exist"""
        print("\n📋 Checking existing enum types...")
        
        try:
            # Get all enum types
            enum_query = """
                SELECT t.typname, string_agg(e.enumlabel, ', ' ORDER BY e.enumsortorder) as values
                FROM pg_type t 
                JOIN pg_enum e ON t.oid = e.enumtypid 
                GROUP BY t.typname
                ORDER BY t.typname;
            """
            
            enums = await self.connection.fetch(enum_query)
            
            if enums:
                print("📊 Current enum types:")
                for enum_type in enums:
                    print(f"  {enum_type['typname']}: {enum_type['values']}")
            else:
                print("ℹ️ No enum types found")
            
            return enums
            
        except Exception as e:
            print(f"❌ Error checking enums: {e}")
            return []
    
    async def check_table_schemas(self):
        """Check current table schemas for enum columns"""
        print("\n🔍 Checking table schemas...")
        
        tables_to_check = ['users', 'jobs', 'companies']
        
        for table_name in tables_to_check:
            try:
                # Check if table exists
                table_exists = await self.connection.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = $1
                    );
                """, table_name)
                
                if not table_exists:
                    print(f"⚠️ Table '{table_name}' does not exist")
                    continue
                
                # Get columns with enum types
                enum_columns = await self.connection.fetch("""
                    SELECT column_name, udt_name, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = $1 
                    AND data_type = 'USER-DEFINED'
                    ORDER BY ordinal_position;
                """, table_name)
                
                if enum_columns:
                    print(f"📋 Table '{table_name}' enum columns:")
                    for col in enum_columns:
                        print(f"  - {col['column_name']}: {col['udt_name']} (nullable: {col['is_nullable']})")
                else:
                    print(f"ℹ️ Table '{table_name}' has no enum columns")
                    
            except Exception as e:
                print(f"❌ Error checking table '{table_name}': {e}")
    
    async def create_correct_enums(self):
        """Create enum types with correct values"""
        print("\n🔧 Creating correct enum types...")
        
        enum_definitions = {
            'userrole_fixed': [role.value for role in UserRole],
            'accountstatus_fixed': [status.value for status in AccountStatus],
            'jobtype_fixed': [job_type.value for job_type in JobType],
            'jobstatus_fixed': [status.value for status in JobStatus],
            'employertype_fixed': [emp_type.value for emp_type in EmployerType]
        }
        
        for enum_name, values in enum_definitions.items():
            try:
                # Check if enum already exists
                exists = await self.connection.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM pg_type WHERE typname = $1
                    );
                """, enum_name)
                
                if exists:
                    print(f"ℹ️ Enum '{enum_name}' already exists, skipping")
                    continue
                
                # Create enum with proper values
                values_str = "', '".join(values)
                create_enum_sql = f"CREATE TYPE {enum_name} AS ENUM ('{values_str}');"
                
                await self.connection.execute(create_enum_sql)
                print(f"✅ Created enum '{enum_name}' with values: {values}")
                
            except Exception as e:
                print(f"❌ Error creating enum '{enum_name}': {e}")
    
    async def test_job_creation(self):
        """Test creating a job with correct enum values"""
        print("\n🧪 Testing job creation with correct enum values...")
        
        try:
            # Check if jobs table exists and what columns it has
            columns = await self.connection.fetch("""
                SELECT column_name, data_type, udt_name
                FROM information_schema.columns 
                WHERE table_name = 'jobs'
                ORDER BY ordinal_position;
            """)
            
            if not columns:
                print("❌ Jobs table does not exist")
                return False
            
            print("📋 Jobs table columns:")
            for col in columns:
                print(f"  - {col['column_name']}: {col['data_type']} ({col['udt_name']})")
            
            # Try to insert a test job (this will help identify the exact enum issue)
            test_job_sql = """
                INSERT INTO jobs (
                    job_id, title, description, job_type, status, 
                    company_name, contact_email, created_at
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, NOW()
                )
                ON CONFLICT (job_id) DO NOTHING;
            """
            
            await self.connection.execute(
                test_job_sql,
                'test_enum_fix_001',
                'Test Job - Enum Fix',
                'Test job to verify enum values work correctly',
                'full_time',  # This should match JobType.FULL_TIME.value
                'active',     # This should match JobStatus.ACTIVE.value
                'Test Company',
                'test@company.com'
            )
            
            print("✅ Test job created successfully!")
            
            # Clean up test job
            await self.connection.execute(
                "DELETE FROM jobs WHERE job_id = $1",
                'test_enum_fix_001'
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Job creation test failed: {e}")
            return False
    
    async def fix_production_enums(self):
        """Main function to fix production enum issues"""
        print("🚀 Production Database Enum Fix")
        print("=" * 50)
        
        if not await self.connect():
            return False
        
        try:
            # Step 1: Check current state
            await self.check_existing_enums()
            await self.check_table_schemas()
            
            # Step 2: Create correct enum types
            await self.create_correct_enums()
            
            # Step 3: Test job creation
            success = await self.test_job_creation()
            
            if success:
                print("\n🎉 Production database enum fix completed successfully!")
                print("✅ Job creation should now work correctly")
            else:
                print("\n⚠️ Enum fix completed but job creation test failed")
                print("Manual intervention may be required")
            
            return success
            
        except Exception as e:
            print(f"❌ Error during enum fix: {e}")
            return False
            
        finally:
            if self.connection:
                await self.connection.close()
                print("🔌 Database connection closed")
    
    async def show_fix_instructions(self):
        """Show manual fix instructions if needed"""
        print("\n📖 Manual Fix Instructions:")
        print("=" * 40)
        print("If automated fix fails, run these SQL commands on production:")
        print()
        print("1. Check current enum values:")
        print("   SELECT enumlabel FROM pg_enum WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'jobtype');")
        print()
        print("2. Add missing enum values (if needed):")
        print("   ALTER TYPE jobtype ADD VALUE IF NOT EXISTS 'full_time';")
        print("   ALTER TYPE jobtype ADD VALUE IF NOT EXISTS 'part_time';")
        print()
        print("3. Check Python enum values:")
        for role in JobType:
            print(f"   JobType.{role.name} = '{role.value}'")

async def main():
    """Main function"""
    fixer = ProductionEnumFixer()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--instructions':
        await fixer.show_fix_instructions()
    else:
        await fixer.fix_production_enums()

if __name__ == "__main__":
    asyncio.run(main())