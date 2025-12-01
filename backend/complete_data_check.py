#!/usr/bin/env python3
"""
Complete Data Integrity Check for Punjab Rozgar Portal
Comprehensive validation of all data across the system
"""

import sqlite3
import json
from datetime import datetime

def complete_data_check():
    print("📊 COMPLETE DATA INTEGRITY CHECK")
    print("=" * 60)
    print(f"Punjab Rozgar Portal - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect('punjab_rozgar.db')
        cursor = conn.cursor()
        
        # 1. USERS TABLE ANALYSIS
        print("\n👥 USERS TABLE ANALYSIS")
        print("-" * 30)
        
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE role = "admin"')
        admin_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE role = "employer"')
        employer_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE role = "job_seeker"')
        jobseeker_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE status = "active"')
        active_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE email_verified = 1')
        verified_users = cursor.fetchone()[0]
        
        print(f"Total Users: {total_users}")
        print(f"  • Admins: {admin_count}")
        print(f"  • Employers: {employer_count}")
        print(f"  • Job Seekers: {jobseeker_count}")
        print(f"  • Active: {active_users}")
        print(f"  • Email Verified: {verified_users}")
        
        # Check for data integrity issues
        cursor.execute('SELECT COUNT(*) FROM users WHERE email IS NULL OR email = ""')
        missing_emails = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE hashed_password IS NULL OR hashed_password = ""')
        missing_passwords = cursor.fetchone()[0]
        
        if missing_emails > 0 or missing_passwords > 0:
            print(f"⚠️  Data Issues: {missing_emails} missing emails, {missing_passwords} missing passwords")
        else:
            print("✅ User data integrity: PERFECT")
        
        # Sample user data
        cursor.execute('SELECT user_id, email, role, status FROM users LIMIT 3')
        sample_users = cursor.fetchall()
        print("\n📋 Sample Users:")
        for user in sample_users:
            print(f"  • {user[1]} ({user[2]}) - {user[3]}")
        
        # 2. JOBS TABLE ANALYSIS
        print("\n💼 JOBS TABLE ANALYSIS")
        print("-" * 30)
        
        cursor.execute('SELECT COUNT(*) FROM jobs')
        total_jobs = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM jobs WHERE status = "active"')
        active_jobs = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM jobs WHERE status = "pending_approval"')
        pending_jobs = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM jobs WHERE status = "draft"')
        draft_jobs = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM jobs WHERE status = "closed"')
        closed_jobs = cursor.fetchone()[0]
        
        print(f"Total Jobs: {total_jobs}")
        print(f"  • Active: {active_jobs}")
        print(f"  • Pending Approval: {pending_jobs}")
        print(f"  • Draft: {draft_jobs}")
        print(f"  • Closed: {closed_jobs}")
        
        # Job categories analysis
        cursor.execute('SELECT category, COUNT(*) FROM jobs WHERE category IS NOT NULL GROUP BY category')
        categories = cursor.fetchall()
        print("\n📊 Jobs by Category:")
        for cat, count in categories:
            print(f"  • {cat}: {count} jobs")
        
        # Job types analysis
        cursor.execute('SELECT job_type, COUNT(*) FROM jobs WHERE job_type IS NOT NULL GROUP BY job_type')
        job_types = cursor.fetchall()
        print("\n🏷️  Jobs by Type:")
        for jtype, count in job_types:
            print(f"  • {jtype}: {count} jobs")
        
        # Employer types analysis
        cursor.execute('SELECT employer_type, COUNT(*) FROM jobs WHERE employer_type IS NOT NULL GROUP BY employer_type')
        emp_types = cursor.fetchall()
        print("\n🏢 Jobs by Employer Type:")
        for etype, count in emp_types:
            print(f"  • {etype}: {count} jobs")
        
        # Salary analysis
        cursor.execute('SELECT AVG(salary_min), AVG(salary_max), MIN(salary_min), MAX(salary_max) FROM jobs WHERE salary_min IS NOT NULL')
        salary_stats = cursor.fetchone()
        if salary_stats[0]:
            print(f"\n💰 Salary Statistics:")
            print(f"  • Avg Min Salary: ₹{int(salary_stats[0]):,}")
            print(f"  • Avg Max Salary: ₹{int(salary_stats[1]):,}")
            print(f"  • Lowest Min: ₹{int(salary_stats[2]):,}")
            print(f"  • Highest Max: ₹{int(salary_stats[3]):,}")
        
        # Location analysis
        cursor.execute('SELECT location_city, COUNT(*) FROM jobs WHERE location_city IS NOT NULL GROUP BY location_city ORDER BY COUNT(*) DESC LIMIT 5')
        locations = cursor.fetchall()
        print("\n🌍 Top Job Locations:")
        for loc, count in locations:
            print(f"  • {loc}: {count} jobs")
        
        # Data quality checks
        cursor.execute('SELECT COUNT(*) FROM jobs WHERE title IS NULL OR title = ""')
        missing_titles = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM jobs WHERE description IS NULL OR description = ""')
        missing_descriptions = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM jobs WHERE employer_id IS NULL OR employer_id = ""')
        missing_employer_ids = cursor.fetchone()[0]
        
        print("\n🔍 Data Quality Check:")
        if missing_titles == 0 and missing_descriptions == 0 and missing_employer_ids == 0:
            print("✅ Job data integrity: PERFECT")
        else:
            print(f"⚠️  Issues: {missing_titles} missing titles, {missing_descriptions} missing descriptions, {missing_employer_ids} missing employer IDs")
        
        # Sample job data
        cursor.execute('SELECT title, category, job_type, employer_name, status FROM jobs LIMIT 3')
        sample_jobs = cursor.fetchall()
        print("\n📋 Sample Jobs:")
        for job in sample_jobs:
            print(f"  • {job[0]} ({job[1]}, {job[2]}) by {job[3]} - {job[4]}")
        
        # 3. APPLICATIONS TABLE ANALYSIS (if exists)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='job_applications'")
        if cursor.fetchone():
            print("\n📄 JOB APPLICATIONS ANALYSIS")
            print("-" * 30)
            
            cursor.execute('SELECT COUNT(*) FROM job_applications')
            total_applications = cursor.fetchone()[0]
            
            cursor.execute('SELECT status, COUNT(*) FROM job_applications GROUP BY status')
            app_statuses = cursor.fetchall()
            
            print(f"Total Applications: {total_applications}")
            print("Application Status Distribution:")
            for status, count in app_statuses:
                print(f"  • {status}: {count}")
        
        # 4. RELATIONSHIPS VALIDATION
        print("\n🔗 RELATIONSHIP VALIDATION")
        print("-" * 30)
        
        # Check if all jobs have valid employer IDs
        cursor.execute('''
            SELECT COUNT(*) FROM jobs j 
            LEFT JOIN users u ON j.employer_id = u.user_id 
            WHERE u.user_id IS NULL AND j.employer_id IS NOT NULL
        ''')
        orphaned_jobs = cursor.fetchone()[0]
        
        if orphaned_jobs == 0:
            print("✅ All jobs have valid employers")
        else:
            print(f"⚠️  {orphaned_jobs} jobs have invalid employer references")
        
        # Check employer role consistency
        cursor.execute('''
            SELECT COUNT(*) FROM jobs j
            JOIN users u ON j.employer_id = u.user_id
            WHERE u.role NOT IN ('employer', 'admin')
        ''')
        invalid_employer_roles = cursor.fetchone()[0]
        
        if invalid_employer_roles == 0:
            print("✅ All job creators have appropriate roles")
        else:
            print(f"⚠️  {invalid_employer_roles} jobs created by non-employers")
        
        # 5. ENUM CONSISTENCY CHECK
        print("\n🏷️  ENUM CONSISTENCY CHECK")
        print("-" * 30)
        
        # Check user roles
        cursor.execute('SELECT DISTINCT role FROM users')
        user_roles = [r[0] for r in cursor.fetchall() if r[0]]
        valid_user_roles = ['admin', 'employer', 'job_seeker']
        invalid_user_roles = [r for r in user_roles if r not in valid_user_roles]
        
        print(f"User Roles: {user_roles}")
        if not invalid_user_roles:
            print("✅ All user roles are valid")
        else:
            print(f"⚠️  Invalid user roles: {invalid_user_roles}")
        
        # Check job statuses
        cursor.execute('SELECT DISTINCT status FROM jobs WHERE status IS NOT NULL')
        job_statuses = [r[0] for r in cursor.fetchall()]
        valid_job_statuses = ['draft', 'pending_approval', 'active', 'paused', 'closed', 'expired']
        invalid_job_statuses = [s for s in job_statuses if s not in valid_job_statuses]
        
        print(f"Job Statuses: {job_statuses}")
        if not invalid_job_statuses:
            print("✅ All job statuses are valid")
        else:
            print(f"⚠️  Invalid job statuses: {invalid_job_statuses}")
        
        # Check job types
        cursor.execute('SELECT DISTINCT job_type FROM jobs WHERE job_type IS NOT NULL')
        db_job_types = [r[0] for r in cursor.fetchall()]
        valid_job_types = ['full_time', 'part_time', 'contract', 'temporary', 'internship', 'freelance']
        invalid_job_types = [t for t in db_job_types if t not in valid_job_types]
        
        print(f"Job Types: {db_job_types}")
        if not invalid_job_types:
            print("✅ All job types are valid")
        else:
            print(f"⚠️  Invalid job types: {invalid_job_types}")
        
        # Check employer types
        cursor.execute('SELECT DISTINCT employer_type FROM jobs WHERE employer_type IS NOT NULL')
        db_employer_types = [r[0] for r in cursor.fetchall()]
        valid_employer_types = ['government', 'public_sector', 'private', 'ngo', 'startup']
        invalid_employer_types = [t for t in db_employer_types if t not in valid_employer_types]
        
        print(f"Employer Types: {db_employer_types}")
        if not invalid_employer_types:
            print("✅ All employer types are valid")
        else:
            print(f"⚠️  Invalid employer types: {invalid_employer_types}")
        
        # 6. TEMPORAL DATA ANALYSIS
        print("\n⏰ TEMPORAL DATA ANALYSIS")
        print("-" * 30)
        
        cursor.execute('SELECT MIN(created_at), MAX(created_at) FROM users WHERE created_at IS NOT NULL')
        user_date_range = cursor.fetchone()
        if user_date_range[0]:
            print(f"User Registration Range: {user_date_range[0]} to {user_date_range[1]}")
        
        cursor.execute('SELECT MIN(created_at), MAX(created_at) FROM jobs WHERE created_at IS NOT NULL')
        job_date_range = cursor.fetchone()
        if job_date_range[0]:
            print(f"Job Creation Range: {job_date_range[0]} to {job_date_range[1]}")
        
        # Recent activity
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE created_at > datetime('now', '-7 days')")
        recent_jobs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE created_at > datetime('now', '-7 days')")
        recent_users = cursor.fetchone()[0]
        
        print(f"Recent Activity (Last 7 Days):")
        print(f"  • New Jobs: {recent_jobs}")
        print(f"  • New Users: {recent_users}")
        
        # 7. OVERALL HEALTH SCORE
        print("\n🏥 OVERALL DATA HEALTH SCORE")
        print("-" * 30)
        
        health_issues = 0
        health_issues += missing_emails + missing_passwords
        health_issues += missing_titles + missing_descriptions + missing_employer_ids
        health_issues += orphaned_jobs + invalid_employer_roles
        health_issues += len(invalid_user_roles + invalid_job_statuses + invalid_job_types + invalid_employer_types)
        
        if health_issues == 0:
            print("🎉 DATA HEALTH SCORE: 100% - PERFECT!")
            print("✅ No data integrity issues detected")
        elif health_issues < 5:
            print(f"⚠️  DATA HEALTH SCORE: 90% - Minor Issues ({health_issues} issues)")
        elif health_issues < 10:
            print(f"⚠️  DATA HEALTH SCORE: 70% - Some Issues ({health_issues} issues)")
        else:
            print(f"❌ DATA HEALTH SCORE: <70% - Major Issues ({health_issues} issues)")
        
        conn.close()
        
        # 8. SUMMARY STATISTICS
        print("\n📈 SUMMARY STATISTICS")
        print("-" * 30)
        print(f"📊 Database contains:")
        print(f"  • {total_users} total users ({active_users} active)")
        print(f"  • {total_jobs} total jobs ({active_jobs} active)")
        print(f"  • {len(categories)} job categories")
        print(f"  • {len(set([loc[0] for loc in locations]))} cities with jobs")
        print(f"  • Data spans from {user_date_range[0] or 'N/A'} to present")
        
        return health_issues == 0
        
    except Exception as e:
        print(f"❌ Error during data check: {e}")
        return False

if __name__ == "__main__":
    success = complete_data_check()
    print("\n" + "=" * 60)
    if success:
        print("🎊 COMPLETE DATA CHECK: SUCCESSFUL!")
        print("✅ All data is consistent, complete, and valid")
    else:
        print("⚠️  COMPLETE DATA CHECK: Issues detected")
        print("Please review the details above")
    print("=" * 60)