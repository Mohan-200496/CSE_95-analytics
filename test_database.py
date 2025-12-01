#!/usr/bin/env python3
"""
Test job creation and verify database setup
"""

import sqlite3
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def check_all_databases():
    """Check all SQLite database files"""
    print("🔍 Checking All Database Files")
    print("=" * 60)
    
    db_files = ['punjab_rozgar.db', 'dev_punjab_rozgar.db']
    
    for db_file in db_files:
        print(f"\n📁 Database: {db_file}")
        if not os.path.exists(db_file):
            print(f"   ❌ File not found: {db_file}")
            continue
        
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            if not tables:
                print("   ❌ No tables found")
            else:
                print(f"   ✅ Found {len(tables)} tables:")
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                    count = cursor.fetchone()[0]
                    print(f"      - {table[0]}: {count} records")
            
            conn.close()
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)

def test_job_creation_directly():
    """Test job creation by directly inserting into database"""
    print("🧪 Testing Job Creation Directly")
    print("=" * 60)
    
    # Use the database that has tables
    db_file = 'dev_punjab_rozgar.db'
    
    if not os.path.exists(db_file):
        print(f"❌ Database file not found: {db_file}")
        return False
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Check if jobs table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='jobs';")
        if not cursor.fetchone():
            print("❌ Jobs table does not exist")
            return False
        
        # Insert a test job
        job_data = {
            'job_id': 'test-job-001',
            'title': 'Test Software Developer',
            'description': 'Test job posting to verify database functionality',
            'requirements': 'Python, FastAPI',
            'location': 'Punjab, India',
            'job_type': 'full_time',
            'status': 'active',
            'company_name': 'Test Company',
            'contact_email': 'test@example.com',
            'salary_min': 50000,
            'salary_max': 80000,
            'created_by': 'test-user-001'
        }
        
        # Insert job
        insert_query = """
            INSERT INTO jobs (
                job_id, title, description, requirements, location, 
                job_type, status, company_name, contact_email, 
                salary_min, salary_max, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor.execute(insert_query, list(job_data.values()))
        conn.commit()
        
        # Verify insertion
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE job_id = ?", (job_data['job_id'],))
        count = cursor.fetchone()[0]
        
        if count > 0:
            print("✅ Test job created successfully!")
            
            # Get the job details
            cursor.execute("SELECT title, company_name, job_type, status FROM jobs WHERE job_id = ?", (job_data['job_id'],))
            job = cursor.fetchone()
            print(f"   📋 Title: {job[0]}")
            print(f"   🏢 Company: {job[1]}")
            print(f"   💼 Type: {job[2]}")
            print(f"   📈 Status: {job[3]}")
            
            # Count total jobs
            cursor.execute("SELECT COUNT(*) FROM jobs")
            total = cursor.fetchone()[0]
            print(f"   📊 Total jobs in database: {total}")
            
        else:
            print("❌ Failed to create test job")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error testing job creation: {e}")
        return False

if __name__ == "__main__":
    check_all_databases()
    test_job_creation_directly()