#!/usr/bin/env python3
"""
Simple job creation script for Punjab Rozgar Portal
"""

import sqlite3
import uuid
from datetime import datetime, timedelta
import json

def create_sample_jobs():
    """Create sample jobs directly using SQLite"""
    db_path = "backend/punjab_rozgar.db"
    
    # Sample jobs data
    jobs_data = [
        {
            "title": "Software Developer - Government Portal",
            "description": "Develop and maintain government web applications using modern technologies. Work on citizen-facing services and digital governance solutions.",
            "category": "Information Technology",
            "location_city": "Chandigarh",
            "salary_min": 40000,
            "salary_max": 70000,
            "experience_min": 2,
            "skills": ["Python", "JavaScript", "SQL", "Git", "Web Development"]
        },
        {
            "title": "Data Analyst - Punjab Analytics", 
            "description": "Analyze government data to derive insights for policy making. Work with large datasets and create visualizations.",
            "category": "Data Science",
            "location_city": "Ludhiana",
            "salary_min": 50000,
            "salary_max": 85000,
            "experience_min": 3,
            "skills": ["Python", "R", "SQL", "Statistics", "Data Visualization"]
        },
        {
            "title": "Digital Marketing Specialist",
            "description": "Drive digital marketing campaigns for Punjab tourism and government initiatives. Manage social media presence.",
            "category": "Marketing", 
            "location_city": "Amritsar",
            "salary_min": 35000,
            "salary_max": 60000,
            "experience_min": 2,
            "skills": ["Digital Marketing", "SEO", "Social Media", "Content Writing"]
        },
        {
            "title": "Mechanical Engineer - Industrial Development",
            "description": "Support industrial development projects across Punjab. Work on manufacturing automation and process improvement.",
            "category": "Engineering",
            "location_city": "Jalandhar", 
            "salary_min": 45000,
            "salary_max": 80000,
            "experience_min": 3,
            "skills": ["Mechanical Engineering", "AutoCAD", "Project Management"]
        },
        {
            "title": "Healthcare Administrator - Rural Health",
            "description": "Manage healthcare delivery in rural Punjab areas. Coordinate with medical staff and ensure quality services.",
            "category": "Healthcare",
            "location_city": "Bathinda",
            "salary_min": 55000,
            "salary_max": 90000,
            "experience_min": 3,
            "skills": ["Healthcare Management", "Public Health", "Leadership"]
        },
        {
            "title": "Agricultural Extension Officer", 
            "description": "Support farmers with modern agricultural practices and technology adoption. Promote sustainable farming.",
            "category": "Agriculture",
            "location_city": "Patiala",
            "salary_min": 30000,
            "salary_max": 50000,
            "experience_min": 1,
            "skills": ["Agriculture", "Punjabi Language", "Communication"]
        },
        {
            "title": "UI/UX Designer - Government Apps",
            "description": "Design user-friendly interfaces for government mobile apps and web services. Focus on citizen experience.",
            "category": "Design",
            "location_city": "Mohali",
            "salary_min": 45000,
            "salary_max": 75000,
            "experience_min": 2,
            "skills": ["UI Design", "UX Design", "Figma", "User Research"]
        },
        {
            "title": "Cybersecurity Analyst - Government Systems",
            "description": "Secure government IT infrastructure and protect citizen data. Monitor security threats and implement protection.",
            "category": "Information Technology",
            "location_city": "Chandigarh",
            "salary_min": 55000,
            "salary_max": 95000,
            "experience_min": 2,
            "skills": ["Cybersecurity", "Network Security", "Incident Response"]
        }
    ]
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get a sample employer
        cursor.execute("SELECT user_id, email, first_name, last_name FROM users WHERE role = 'employer' LIMIT 1")
        employer = cursor.fetchone()
        
        if not employer:
            print("No employer found. Creating sample employer...")
            employer_id = f"employer_{uuid.uuid4().hex[:8]}"
            cursor.execute("""
                INSERT INTO users (user_id, email, first_name, last_name, hashed_password, role, status, created_at, email_verified)
                VALUES (?, ?, ?, ?, ?, 'employer', 'active', ?, 1)
            """, (employer_id, "sample.employer@punjab.gov.in", "Punjab", "Government", "hashed_password_placeholder", datetime.now().isoformat()))
            conn.commit()
            employer = (employer_id, "sample.employer@punjab.gov.in", "Punjab", "Government")
        
        employer_id, employer_email, first_name, last_name = employer
        employer_name = f"{first_name} {last_name}" if last_name else first_name
        
        created_jobs = []
        
        for i, job in enumerate(jobs_data):
            job_id = f"PJB{datetime.now().year}{uuid.uuid4().hex[:8].upper()}"
            created_at = datetime.now() - timedelta(days=i)
            
            # Insert job with required fields
            cursor.execute("""
                INSERT INTO jobs (
                    job_id, title, description, requirements, responsibilities,
                    job_type, category, location_city, location_state,
                    salary_min, salary_max, salary_currency, salary_period,
                    experience_min, experience_max, education_level,
                    skills_required, employer_id, employer_name, employer_type,
                    application_deadline, contact_email, status,
                    created_at, published_at, expires_at,
                    views_count, applications_count, featured, urgent
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_id, job["title"], job["description"],
                f"Required skills: {', '.join(job['skills'])}, {job['experience_min']}+ years experience",
                "Execute assigned tasks, collaborate with team, ensure quality delivery",
                "full_time", job["category"], job["location_city"], "Punjab",
                job["salary_min"], job["salary_max"], "INR", "monthly",
                job["experience_min"], job["experience_min"] + 3, "Bachelor's Degree",
                json.dumps(job["skills"]), employer_id, employer_name, "government",
                (datetime.now() + timedelta(days=30)).isoformat(), employer_email, "active",
                created_at.isoformat(), created_at.isoformat(), (datetime.now() + timedelta(days=30)).isoformat(),
                50 + (i * 25), 5 + (i * 3), 1 if i < 3 else 0, 1 if i == 0 else 0
            ))
            
            created_jobs.append({
                "job_id": job_id,
                "title": job["title"],
                "category": job["category"],
                "location": job["location_city"]
            })
            
            print(f"✅ Created: {job['title']} ({job_id})")
        
        conn.commit()
        conn.close()
        
        print(f"\n🎉 Successfully created {len(created_jobs)} jobs!")
        return created_jobs
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return []

if __name__ == "__main__":
    print("🚀 Creating sample jobs for Punjab Rozgar Portal...")
    jobs = create_sample_jobs()
    
    if jobs:
        print("\n📋 Jobs Created:")
        for job in jobs:
            print(f"  • {job['title']} - {job['category']} - {job['location']}")
        print("\n🔍 Jobs are now available for browsing and recommendations!")
    else:
        print("❌ Failed to create jobs")