#!/usr/bin/env python3
"""
Migration script to add missing columns to the jobs table
"""

import sqlite3
import sys
import os

def add_job_columns():
    """Add resume_required and application_method columns to jobs table"""
    
    # Database path
    db_path = os.path.join(os.path.dirname(__file__), "punjab_rozgar.db")
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute("PRAGMA table_info(jobs)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Current columns: {columns}")
        
        # Add resume_required column if it doesn't exist
        if 'resume_required' not in columns:
            print("Adding resume_required column...")
            cursor.execute("""
                ALTER TABLE jobs 
                ADD COLUMN resume_required BOOLEAN DEFAULT 1
            """)
            print("✓ Added resume_required column")
        else:
            print("resume_required column already exists")
        
        # Add application_method column if it doesn't exist
        if 'application_method' not in columns:
            print("Adding application_method column...")
            cursor.execute("""
                ALTER TABLE jobs 
                ADD COLUMN application_method TEXT DEFAULT 'online'
            """)
            print("✓ Added application_method column")
        else:
            print("application_method column already exists")
        
        # Commit changes
        conn.commit()
        
        # Verify new schema
        cursor.execute("PRAGMA table_info(jobs)")
        new_columns = [column[1] for column in cursor.fetchall()]
        print(f"Updated columns: {new_columns}")
        
        # Close connection
        conn.close()
        
        print("✓ Database migration completed successfully!")
        return True
        
    except sqlite3.Error as e:
        print(f"✗ Database error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("Starting database migration...")
    success = add_job_columns()
    
    if success:
        print("\nMigration completed successfully!")
        print("You can now restart the server.")
    else:
        print("\nMigration failed!")
        sys.exit(1)