#!/usr/bin/env python3
"""
Create demo jobs for testing the recommendation system
"""

import asyncio
import sys
import os
import uuid
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_database_session
from app.models.job import Job, JobStatus, JobType
from app.models.user import User, UserRole

async def create_demo_jobs():
    """Create demo jobs for testing"""
    
    async with get_database_session() as session:
        try:
            # Check if demo jobs already exist
            existing_jobs_result = await session.execute(select(Job))
            existing_jobs = existing_jobs_result.scalars().all()
            
            if len(existing_jobs) > 0:
                print(f"✅ Found {len(existing_jobs)} existing jobs")
                for job in existing_jobs[:3]:
                    print(f"   - {job.title} ({job.status})")
                return
            
            # Get the test employer user
            employer_result = await session.execute(
                select(User).where(User.email == "employer@test.com")
            )
            employer = employer_result.scalar_one_or_none()
            
            if not employer:
                print("❌ Test employer not found! Run create-test-users first.")
                return
                
            print(f"✅ Found test employer: {employer.email}")
            
            # Demo jobs data
            demo_jobs = [
                {
                    "title": "Software Developer - Python/FastAPI",
                    "description": "We are looking for a skilled Python developer to join our team. Experience with FastAPI, SQLAlchemy, and async programming required.",
                    "requirements": "Bachelor's degree in CS, 2+ years Python experience",
                    "responsibilities": "Develop and maintain web applications, work with APIs, collaborate with team",
                    "category": "Technology",
                    "subcategory": "Software Development",
                    "location_city": "Chandigarh",
                    "location_state": "Punjab",
                    "job_type": JobType.FULL_TIME,
                    "salary_min": 50000,
                    "salary_max": 80000,
                    "experience_min": 2,
                    "experience_max": 5,
                    "skills_required": ["Python", "FastAPI", "SQL", "Git"],
                    "status": JobStatus.ACTIVE
                },
                {
                    "title": "Marketing Manager",
                    "description": "Join our marketing team to develop and execute marketing strategies. Experience in digital marketing and social media required.",
                    "requirements": "MBA in Marketing, 3+ years experience",
                    "responsibilities": "Develop marketing campaigns, manage social media, analyze performance",
                    "category": "Marketing",
                    "subcategory": "Digital Marketing",
                    "location_city": "Ludhiana",
                    "location_state": "Punjab",
                    "job_type": JobType.FULL_TIME,
                    "salary_min": 40000,
                    "salary_max": 60000,
                    "experience_min": 3,
                    "experience_max": 7,
                    "skills_required": ["Marketing", "Social Media", "Analytics"],
                    "status": JobStatus.PENDING  # Waiting for admin approval
                },
                {
                    "title": "Data Analyst",
                    "description": "Analyze large datasets to provide insights for business decisions. Experience with Python, SQL, and data visualization tools required.",
                    "requirements": "Bachelor's in Statistics/CS, 1+ years experience",
                    "responsibilities": "Data analysis, reporting, visualization, statistical modeling",
                    "category": "Technology",
                    "subcategory": "Data Science",
                    "location_city": "Amritsar",
                    "location_state": "Punjab",
                    "job_type": JobType.FULL_TIME,
                    "salary_min": 35000,
                    "salary_max": 55000,
                    "experience_min": 1,
                    "experience_max": 4,
                    "skills_required": ["Python", "SQL", "Excel", "Statistics"],
                    "status": JobStatus.ACTIVE
                },
                {
                    "title": "Frontend Developer - React",
                    "description": "Build responsive web applications using React and modern JavaScript. Strong CSS and design skills required.",
                    "requirements": "Bachelor's degree, 2+ years React experience",
                    "responsibilities": "Develop UI components, implement designs, optimize performance",
                    "category": "Technology",
                    "subcategory": "Frontend Development",
                    "location_city": "Jalandhar",
                    "location_state": "Punjab",
                    "job_type": JobType.FULL_TIME,
                    "remote_allowed": True,
                    "salary_min": 45000,
                    "salary_max": 70000,
                    "experience_min": 2,
                    "experience_max": 6,
                    "skills_required": ["React", "JavaScript", "CSS", "HTML"],
                    "status": JobStatus.ACTIVE
                }
            ]
            
            created_jobs = []
            for job_data in demo_jobs:
                job = Job(
                    job_id=f"job_{uuid.uuid4().hex[:12]}",
                    employer_id=employer.user_id,
                    **job_data,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    application_deadline=datetime.utcnow() + timedelta(days=30)
                )
                
                session.add(job)
                created_jobs.append(job.title)
            
            await session.commit()
            
            print(f"✅ Created {len(created_jobs)} demo jobs:")
            for title in created_jobs:
                print(f"   - {title}")
                
        except Exception as e:
            print(f"❌ Error creating demo jobs: {e}")
            await session.rollback()

if __name__ == "__main__":
    print("🚀 Creating demo jobs for Punjab Rozgar Portal...")
    asyncio.run(create_demo_jobs())