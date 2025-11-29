#!/usr/bin/env python3
"""
Add diverse sample jobs to Punjab Rozgar Portal
Creates jobs across different categories, locations, and types
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import uuid
from typing import List, Dict, Any

from backend.app.core.database import get_async_db_url, Base
from backend.app.models.job import Job, JobType, JobStatus, EmployerType
from backend.app.models.user import User

# Database connection
DATABASE_URL = get_async_db_url()
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Sample job data with diverse categories
SAMPLE_JOBS = [
    {
        "title": "Software Developer - Government Portal",
        "description": "Develop and maintain government web applications using modern technologies. Work on citizen-facing services and digital governance solutions.",
        "requirements": "Bachelor's in Computer Science, 2+ years Python/JavaScript experience, Knowledge of web frameworks, Database management skills",
        "responsibilities": "Develop web applications, Maintain government portals, Collaborate with teams, Ensure data security, Write clean code",
        "job_type": JobType.FULL_TIME,
        "category": "Information Technology",
        "subcategory": "Software Development",
        "location_city": "Chandigarh",
        "location_area": "Sector 17",
        "salary_min": 40000,
        "salary_max": 70000,
        "experience_min": 2,
        "experience_max": 5,
        "education_level": "Bachelor's Degree",
        "skills_required": ["Python", "JavaScript", "SQL", "Git", "Web Development"],
        "skills_preferred": ["React", "FastAPI", "PostgreSQL", "Docker"],
        "employer_type": EmployerType.GOVERNMENT,
        "government_scheme": "Digital Punjab Initiative",
        "benefits": ["Health Insurance", "Provident Fund", "Leave Travel Allowance", "Professional Development"],
        "working_hours": "9:00 AM - 6:00 PM",
        "age_limit_max": 35
    },
    {
        "title": "Data Analyst - Punjab Analytics",
        "description": "Analyze government data to derive insights for policy making. Work with large datasets and create visualizations for decision makers.",
        "requirements": "Master's in Statistics/Data Science, 3+ years analytics experience, Proficiency in R/Python, Strong analytical skills",
        "responsibilities": "Data analysis and reporting, Create dashboards, Statistical modeling, Policy recommendations, Data visualization",
        "job_type": JobType.FULL_TIME,
        "category": "Data Science",
        "subcategory": "Business Analytics",
        "location_city": "Ludhiana",
        "location_area": "Civil Lines",
        "salary_min": 50000,
        "salary_max": 85000,
        "experience_min": 3,
        "experience_max": 7,
        "education_level": "Master's Degree",
        "skills_required": ["Python", "R", "SQL", "Statistics", "Data Visualization"],
        "skills_preferred": ["Tableau", "Power BI", "Machine Learning", "Jupyter"],
        "employer_type": EmployerType.GOVERNMENT,
        "government_scheme": "Punjab Data Initiative",
        "benefits": ["Health Insurance", "Research Allowance", "Conference Attendance", "Flexible Hours"],
        "working_hours": "Flexible",
        "age_limit_max": 40
    },
    {
        "title": "Digital Marketing Specialist",
        "description": "Drive digital marketing campaigns for Punjab tourism and government initiatives. Manage social media and online presence.",
        "requirements": "Bachelor's in Marketing/Communication, 2+ years digital marketing experience, Social media expertise, SEO knowledge",
        "responsibilities": "Social media management, SEO optimization, Content creation, Campaign analysis, Brand promotion",
        "job_type": JobType.FULL_TIME,
        "category": "Marketing",
        "subcategory": "Digital Marketing",
        "location_city": "Amritsar",
        "location_area": "Heritage Street",
        "salary_min": 35000,
        "salary_max": 60000,
        "experience_min": 2,
        "experience_max": 5,
        "education_level": "Bachelor's Degree",
        "skills_required": ["Digital Marketing", "SEO", "Social Media", "Content Writing", "Analytics"],
        "skills_preferred": ["Google Ads", "Facebook Marketing", "Photoshop", "Video Editing"],
        "employer_type": EmployerType.GOVERNMENT,
        "government_scheme": "Digital Punjab Campaign",
        "benefits": ["Creative Freedom", "Travel Opportunities", "Health Insurance", "Performance Bonus"],
        "working_hours": "10:00 AM - 7:00 PM"
    },
    {
        "title": "Mechanical Engineer - Industrial Development",
        "description": "Support industrial development projects across Punjab. Work on manufacturing automation and process improvement initiatives.",
        "requirements": "B.Tech in Mechanical Engineering, 3+ years industry experience, AutoCAD proficiency, Project management skills",
        "responsibilities": "Project planning, Technical design, Quality control, Team coordination, Process optimization",
        "job_type": JobType.FULL_TIME,
        "category": "Engineering",
        "subcategory": "Mechanical Engineering",
        "location_city": "Jalandhar",
        "location_area": "Industrial Area",
        "salary_min": 45000,
        "salary_max": 80000,
        "experience_min": 3,
        "experience_max": 8,
        "education_level": "Bachelor's Degree",
        "skills_required": ["Mechanical Engineering", "AutoCAD", "Project Management", "Quality Control"],
        "skills_preferred": ["SolidWorks", "PLC Programming", "Lean Manufacturing", "Six Sigma"],
        "employer_type": EmployerType.PUBLIC_SECTOR,
        "government_scheme": "Make in Punjab",
        "benefits": ["Technical Training", "Health Insurance", "Performance Incentives", "Skill Development"],
        "working_hours": "8:00 AM - 5:00 PM"
    },
    {
        "title": "Healthcare Administrator - Rural Health",
        "description": "Manage healthcare delivery in rural Punjab areas. Coordinate with medical staff and ensure quality healthcare services.",
        "requirements": "Master's in Hospital Administration/Public Health, 3+ years healthcare experience, Leadership skills, Rural health knowledge",
        "responsibilities": "Healthcare management, Staff coordination, Policy implementation, Community outreach, Quality assurance",
        "job_type": JobType.FULL_TIME,
        "category": "Healthcare",
        "subcategory": "Administration",
        "location_city": "Bathinda",
        "location_area": "Civil Hospital",
        "salary_min": 55000,
        "salary_max": 90000,
        "experience_min": 3,
        "experience_max": 10,
        "education_level": "Master's Degree",
        "skills_required": ["Healthcare Management", "Public Health", "Leadership", "Communication"],
        "skills_preferred": ["Healthcare IT", "Rural Health", "Policy Development", "Community Engagement"],
        "employer_type": EmployerType.GOVERNMENT,
        "government_scheme": "Ayushman Bharat Punjab",
        "benefits": ["Medical Allowance", "Rural Posting Allowance", "Health Insurance", "Career Growth"],
        "working_hours": "Emergency on-call"
    },
    {
        "title": "Agricultural Extension Officer",
        "description": "Support farmers with modern agricultural practices and technology adoption. Promote sustainable farming in Punjab.",
        "requirements": "B.Sc Agriculture/Horticulture, Field experience preferred, Local language fluency, Communication skills",
        "responsibilities": "Farmer training, Technology demonstration, Crop planning guidance, Market linkage support, Data collection",
        "job_type": JobType.FULL_TIME,
        "category": "Agriculture",
        "subcategory": "Extension Services",
        "location_city": "Patiala",
        "location_area": "Agricultural University",
        "salary_min": 30000,
        "salary_max": 50000,
        "experience_min": 1,
        "experience_max": 5,
        "education_level": "Bachelor's Degree",
        "skills_required": ["Agriculture", "Punjabi Language", "Communication", "Field Work"],
        "skills_preferred": ["Organic Farming", "Precision Agriculture", "Soil Science", "Pest Management"],
        "employer_type": EmployerType.GOVERNMENT,
        "government_scheme": "Krishi Vigyan Kendra",
        "benefits": ["Vehicle Allowance", "Field Allowance", "Training Programs", "Rural Posting Benefits"],
        "working_hours": "Field work timing"
    },
    {
        "title": "UI/UX Designer - Government Apps",
        "description": "Design user-friendly interfaces for government mobile apps and web services. Focus on citizen experience and accessibility.",
        "requirements": "Bachelor's in Design/HCI, 2+ years UI/UX experience, Figma/Adobe XD proficiency, User research skills",
        "responsibilities": "User interface design, User experience research, Prototyping, Usability testing, Design systems",
        "job_type": JobType.CONTRACT,
        "category": "Design",
        "subcategory": "UI/UX Design",
        "location_city": "Mohali",
        "location_area": "IT City",
        "remote_allowed": True,
        "salary_min": 45000,
        "salary_max": 75000,
        "experience_min": 2,
        "experience_max": 6,
        "education_level": "Bachelor's Degree",
        "skills_required": ["UI Design", "UX Design", "Figma", "User Research", "Prototyping"],
        "skills_preferred": ["Adobe Creative Suite", "Sketch", "InVision", "HTML/CSS"],
        "employer_type": EmployerType.GOVERNMENT,
        "government_scheme": "Digital Punjab Interface",
        "benefits": ["Creative Environment", "Flexible Hours", "Design Tools", "Portfolio Building"],
        "working_hours": "Flexible with core hours"
    },
    {
        "title": "Financial Analyst - Budget Planning",
        "description": "Analyze government budgets and financial data. Support financial planning and policy decisions for Punjab state departments.",
        "requirements": "Master's in Finance/Economics, CA/CFA preferred, 3+ years financial analysis experience, Government finance knowledge",
        "responsibilities": "Budget analysis, Financial reporting, Policy impact assessment, Cost-benefit analysis, Variance analysis",
        "job_type": JobType.FULL_TIME,
        "category": "Finance",
        "subcategory": "Financial Analysis",
        "location_city": "Chandigarh",
        "location_area": "Secretariat",
        "salary_min": 60000,
        "salary_max": 100000,
        "experience_min": 3,
        "experience_max": 8,
        "education_level": "Master's Degree",
        "skills_required": ["Financial Analysis", "Excel", "Budgeting", "Public Finance", "Reporting"],
        "skills_preferred": ["SAP", "Tableau", "Advanced Excel", "Government Accounting"],
        "employer_type": EmployerType.GOVERNMENT,
        "benefits": ["Professional Development", "Government Pension", "Health Benefits", "Study Leave"],
        "working_hours": "9:00 AM - 6:00 PM"
    },
    {
        "title": "Cybersecurity Analyst - Government Systems",
        "description": "Secure government IT infrastructure and protect citizen data. Monitor security threats and implement protective measures.",
        "requirements": "B.Tech in IT/Cybersecurity, Security certifications preferred, 2+ years security experience, Incident response skills",
        "responsibilities": "Security monitoring, Threat analysis, Incident response, Security policy implementation, Vulnerability assessment",
        "job_type": JobType.FULL_TIME,
        "category": "Information Technology",
        "subcategory": "Cybersecurity",
        "location_city": "Chandigarh",
        "location_area": "IT Park",
        "salary_min": 55000,
        "salary_max": 95000,
        "experience_min": 2,
        "experience_max": 7,
        "education_level": "Bachelor's Degree",
        "skills_required": ["Cybersecurity", "Network Security", "Incident Response", "Risk Assessment"],
        "skills_preferred": ["CISSP", "CEH", "SIEM Tools", "Penetration Testing"],
        "employer_type": EmployerType.GOVERNMENT,
        "government_scheme": "Cyber Punjab Initiative",
        "benefits": ["Security Clearance", "Certification Support", "Technology Training", "High Security Environment"],
        "working_hours": "24/7 rotation shifts"
    },
    {
        "title": "Content Writer - Government Communication",
        "description": "Create content for government websites, publications, and citizen communication. Write policy documents and public announcements.",
        "requirements": "Master's in English/Journalism, 2+ years content writing experience, Government communication knowledge, Multilingual skills",
        "responsibilities": "Content creation, Policy documentation, Press releases, Website content, Social media content",
        "job_type": JobType.PART_TIME,
        "category": "Content",
        "subcategory": "Technical Writing",
        "location_city": "Ludhiana",
        "location_area": "Press Club",
        "remote_allowed": True,
        "salary_min": 25000,
        "salary_max": 40000,
        "experience_min": 2,
        "experience_max": 5,
        "education_level": "Master's Degree",
        "skills_required": ["Content Writing", "English", "Punjabi", "Government Knowledge"],
        "skills_preferred": ["SEO Writing", "WordPress", "Social Media", "Photography"],
        "employer_type": EmployerType.GOVERNMENT,
        "benefits": ["Flexible Schedule", "Work from Home", "Publishing Credits", "Media Access"],
        "working_hours": "Part-time flexible"
    }
]

async def create_sample_jobs():
    """Create sample jobs in the database"""
    async with AsyncSessionLocal() as db:
        try:
            # Get existing employer users
            result = await db.execute(
                text("SELECT user_id, email, full_name FROM users WHERE role = 'employer' LIMIT 5")
            )
            employers = result.fetchall()
            
            if not employers:
                print("No employer accounts found. Creating a sample employer...")
                # Create a sample employer
                employer_id = f"employer_{uuid.uuid4().hex[:8]}"
                await db.execute(
                    text("""
                        INSERT INTO users (user_id, email, full_name, role, is_active, created_at)
                        VALUES (:user_id, :email, :full_name, 'employer', true, :created_at)
                    """),
                    {
                        "user_id": employer_id,
                        "email": "sample.employer@punjab.gov.in",
                        "full_name": "Punjab Government Employer",
                        "created_at": datetime.utcnow()
                    }
                )
                await db.commit()
                employers = [(employer_id, "sample.employer@punjab.gov.in", "Punjab Government Employer")]
            
            created_jobs = []
            
            for i, job_data in enumerate(SAMPLE_JOBS):
                # Cycle through available employers
                employer = employers[i % len(employers)]
                employer_id, employer_email, employer_name = employer
                
                # Generate unique job ID
                job_id = f"PJB{datetime.now().year}{uuid.uuid4().hex[:8].upper()}"
                
                # Create job entry
                job_entry = {
                    "job_id": job_id,
                    "title": job_data["title"],
                    "description": job_data["description"],
                    "requirements": job_data["requirements"],
                    "responsibilities": job_data["responsibilities"],
                    "job_type": job_data["job_type"].value,
                    "category": job_data["category"],
                    "subcategory": job_data.get("subcategory"),
                    "location_city": job_data["location_city"],
                    "location_state": "Punjab",
                    "location_area": job_data.get("location_area"),
                    "remote_allowed": job_data.get("remote_allowed", False),
                    "salary_min": job_data.get("salary_min"),
                    "salary_max": job_data.get("salary_max"),
                    "salary_currency": "INR",
                    "salary_period": "monthly",
                    "experience_min": job_data.get("experience_min", 0),
                    "experience_max": job_data.get("experience_max"),
                    "education_level": job_data.get("education_level"),
                    "skills_required": str(job_data.get("skills_required", [])).replace("'", '"'),
                    "skills_preferred": str(job_data.get("skills_preferred", [])).replace("'", '"'),
                    "employer_id": employer_id,
                    "employer_name": employer_name,
                    "employer_type": job_data["employer_type"].value,
                    "application_deadline": (datetime.now() + timedelta(days=30)).isoformat(),
                    "application_method": "online",
                    "contact_email": employer_email,
                    "resume_required": True,
                    "status": "active",  # Make jobs active immediately for demo
                    "created_at": (datetime.now() - timedelta(days=i)).isoformat(),  # Stagger creation dates
                    "published_at": (datetime.now() - timedelta(days=i)).isoformat(),
                    "expires_at": (datetime.now() + timedelta(days=30)).isoformat(),
                    "views_count": 50 + (i * 25),  # Demo view counts
                    "applications_count": 5 + (i * 3),  # Demo application counts
                    "featured": i < 3,  # Make first 3 jobs featured
                    "urgent": i == 0,  # Make first job urgent
                    "government_scheme": job_data.get("government_scheme"),
                    "benefits": str(job_data.get("benefits", [])).replace("'", '"'),
                    "working_hours": job_data.get("working_hours"),
                    "age_limit_max": job_data.get("age_limit_max"),
                    "slug": f"{job_data['title'].lower().replace(' ', '-').replace(',', '')}-{job_id.lower()}"
                }
                
                # Insert job
                columns = ", ".join(job_entry.keys())
                placeholders = ", ".join([f":{key}" for key in job_entry.keys()])
                
                await db.execute(
                    text(f"INSERT INTO jobs ({columns}) VALUES ({placeholders})"),
                    job_entry
                )
                
                created_jobs.append({
                    "job_id": job_id,
                    "title": job_data["title"],
                    "category": job_data["category"],
                    "location": job_data["location_city"],
                    "employer": employer_name
                })
                
                print(f"✅ Created job: {job_data['title']} ({job_id})")
            
            await db.commit()
            
            print(f"\n🎉 Successfully created {len(created_jobs)} sample jobs!")
            print("\n📋 Jobs Summary:")
            for job in created_jobs:
                print(f"  • {job['title']} - {job['category']} - {job['location']} ({job['job_id']})")
                
            return created_jobs
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error creating jobs: {str(e)}")
            raise

async def main():
    """Main function"""
    print("🚀 Adding sample jobs to Punjab Rozgar Portal...")
    
    try:
        jobs = await create_sample_jobs()
        print(f"\n✅ Process completed successfully!")
        print(f"📊 {len(jobs)} diverse jobs added across multiple categories")
        print("🔍 Jobs are now available for browsing and recommendations")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)