#!/usr/bin/env python3
"""Fix database enum values"""

import sqlite3

def fix_database_enums():
    """Fix invalid enum values in database"""
    conn = sqlite3.connect('punjab_rozgar.db')
    cursor = conn.cursor()
    
    print("🔧 Fixing database enum values...")
    
    # Check current values
    cursor.execute('SELECT DISTINCT employer_type FROM jobs WHERE employer_type IS NOT NULL')
    employer_types = [row[0] for row in cursor.fetchall()]
    print(f"Current employer_type values: {employer_types}")
    
    cursor.execute('SELECT DISTINCT job_type FROM jobs WHERE job_type IS NOT NULL')
    job_types = [row[0] for row in cursor.fetchall()]
    print(f"Current job_type values: {job_types}")
    
    # Fix employer_type enum values
    updates_made = 0
    
    cursor.execute('UPDATE jobs SET employer_type = ? WHERE employer_type = ?', ('private', 'private_company'))
    updates_made += cursor.rowcount
    
    cursor.execute('UPDATE jobs SET employer_type = ? WHERE employer_type = ?', ('government', 'govt'))
    updates_made += cursor.rowcount
    
    cursor.execute('UPDATE jobs SET employer_type = ? WHERE employer_type = ?', ('public_sector', 'public'))
    updates_made += cursor.rowcount
    
    # Fix job_type enum values
    cursor.execute('UPDATE jobs SET job_type = ? WHERE job_type = ?', ('full_time', 'full-time'))
    updates_made += cursor.rowcount
    
    cursor.execute('UPDATE jobs SET job_type = ? WHERE job_type = ?', ('part_time', 'part-time'))
    updates_made += cursor.rowcount
    
    conn.commit()
    
    # Verify fixes
    cursor.execute('SELECT DISTINCT employer_type FROM jobs WHERE employer_type IS NOT NULL')
    new_employer_types = [row[0] for row in cursor.fetchall()]
    print(f"Updated employer_type values: {new_employer_types}")
    
    cursor.execute('SELECT DISTINCT job_type FROM jobs WHERE job_type IS NOT NULL')
    new_job_types = [row[0] for row in cursor.fetchall()]
    print(f"Updated job_type values: {new_job_types}")
    
    conn.close()
    
    print(f"✅ Fixed {updates_made} enum value mismatches")
    return updates_made > 0

if __name__ == "__main__":
    fix_database_enums()