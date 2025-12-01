#!/usr/bin/env python3
"""
Check database schema and current data
"""

import sqlite3
import os

def check_database_schema():
    """Check the SQLite database schema and data"""
    print("🔍 Checking Database Schema and Data")
    print("=" * 50)
    
    db_path = "./punjab_rozgar.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if users table exists
        print("1. Checking users table...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        users_table = cursor.fetchone()
        if users_table:
            print("   ✅ users table exists")
            
            # Check users table schema
            cursor.execute("PRAGMA table_info(users);")
            users_schema = cursor.fetchall()
            print("   📋 users table columns:")
            for col in users_schema:
                print(f"      - {col[1]} {col[2]}")
            
            # Check user count
            cursor.execute("SELECT COUNT(*) FROM users;")
            user_count = cursor.fetchone()[0]
            print(f"   📊 Total users: {user_count}")
            
            if user_count > 0:
                cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role;")
                role_counts = cursor.fetchall()
                print("   👥 Users by role:")
                for role, count in role_counts:
                    print(f"      - {role}: {count}")
        else:
            print("   ❌ users table does not exist")
        
        print()
        
        # Check if jobs table exists
        print("2. Checking jobs table...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='jobs';")
        jobs_table = cursor.fetchone()
        if jobs_table:
            print("   ✅ jobs table exists")
            
            # Check jobs table schema
            cursor.execute("PRAGMA table_info(jobs);")
            jobs_schema = cursor.fetchall()
            print("   📋 jobs table columns:")
            for col in jobs_schema:
                print(f"      - {col[1]} {col[2]}")
            
            # Check job count
            cursor.execute("SELECT COUNT(*) FROM jobs;")
            job_count = cursor.fetchone()[0]
            print(f"   📊 Total jobs: {job_count}")
            
            if job_count > 0:
                cursor.execute("SELECT job_type, COUNT(*) FROM jobs GROUP BY job_type;")
                type_counts = cursor.fetchall()
                print("   💼 Jobs by type:")
                for job_type, count in type_counts:
                    print(f"      - {job_type}: {count}")
                    
                cursor.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status;")
                status_counts = cursor.fetchall()
                print("   📈 Jobs by status:")
                for status, count in status_counts:
                    print(f"      - {status}: {count}")
        else:
            print("   ❌ jobs table does not exist")
        
        print()
        
        # Check all tables
        print("3. All tables in database:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            print(f"   - {table[0]}")
        
        conn.close()
        
        print()
        print("=" * 50)
        print("🎯 Next: Check if database needs to be created/migrated")
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_database_schema()