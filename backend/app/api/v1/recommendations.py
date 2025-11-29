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
import logging

from app.core.database import get_database
from app.models.job import Job, JobStatus, JobType
from app.models.user import User, UserRole
from app.core.security import verify_token
from app.analytics.tracker import get_analytics_tracker

# Set up logger
logger = logging.getLogger(__name__)

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

@router.get("/test", response_model=dict)
async def test_recommendations_auth(
    current_user: User = Depends(get_current_user)
):
    """Test endpoint to debug authentication and role checking"""
    return {
        "success": True,
        "message": "Authentication successful",
        "user": {
            "email": current_user.email,
            "role": current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
            "role_type": type(current_user.role).__name__,
            "user_id": current_user.user_id
        }
    }


@router.get("/", response_model=dict)
async def get_job_recommendations(
    limit: int = Query(10, ge=1, le=50),
    session: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user),
    analytics = Depends(get_analytics_tracker)
):
    """Get personalized job recommendations for job seekers"""
    
    # Check role with better error handling
    user_role_str = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    
    if user_role_str != "job_seeker":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Job recommendations are only available for job seekers. Current role: {user_role_str}"
        )
    
    try:
        # Enhanced recommendation algorithm
        recommendations = await get_personalized_recommendations(
            current_user, session, limit
        )
        
        # If no database jobs found, use mock data
        if not recommendations:
            recommendations = get_mock_recommendations(limit)
            data_source = "mock"
        else:
            data_source = "database"
        
    except Exception as e:
        logger.error(f"Database error in recommendations: {e}")
        # Fallback to mock data if database fails
        recommendations = get_mock_recommendations(limit)
        data_source = "mock_fallback"
    
    # Log analytics
    try:
        await analytics.track_event(
            user_id=current_user.user_id,
            event_type="job_recommendations_viewed",
            properties={
                "recommendations_count": len(recommendations),
                "user_role": user_role_str,
                "data_source": data_source,
                "user_city": getattr(current_user, 'city', None)
            }
        )
    except Exception as analytics_error:
        logger.warning(f"Analytics tracking failed: {analytics_error}")
    
    return {
        "success": True,
        "data": {
            "recommendations": recommendations,
            "total_count": len(recommendations),
            "data_source": data_source,
            "user_profile": {
                "city": getattr(current_user, 'city', None),
                "role": user_role_str
            }
        },
        "message": f"Found {len(recommendations)} job recommendations"
    }


async def get_personalized_recommendations(user: User, session: AsyncSession, limit: int = 10):
    """Get personalized job recommendations based on user profile"""
    try:
        # Get active jobs
        query = select(Job).where(
            and_(
                Job.status == JobStatus.ACTIVE,
                Job.employer_id != user.user_id  # Don't recommend own jobs
            )
        ).order_by(desc(Job.created_at))
        
        jobs_result = await session.execute(query)
        jobs = jobs_result.scalars().all()
        
        recommendations = []
        
        for job in jobs:
            try:
                # Calculate match score based on user profile
                match_score = calculate_match_score(user, job)
                
                # Get employer info
                employer_result = await session.execute(
                    select(User).where(User.user_id == job.employer_id)
                )
                employer = employer_result.scalar_one_or_none()
                
                job_data = {
                    "job_id": job.job_id,
                    "title": job.title,
                    "description": job.description[:300] + "..." if len(job.description) > 300 else job.description,
                    "company_name": getattr(employer, 'name', 'Unknown Company') if employer else "Unknown Company",
                    "location": {
                        "city": job.location_city,
                        "state": job.location_state
                    },
                    "job_type": job.job_type.value if hasattr(job.job_type, 'value') else job.job_type,
                    "category": job.category,
                    "salary": {
                        "min": job.salary_min,
                        "max": job.salary_max,
                        "currency": getattr(job, 'salary_currency', 'INR')
                    },
                    "experience": {
                        "min": job.experience_min,
                        "max": job.experience_max
                    },
                    "skills_required": getattr(job, 'skills_required', []) or [],
                    "remote_allowed": getattr(job, 'remote_allowed', False),
                    "created_at": job.created_at.isoformat() if job.created_at else None,
                    "application_deadline": job.application_deadline.isoformat() if job.application_deadline else None,
                    "match_score": match_score,
                    "match_reasons": get_match_reasons(user, job, match_score)
                }
                recommendations.append(job_data)
                
            except Exception as job_error:
                logger.warning(f"Error processing job {getattr(job, 'job_id', 'unknown')}: {job_error}")
                continue
        
        # Sort by match score descending
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        
        return recommendations[:limit]
        
    except Exception as e:
        logger.error(f"Error in get_personalized_recommendations: {e}")
        return []


def calculate_match_score(user: User, job: Job) -> int:
    """Calculate job match score for a user"""
    score = 50  # Base score
    
    try:
        # Location match
        if hasattr(user, 'city') and user.city:
            if job.location_city and user.city.lower() == job.location_city.lower():
                score += 20
            elif job.location_state and hasattr(user, 'state') and user.state:
                if user.state.lower() == job.location_state.lower():
                    score += 10
        
        # Experience level match
        if hasattr(user, 'experience_years') and user.experience_years is not None:
            if job.experience_min is not None and job.experience_max is not None:
                if job.experience_min <= user.experience_years <= job.experience_max:
                    score += 15
                elif user.experience_years >= job.experience_min:
                    score += 10
        
        # Skills match (if user has skills data)
        if hasattr(user, 'skills') and user.skills:
            job_skills = getattr(job, 'skills_required', []) or []
            if job_skills and isinstance(job_skills, list):
                user_skills = user.skills if isinstance(user.skills, list) else []
                matching_skills = set(skill.lower() for skill in user_skills) & set(skill.lower() for skill in job_skills)
                if matching_skills:
                    score += min(len(matching_skills) * 5, 20)
        
        # Remote work preference
        if getattr(job, 'remote_allowed', False):
            score += 5
        
        # Recent posting bonus
        if job.created_at:
            days_old = (datetime.utcnow() - job.created_at).days
            if days_old < 7:
                score += 10
            elif days_old < 30:
                score += 5
        
    except Exception as e:
        logger.warning(f"Error calculating match score: {e}")
    
    return min(max(score, 0), 100)  # Keep score between 0-100


def get_match_reasons(user: User, job: Job, score: int) -> List[str]:
    """Get list of reasons why this job matches the user"""
    reasons = []
    
    try:
        if hasattr(user, 'city') and user.city and job.location_city:
            if user.city.lower() == job.location_city.lower():
                reasons.append(f"Located in your city ({user.city})")
            elif hasattr(user, 'state') and user.state and job.location_state:
                if user.state.lower() == job.location_state.lower():
                    reasons.append(f"Located in your state ({user.state})")
        
        if getattr(job, 'remote_allowed', False):
            reasons.append("Remote work available")
        
        if job.created_at and (datetime.utcnow() - job.created_at).days < 7:
            reasons.append("Recently posted")
        
        if score >= 80:
            reasons.append("High compatibility match")
        elif score >= 65:
            reasons.append("Good match for your profile")
    
    except Exception as e:
        logger.warning(f"Error getting match reasons: {e}")
    
    return reasons


def get_mock_recommendations(limit: int = 10):
    """Return enhanced mock job recommendations when database is unavailable"""
    mock_jobs = [
        {
            "job_id": "mock_job_1",
            "title": "Software Developer - Python/FastAPI",
            "description": "Join our dynamic team as a Python developer! We're looking for someone skilled in FastAPI, SQLAlchemy, and async programming. You'll work on building scalable web applications and APIs for our Punjab-based clients.",
            "company_name": "TechSoft Solutions Pvt Ltd",
            "location": {
                "city": "Chandigarh", 
                "state": "Punjab"
            },
            "job_type": "full_time",
            "category": "Technology",
            "salary": {
                "min": 50000,
                "max": 80000,
                "currency": "INR"
            },
            "experience": {
                "min": 2,
                "max": 5
            },
            "skills_required": ["Python", "FastAPI", "SQL", "Git", "PostgreSQL"],
            "remote_allowed": True,
            "created_at": "2024-11-28T10:00:00",
            "application_deadline": "2024-12-28T23:59:59",
            "match_score": 92,
            "match_reasons": ["High demand skills", "Remote work available", "Salary matches expectation"]
        },
        {
            "job_id": "mock_job_2",
            "title": "Digital Marketing Manager",
            "description": "Lead our digital marketing initiatives and help grow Punjab-based businesses. Experience in social media marketing, SEO, content strategy, and performance analytics required. Great opportunity for career growth.",
            "company_name": "Creative Agency Punjab",
            "location": {
                "city": "Ludhiana",
                "state": "Punjab"
            },
            "job_type": "full_time", 
            "category": "Marketing",
            "salary": {
                "min": 40000,
                "max": 60000,
                "currency": "INR"
            },
            "experience": {
                "min": 3,
                "max": 7
            },
            "skills_required": ["Digital Marketing", "Social Media", "SEO", "Google Analytics", "Content Marketing"],
            "remote_allowed": True,
            "created_at": "2024-11-27T15:30:00",
            "application_deadline": "2024-12-27T23:59:59",
            "match_score": 88,
            "match_reasons": ["Growing industry", "Remote flexibility", "Leadership opportunity"]
        },
        {
            "job_id": "mock_job_3",
            "title": "Data Analyst - Government Sector",
            "description": "Analyze large datasets to provide insights for policy decisions in Punjab Government. Work with census data, economic indicators, and social metrics. Experience with Python, SQL, and data visualization tools required.",
            "company_name": "Government of Punjab",
            "location": {
                "city": "Amritsar",
                "state": "Punjab"
            },
            "job_type": "full_time",
            "category": "Government", 
            "salary": {
                "min": 35000,
                "max": 55000,
                "currency": "INR"
            },
            "experience": {
                "min": 1,
                "max": 4
            },
            "skills_required": ["Python", "SQL", "Excel", "Statistics", "Tableau"],
            "remote_allowed": False,
            "created_at": "2024-11-26T09:15:00",
            "application_deadline": "2024-12-26T23:59:59",
            "match_score": 85,
            "match_reasons": ["Government job security", "Social impact", "Good for fresh graduates"]
        },
        {
            "job_id": "mock_job_4",
            "title": "Frontend Developer - React Specialist",
            "description": "Build beautiful, responsive web applications using React and modern JavaScript. Work with a talented team to create user-friendly interfaces for Punjab's growing tech ecosystem. Strong CSS and design skills required.",
            "company_name": "Digital Innovations Pvt Ltd",
            "location": {
                "city": "Jalandhar",
                "state": "Punjab"
            },
            "job_type": "full_time",
            "category": "Technology",
            "salary": {
                "min": 45000,
                "max": 70000,
                "currency": "INR"
            },
            "experience": {
                "min": 2,
                "max": 6
            },
            "skills_required": ["React", "JavaScript", "CSS3", "HTML5", "Redux"],
            "remote_allowed": True,
            "created_at": "2024-11-25T14:20:00",
            "application_deadline": "2024-12-25T23:59:59",
            "match_score": 90,
            "match_reasons": ["Modern tech stack", "Creative environment", "Hybrid work model"]
        },
        {
            "job_id": "mock_job_5", 
            "title": "Customer Support Executive",
            "description": "Provide excellent customer service for our clients across Punjab. Handle inquiries, resolve issues, and maintain customer satisfaction. Good communication skills in Hindi, Punjabi, and English required.",
            "company_name": "Punjab Customer Care Services",
            "location": {
                "city": "Patiala",
                "state": "Punjab"
            },
            "job_type": "full_time",
            "category": "Customer Service",
            "salary": {
                "min": 25000,
                "max": 35000,
                "currency": "INR"
            },
            "experience": {
                "min": 0,
                "max": 3
            },
            "skills_required": ["Communication", "Hindi", "Punjabi", "Customer Service", "MS Office"],
            "remote_allowed": False,
            "created_at": "2024-11-24T11:45:00",
            "application_deadline": "2024-12-24T23:59:59",
            "match_score": 82,
            "match_reasons": ["Entry level friendly", "Local language skills valued", "Stable employment"]
        },
        {
            "job_id": "mock_job_6",
            "title": "Graphic Designer",
            "description": "Create visual content for digital and print media. Design logos, brochures, social media graphics, and marketing materials for Punjab-based businesses. Adobe Creative Suite expertise required.",
            "company_name": "Creative Studio Punjab",
            "location": {
                "city": "Mohali",
                "state": "Punjab"
            },
            "job_type": "full_time",
            "category": "Design",
            "salary": {
                "min": 30000,
                "max": 50000,
                "currency": "INR"
            },
            "experience": {
                "min": 1,
                "max": 4
            },
            "skills_required": ["Adobe Photoshop", "Adobe Illustrator", "CorelDRAW", "Creative Design", "Brand Identity"],
            "remote_allowed": True,
            "created_at": "2024-11-23T16:00:00",
            "application_deadline": "2024-12-23T23:59:59",
            "match_score": 87,
            "match_reasons": ["Creative field", "Portfolio-based growth", "Flexible work options"]
        }
    ]
    
    # Randomize the order for variety
    random.shuffle(mock_jobs)
    return mock_jobs[:limit]
