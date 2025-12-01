#!/usr/bin/env python3
"""
Quick fix for role inconsistency - convert lowercase roles to uppercase to match UserRole enum
"""

import sqlite3
import sys

def fix_user_roles():
    """Convert user roles from lowercase to uppercase to match backend enum"""
    
    try:
        # Connect to database
        conn = sqlite3.connect('backend/punjab_rozgar.db')
        cursor = conn.cursor()
        
        print("🔧 Fixing user role inconsistencies...")
        
        # Convert lowercase roles to uppercase to match UserRole enum
        fixes = 0
        
        cursor.execute("UPDATE users SET role = 'EMPLOYER' WHERE role = 'employer'")
        fixes += cursor.rowcount
        print(f"   ✅ Fixed {cursor.rowcount} employer roles")
        
        cursor.execute("UPDATE users SET role = 'ADMIN' WHERE role = 'admin'")
        fixes += cursor.rowcount
        print(f"   ✅ Fixed {cursor.rowcount} admin roles")
        
        cursor.execute("UPDATE users SET role = 'JOB_SEEKER' WHERE role = 'job_seeker'")
        fixes += cursor.rowcount
        print(f"   ✅ Fixed {cursor.rowcount} job_seeker roles")
        
        # Commit changes
        conn.commit()
        print(f"\n✅ Total role fixes applied: {fixes}")
        
        # Verify the roles
        cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
        roles = cursor.fetchall()
        print("\n📊 Current role distribution:")
        for role, count in roles:
            print(f"   {role}: {count} users")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error fixing roles: {e}")
        return False

if __name__ == "__main__":
    success = fix_user_roles()
    sys.exit(0 if success else 1)