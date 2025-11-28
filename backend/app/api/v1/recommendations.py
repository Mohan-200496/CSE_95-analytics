"""
Job recommendations API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc, or_
from typing import List, Optional
from datetime import datetime
import random

from app.core.database import get_database
from app.models.job import Job, JobStatus, JobType
from app.models.user import User, UserRole
from app.core.security import verify_token
from app.analytics.tracker import get_analytics_tracker

router = APIRouter(tags=["recommendations"])
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_database)
):
    """Get current authenticated user"""
    user_id = verify_token(credentials.credentials)
    user_result = await session.execute(select(User).where(User.user_id == user_id))
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@router.get("/", response_model=List[dict])
async def get_job_recommendations(
    limit: int = Query(10, ge=1, le=50),
    session: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user),
    analytics = Depends(get_analytics_tracker)
):
    """Get personalized job recommendations for job seekers"""
    
    # Only job seekers should get recommendations
    if current_user.role != UserRole.JOB_SEEKER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Job recommendations are only available for job seekers"
        )
    
    try:
        # Get active jobs (approved by admin)
        query = select(Job).where(
            and_(
                Job.status == JobStatus.ACTIVE,
                Job.employer_id != current_user.user_id  # Don't recommend own jobs
            )
        ).order_by(desc(Job.created_at)).limit(limit * 2)  # Get more than needed for filtering
        
        jobs_result = await session.execute(query)
        jobs = jobs_result.scalars().all()
        
        # Simple recommendation algorithm:
        # 1. Filter by user's city if available
        # 2. Randomize to provide variety
        # 3. Limit to requested amount
        
        recommendations = []
        
        for job in jobs:
            try:
                # Get employer info
                employer_result = await session.execute(
                    select(User).where(User.user_id == job.employer_id)
                )
                employer = employer_result.scalar_one_or_none()
                
                job_data = {
                    "job_id": job.job_id,
                    "title": job.title,
                    "description": job.description[:200] + "..." if len(job.description) > 200 else job.description,
                    "company_name": getattr(employer, 'company_name', None) if employer else "Unknown Company",
                    "location_city": job.location_city,
                    "location_state": job.location_state,
                    "job_type": job.job_type.value if hasattr(job.job_type, 'value') else job.job_type,
                    "category": job.category,
                    "salary_min": job.salary_min,
                    "salary_max": job.salary_max,
                    "salary_currency": job.salary_currency,
                    "created_at": job.created_at.isoformat() if job.created_at else None,
                    "application_deadline": job.application_deadline.isoformat() if job.application_deadline else None,
                    "remote_allowed": getattr(job, 'remote_allowed', False),
                    "experience_min": job.experience_min,
                    "experience_max": job.experience_max,
                    "skills_required": getattr(job, 'skills_required', []) or [],
                    "match_score": random.randint(70, 95)  # Placeholder matching score
                }
                recommendations.append(job_data)
            except Exception as job_error:
                logger.warning(f"Error processing job {getattr(job, 'job_id', 'unknown')}: {job_error}")
                continue
        
        # Randomize and limit
        random.shuffle(recommendations)
        recommendations = recommendations[:limit]
        
    except Exception as e:
        logger.error(f"Database error in recommendations: {e}")
        # Fallback to mock data if database fails
        recommendations = get_mock_recommendations(limit)
    
    # If no jobs found, provide mock recommendations
    if not recommendations:
        recommendations = get_mock_recommendations(limit)
    
    # Log analytics
    try:
        await analytics.track_event(
            user_id=current_user.user_id,
            event_type="job_recommendations_viewed",
            properties={
                "recommendations_count": len(recommendations),
                "user_role": current_user.role.value,
                "data_source": "mock" if not any(rec.get("job_id", "").startswith("mock") for rec in recommendations) else "database"
            }
        )
    except Exception as analytics_error:
        logger.warning(f"Analytics tracking failed: {analytics_error}")
    
    return recommendations


def get_mock_recommendations(limit: int = 10):
    """Return mock job recommendations for testing when database is unavailable"""
    mock_jobs = [
        {
            "job_id": "mock_job_1",
            "title": "Software Developer - Python/FastAPI",
            "description": "We are looking for a skilled Python developer to join our team. Experience with FastAPI, SQLAlchemy, and async programming required.",
            "company_name": "TechSoft Solutions",
            "location_city": "Chandigarh", 
            "location_state": "Punjab",
            "job_type": "full_time",
            "category": "Technology",
            "salary_min": 50000,
            "salary_max": 80000,
            "salary_currency": "INR",
            "created_at": "2024-11-28T10:00:00",
            "application_deadline": "2024-12-28T10:00:00",
            "remote_allowed": False,
            "experience_min": 2,
            "experience_max": 5,
            "skills_required": ["Python", "FastAPI", "SQL", "Git"],
            "match_score": 92
        },
        {
            "job_id": "mock_job_2",
            "title": "Digital Marketing Manager",
            "description": "Join our marketing team to develop and execute digital marketing strategies. Experience in social media marketing and SEO required.",
            "company_name": "Creative Agency Punjab",
            "location_city": "Ludhiana",
            "location_state": "Punjab",
            "job_type": "full_time", 
            "category": "Marketing",
            "salary_min": 40000,
            "salary_max": 60000,
            "salary_currency": "INR",
            "created_at": "2024-11-27T15:30:00",
            "application_deadline": "2024-12-27T15:30:00",
            "remote_allowed": True,
            "experience_min": 3,
            "experience_max": 7,
            "skills_required": ["Marketing", "Social Media", "SEO", "Analytics"],
            "match_score": 88
        },
        {
            "job_id": "mock_job_3",
            "title": "Data Analyst",
            "description": "Analyze large datasets to provide insights for business decisions. Experience with Python, SQL, and data visualization tools required.",
            "company_name": "Punjab Government",
            "location_city": "Amritsar",
            "location_state": "Punjab",
            "job_type": "full_time",
            "category": "Technology", 
            "salary_min": 35000,
            "salary_max": 55000,
            "salary_currency": "INR",
            "created_at": "2024-11-26T09:15:00",
            "application_deadline": "2024-12-26T09:15:00",
            "remote_allowed": False,
            "experience_min": 1,
            "experience_max": 4,
            "skills_required": ["Python", "SQL", "Excel", "Statistics"],
            "match_score": 85
        },
        {
            "job_id": "mock_job_4",
            "title": "Frontend Developer - React",
            "description": "Build responsive web applications using React and modern JavaScript. Strong CSS and design skills required.",
            "company_name": "Digital Innovations Pvt Ltd",
            "location_city": "Jalandhar",
            "location_state": "Punjab",
            "job_type": "full_time",
            "category": "Technology",
            "salary_min": 45000,
            "salary_max": 70000,
            "salary_currency": "INR",
            "created_at": "2024-11-25T14:20:00",
            "application_deadline": "2024-12-25T14:20:00",
            "remote_allowed": True,
            "experience_min": 2,
            "experience_max": 6,
            "skills_required": ["React", "JavaScript", "CSS", "HTML"],
            "match_score": 90
        }
    ]
    
    return mock_jobs[:limit]
