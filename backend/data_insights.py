#!/usr/bin/env python3
"""
Final Data Analysis and Insights Report
Punjab Rozgar Portal Database
"""

import sqlite3
import json

def generate_data_insights():
    print("📊 PUNJAB ROZGAR PORTAL - DATA INSIGHTS REPORT")
    print("=" * 70)
    print("Complete Data Analysis and Business Insights")
    print("=" * 70)
    
    conn = sqlite3.connect('punjab_rozgar.db')
    cursor = conn.cursor()
    
    # 1. USER DEMOGRAPHICS AND INSIGHTS
    print("\n👥 USER DEMOGRAPHICS & INSIGHTS")
    print("-" * 40)
    
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT role, COUNT(*) FROM users GROUP BY role')
    role_distribution = cursor.fetchall()
    
    print(f"📊 Total Registered Users: {total_users}")
    print("User Role Distribution:")
    for role, count in role_distribution:
        percentage = (count/total_users)*100
        print(f"  • {role.title()}: {count} ({percentage:.1f}%)")
    
    # Geographic distribution
    cursor.execute('SELECT city, COUNT(*) FROM users WHERE city IS NOT NULL GROUP BY city ORDER BY COUNT(*) DESC LIMIT 10')
    user_cities = cursor.fetchall()
    
    if user_cities:
        print("\n🌍 Top User Cities:")
        for city, count in user_cities:
            print(f"  • {city}: {count} users")
    
    # Experience levels
    cursor.execute('SELECT experience_years, COUNT(*) FROM users WHERE experience_years IS NOT NULL GROUP BY experience_years ORDER BY experience_years')
    experience_dist = cursor.fetchall()
    
    if experience_dist:
        print("\n💼 Experience Distribution:")
        for exp, count in experience_dist:
            print(f"  • {exp} years: {count} users")
    
    # 2. JOB MARKET ANALYSIS
    print("\n💼 JOB MARKET ANALYSIS")
    print("-" * 30)
    
    cursor.execute('SELECT COUNT(*) FROM jobs')
    total_jobs = cursor.fetchone()[0]
    
    cursor.execute('SELECT status, COUNT(*) FROM jobs GROUP BY status')
    job_statuses = cursor.fetchall()
    
    print(f"📊 Total Job Postings: {total_jobs}")
    print("Job Status Distribution:")
    for status, count in job_statuses:
        percentage = (count/total_jobs)*100
        print(f"  • {status.title()}: {count} ({percentage:.1f}%)")
    
    # Category analysis
    cursor.execute('SELECT category, COUNT(*) FROM jobs GROUP BY category ORDER BY COUNT(*) DESC')
    categories = cursor.fetchall()
    
    print("\n🏷️  Job Categories (Most Popular):")
    for cat, count in categories:
        percentage = (count/total_jobs)*100
        print(f"  • {cat}: {count} jobs ({percentage:.1f}%)")
    
    # Salary insights
    cursor.execute('SELECT MIN(salary_min), MAX(salary_max), AVG(salary_min), AVG(salary_max) FROM jobs WHERE salary_min > 0')
    salary_stats = cursor.fetchone()
    
    if salary_stats[0]:
        print(f"\n💰 Salary Insights:")
        print(f"  • Salary Range: ₹{int(salary_stats[0]):,} - ₹{int(salary_stats[1]):,}")
        print(f"  • Average Starting: ₹{int(salary_stats[2]):,}")
        print(f"  • Average Maximum: ₹{int(salary_stats[3]):,}")
    
    # Location insights
    cursor.execute('SELECT location_city, location_state, COUNT(*) FROM jobs WHERE location_city IS NOT NULL GROUP BY location_city, location_state ORDER BY COUNT(*) DESC LIMIT 10')
    job_locations = cursor.fetchall()
    
    print("\n🌍 Top Job Locations:")
    for city, state, count in job_locations:
        percentage = (count/total_jobs)*100
        print(f"  • {city}, {state or 'N/A'}: {count} jobs ({percentage:.1f}%)")
    
    # Employer type analysis
    cursor.execute('SELECT employer_type, COUNT(*) FROM jobs GROUP BY employer_type')
    employer_types = cursor.fetchall()
    
    print("\n🏢 Employer Sector Distribution:")
    for emp_type, count in employer_types:
        percentage = (count/total_jobs)*100
        print(f"  • {emp_type.title()}: {count} jobs ({percentage:.1f}%)")
    
    # 3. PLATFORM ENGAGEMENT METRICS
    print("\n📈 PLATFORM ENGAGEMENT METRICS")
    print("-" * 35)
    
    cursor.execute('SELECT SUM(views_count), SUM(applications_count) FROM jobs')
    engagement = cursor.fetchone()
    
    total_views = engagement[0] or 0
    total_applications = engagement[1] or 0
    
    print(f"📊 Total Job Views: {total_views:,}")
    print(f"📊 Total Applications: {total_applications:,}")
    
    if total_views > 0:
        conversion_rate = (total_applications / total_views) * 100
        print(f"📊 Application Conversion Rate: {conversion_rate:.2f}%")
    
    # Recent activity
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE created_at > datetime('now', '-30 days')")
    recent_jobs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE created_at > datetime('now', '-30 days')")
    recent_users = cursor.fetchone()[0]
    
    print(f"\n📅 Recent Activity (Last 30 Days):")
    print(f"  • New Job Postings: {recent_jobs}")
    print(f"  • New User Registrations: {recent_users}")
    
    # 4. DATA QUALITY & COMPLETENESS
    print("\n🔍 DATA QUALITY ASSESSMENT")
    print("-" * 30)
    
    # User profile completeness
    cursor.execute('SELECT AVG(profile_completion_score) FROM users WHERE profile_completion_score IS NOT NULL')
    avg_completion = cursor.fetchone()[0]
    
    if avg_completion:
        print(f"📊 Average Profile Completion: {avg_completion:.1f}%")
    
    # Contact information completeness
    cursor.execute('SELECT COUNT(*) FROM users WHERE email IS NOT NULL')
    users_with_email = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users WHERE phone IS NOT NULL')
    users_with_phone = cursor.fetchone()[0]
    
    print(f"📧 Users with Email: {users_with_email}/{total_users} ({(users_with_email/total_users)*100:.1f}%)")
    print(f"📱 Users with Phone: {users_with_phone}/{total_users} ({(users_with_phone/total_users)*100:.1f}%)")
    
    # Job posting completeness
    cursor.execute('SELECT COUNT(*) FROM jobs WHERE description IS NOT NULL AND requirements IS NOT NULL')
    complete_jobs = cursor.fetchone()[0]
    
    print(f"💼 Complete Job Descriptions: {complete_jobs}/{total_jobs} ({(complete_jobs/total_jobs)*100:.1f}%)")
    
    # 5. BUSINESS INSIGHTS & RECOMMENDATIONS
    print("\n💡 BUSINESS INSIGHTS & RECOMMENDATIONS")
    print("-" * 45)
    
    # Most popular job category
    cursor.execute('SELECT category, COUNT(*) FROM jobs GROUP BY category ORDER BY COUNT(*) DESC LIMIT 1')
    top_category = cursor.fetchone()
    
    # User-to-job ratio
    user_job_ratio = total_users / total_jobs if total_jobs > 0 else 0
    
    print("🎯 Key Insights:")
    if top_category:
        print(f"  • Most in-demand category: {top_category[0]} ({top_category[1]} jobs)")
    print(f"  • User-to-job ratio: {user_job_ratio:.1f} users per job")
    
    # Government vs private jobs
    cursor.execute('SELECT COUNT(*) FROM jobs WHERE employer_type = "government"')
    gov_jobs = cursor.fetchone()[0]
    gov_percentage = (gov_jobs/total_jobs)*100 if total_jobs > 0 else 0
    
    print(f"  • Government job share: {gov_percentage:.1f}%")
    
    print("\n🚀 Recommendations:")
    if gov_percentage > 50:
        print("  • Strong government job focus - consider promoting to job seekers")
    else:
        print("  • Balanced public-private mix - good for diverse audience")
    
    if user_job_ratio > 2:
        print("  • High user engagement - consider encouraging more job postings")
    else:
        print("  • Good job availability - focus on user acquisition")
    
    # 6. FINAL HEALTH SUMMARY
    print("\n🏥 OVERALL PLATFORM HEALTH")
    print("-" * 30)
    
    health_score = 100
    
    # Deduct points for issues
    if avg_completion and avg_completion < 70:
        health_score -= 10
        print("⚠️  Average profile completion below 70%")
    
    if (users_with_email/total_users) < 0.9:
        health_score -= 5
        print("⚠️  Email coverage below 90%")
    
    if recent_users < 1:
        health_score -= 5
        print("⚠️  Low recent user activity")
    
    if recent_jobs < 1:
        health_score -= 5
        print("⚠️  Low recent job posting activity")
    
    print(f"\n🏆 PLATFORM HEALTH SCORE: {health_score}%")
    
    if health_score >= 95:
        print("🎉 EXCELLENT - Platform is thriving!")
    elif health_score >= 85:
        print("✅ GOOD - Platform is performing well")
    elif health_score >= 70:
        print("⚠️  FAIR - Some areas need attention")
    else:
        print("❌ POOR - Platform needs significant improvement")
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("📊 DATA ANALYSIS COMPLETED")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    generate_data_insights()