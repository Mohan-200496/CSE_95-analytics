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
            "remote_allowed": job.remote_allowed,
            "experience_min": job.experience_min,
            "experience_max": job.experience_max,
            "skills_required": job.skills_required or [],
            "match_score": random.randint(70, 95)  # Placeholder matching score
        }
        recommendations.append(job_data)
    
    # Randomize and limit
    random.shuffle(recommendations)
    recommendations = recommendations[:limit]
    
    # Log analytics
    await analytics.track_event(
        user_id=current_user.user_id,
        event_type="job_recommendations_viewed",
        properties={
            "recommendations_count": len(recommendations),
            "user_role": current_user.role.value
        }
    )
    
    return recommendations
