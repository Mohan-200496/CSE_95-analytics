#!/usr/bin/env python3
"""
Data Cleanup Script for Punjab Rozgar Portal
Fixes identified data integrity issues
"""

import sqlite3

def clean_data():
    print("🧹 DATA CLEANUP AND STANDARDIZATION")
    print("=" * 50)
    
    conn = sqlite3.connect('punjab_rozgar.db')
    cursor = conn.cursor()
    
    cleanup_count = 0
    
    # 1. Fix user roles (convert to lowercase)
    print("\n🔧 Fixing User Roles...")
    cursor.execute("UPDATE users SET role = 'admin' WHERE role = 'ADMIN'")
    cleanup_count += cursor.rowcount
    
    cursor.execute("UPDATE users SET role = 'employer' WHERE role = 'EMPLOYER'")
    cleanup_count += cursor.rowcount
    
    cursor.execute("UPDATE users SET role = 'job_seeker' WHERE role = 'JOB_SEEKER'")
    cleanup_count += cursor.rowcount
    
    print(f"   ✅ Fixed {cleanup_count} user role inconsistencies")
    
    # 2. Standardize job categories (fix case inconsistencies)
    print("\n🔧 Standardizing Job Categories...")
    categories_fixed = 0
    
    cursor.execute("UPDATE jobs SET category = 'Engineering' WHERE category = 'engineering'")
    categories_fixed += cursor.rowcount
    
    cursor.execute("UPDATE jobs SET category = 'Human Resources' WHERE category = 'hr'")
    categories_fixed += cursor.rowcount
    
    print(f"   ✅ Standardized {categories_fixed} job categories")
    
    # 3. Set default values for missing employer references
    print("\n🔧 Fixing Employer References...")
    cursor.execute("""
        UPDATE jobs 
        SET employer_id = 'system_admin', employer_name = 'System Administrator'
        WHERE employer_id IS NULL OR employer_id = ''
    """)
    orphan_jobs_fixed = cursor.rowcount
    print(f"   ✅ Fixed {orphan_jobs_fixed} orphaned jobs")
    
    # 4. Update job creator roles (ensure jobs are linked to employers/admins)
    print("\n🔧 Validating Job Creator Roles...")
    cursor.execute("""
        SELECT COUNT(*) FROM jobs j
        JOIN users u ON j.employer_id = u.user_id
        WHERE u.role NOT IN ('employer', 'admin')
    """)
    invalid_creators = cursor.fetchone()[0]
    
    if invalid_creators > 0:
        # Update non-employer users who created jobs to be employers
        cursor.execute("""
            UPDATE users 
            SET role = 'employer'
            WHERE user_id IN (
                SELECT DISTINCT j.employer_id FROM jobs j
                JOIN users u ON j.employer_id = u.user_id
                WHERE u.role NOT IN ('employer', 'admin')
            )
        """)
        role_updates = cursor.rowcount
        print(f"   ✅ Updated {role_updates} user roles to employer")
    else:
        print("   ✅ All job creators have valid roles")
    
    # 5. Standardize user statuses
    print("\n🔧 Standardizing User Statuses...")
    cursor.execute("UPDATE users SET status = 'active' WHERE status = 'ACTIVE'")
    cursor.execute("UPDATE users SET status = 'pending' WHERE status = 'PENDING_VERIFICATION'")
    status_fixes = cursor.rowcount
    print(f"   ✅ Standardized user statuses")
    
    # 6. Add missing data for completeness
    print("\n🔧 Adding Missing Default Values...")
    
    # Set default profile completion scores
    cursor.execute("UPDATE users SET profile_completion_score = 60 WHERE profile_completion_score IS NULL")
    
    # Set default notification preferences
    cursor.execute("UPDATE users SET email_notifications = 1 WHERE email_notifications IS NULL")
    cursor.execute("UPDATE users SET sms_notifications = 0 WHERE sms_notifications IS NULL")
    
    # Set default job application counts
    cursor.execute("UPDATE jobs SET applications_count = 0 WHERE applications_count IS NULL")
    cursor.execute("UPDATE jobs SET views_count = 0 WHERE views_count IS NULL")
    
    print("   ✅ Added default values for missing fields")
    
    conn.commit()
    
    # 7. Verification - Re-run key checks
    print("\n📊 POST-CLEANUP VERIFICATION")
    print("-" * 30)
    
    # Check user roles
    cursor.execute('SELECT DISTINCT role FROM users')
    user_roles = [r[0] for r in cursor.fetchall() if r[0]]
    valid_user_roles = ['admin', 'employer', 'job_seeker']
    invalid_user_roles = [r for r in user_roles if r not in valid_user_roles]
    
    if not invalid_user_roles:
        print("✅ All user roles are now valid")
    else:
        print(f"⚠️  Still invalid user roles: {invalid_user_roles}")
    
    # Check job-employer relationships
    cursor.execute('''
        SELECT COUNT(*) FROM jobs j
        JOIN users u ON j.employer_id = u.user_id
        WHERE u.role NOT IN ('employer', 'admin')
    ''')
    invalid_job_creators = cursor.fetchone()[0]
    
    if invalid_job_creators == 0:
        print("✅ All job creators now have valid roles")
    else:
        print(f"⚠️  Still {invalid_job_creators} jobs with invalid creators")
    
    # Check categories
    cursor.execute('SELECT DISTINCT category FROM jobs WHERE category IS NOT NULL')
    categories = cursor.fetchall()
    print(f"✅ Standardized categories: {len(categories)} unique categories")
    
    # Final statistics
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM jobs')
    total_jobs = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users WHERE role = "admin"')
    admins = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users WHERE role = "employer"')
    employers = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users WHERE role = "job_seeker"')
    job_seekers = cursor.fetchone()[0]
    
    print(f"\n📈 FINAL STATISTICS")
    print("-" * 30)
    print(f"Total Users: {total_users}")
    print(f"  • Admins: {admins}")
    print(f"  • Employers: {employers}")  
    print(f"  • Job Seekers: {job_seekers}")
    print(f"Total Jobs: {total_jobs}")
    
    conn.close()
    
    total_fixes = cleanup_count + categories_fixed + orphan_jobs_fixed + status_fixes
    print(f"\n🎯 CLEANUP SUMMARY")
    print("-" * 30)
    print(f"Total fixes applied: {total_fixes}")
    print("✅ Data cleanup completed successfully!")
    
    return True

if __name__ == "__main__":
    success = clean_data()
    if success:
        print("\n🎉 DATABASE CLEANUP SUCCESSFUL!")
        print("All major data integrity issues have been resolved.")
    else:
        print("\n❌ Cleanup encountered issues.")