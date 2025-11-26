"""
Job management API endpoints aligned to Job model
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc, or_
from typing import List, Optional
from datetime import datetime
import uuid

from app.core.database import get_database
from app.models.job import Job, JobStatus, JobType, EmployerType, JobApplication
from app.models.user import User, UserRole
from app.core.security import verify_token
from app.analytics.tracker import get_analytics_tracker
from pydantic import BaseModel, Field

router = APIRouter(tags=["jobs"])
security = HTTPBearer()

# Pydantic schemas for job operations (mapped to Job model)
class JobCreate(BaseModel):
    title: str
    description: str
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    job_type: str = Field(default="full_time", description="JobType enum value")
    category: str
    subcategory: Optional[str] = None
    location_city: str
    location_state: Optional[str] = "Punjab"
    remote_allowed: bool = False
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = "INR"
    salary_period: Optional[str] = "monthly"
    experience_min: Optional[int] = 0
    experience_max: Optional[int] = None
    education_level: Optional[str] = None
    skills_required: Optional[List[str]] = None
    skills_preferred: Optional[List[str]] = None
    application_deadline: Optional[datetime] = None
    application_method: Optional[str] = "online"
    application_url: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None

class JobPublicResponse(BaseModel):
    job_id: str
    title: str
    description: str
    job_type: Optional[str] = None
    category: str
    location_city: str
    location_state: Optional[str] = None
    remote_allowed: bool
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    education_level: Optional[str] = None
    employer_name: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

def _to_public_response(job: Job) -> JobPublicResponse:
    return JobPublicResponse(
        job_id=job.job_id,
        title=job.title,
        description=job.description,
        job_type=job.job_type.value if job.job_type else None,
        category=job.category,
        location_city=job.location_city,
        location_state=job.location_state,
        remote_allowed=job.remote_allowed,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        experience_min=job.experience_min,
        experience_max=job.experience_max,
        education_level=job.education_level,
        employer_name=job.employer_name,
        status=job.status.value if job.status else None,
        created_at=job.created_at,
        published_at=job.published_at
    )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_database)
):
    """Get current authenticated user via Bearer token"""
    user_id = verify_token(credentials.credentials)
    user_result = await session.execute(select(User).where(User.user_id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=JobPublicResponse)
async def create_job(
    job_data: JobCreate,
    session: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user),
    analytics = Depends(get_analytics_tracker)
):
    """Create a new job posting"""

    # Only employers and admins can create jobs
    if current_user.role not in [UserRole.EMPLOYER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employers can create job postings"
        )

    # Prepare enums and employer fields
    # Normalize job_type (accept hyphenated or different cases from UI)
    raw_type = (job_data.job_type or "").strip()
    norm_type = raw_type.lower().replace("-", "_")
    try:
        jt = JobType(norm_type)
    except ValueError:
        allowed = ", ".join([e.value for e in JobType])
        raise HTTPException(status_code=400, detail=f"Invalid job_type: '{raw_type}'. Allowed: {allowed}")

    employer_type = EmployerType.PRIVATE
    employer_name = current_user.company_name or f"{getattr(current_user, 'first_name', '')} {getattr(current_user, 'last_name', '')}".strip()

    # Create job with DRAFT status
    job = Job(
        job_id=f"job_{uuid.uuid4().hex[:12]}",
        title=job_data.title,
        description=job_data.description,
        requirements=job_data.requirements,
        responsibilities=job_data.responsibilities,
        job_type=jt,
        category=job_data.category,
        subcategory=job_data.subcategory,
        location_city=job_data.location_city,
        location_state=job_data.location_state or "Punjab",
        remote_allowed=job_data.remote_allowed,
        salary_min=job_data.salary_min,
        salary_max=job_data.salary_max,
        salary_currency=job_data.salary_currency,
        salary_period=job_data.salary_period,
        experience_min=job_data.experience_min,
        experience_max=job_data.experience_max,
        education_level=job_data.education_level,
        skills_required=job_data.skills_required or [],
        skills_preferred=job_data.skills_preferred or [],
        employer_id=current_user.user_id,
        employer_name=employer_name,
        employer_type=employer_type,
        application_deadline=job_data.application_deadline,
        application_method=job_data.application_method,
        application_url=job_data.application_url,
        contact_email=job_data.contact_email or current_user.email,
        contact_phone=job_data.contact_phone,
        status=JobStatus.DRAFT,
        published_at=None
    )

    session.add(job)
    await session.commit()
    await session.refresh(job)

    # Track analytics
    await analytics.track_event(
        user_id=current_user.user_id,
        event_name="job_created",
        properties={
            "job_id": job.job_id,
            "job_title": job.title,
            "category": job.category,
            "location_city": job.location_city
        }
    )

    return _to_public_response(job)

# Alias without trailing slash to avoid 307 redirect and CORS header issues
@router.post("", response_model=JobPublicResponse)
async def create_job_alias(
    job_data: JobCreate,
    session: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user),
    analytics = Depends(get_analytics_tracker)
):
    return await create_job(job_data, session, current_user, analytics)

@router.put("/{job_id}/publish")
async def publish_job(
    job_id: str,
    session: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user),
    analytics = Depends(get_analytics_tracker)
):
    """
    Publish a draft job for admin approval
    Employers use this to submit jobs for review
    """
    # Verify user can access this job (using user_id string)
    job_result = await session.execute(
        select(Job).where(
            and_(
                Job.job_id == job_id,
                Job.employer_id == current_user.user_id
            )
        )
    )
    job = job_result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or you don't have permission to modify it"
        )
    
    if job.status != JobStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job must be in draft status to publish. Current status: {job.status.value}"
        )
    
    # Set to pending approval instead of active
    job.status = JobStatus.PENDING_APPROVAL
    job.updated_at = datetime.utcnow()
    # Don't set published_at yet - that happens when admin approves
    
    await session.commit()
    
    # Track analytics
    await analytics.track_event(
        user_id=current_user.user_id,
        event_name="job_submitted_for_approval",
        properties={
            "job_id": job.job_id,
            "job_title": job.title,
            "category": job.category
        }
    )
    
    return {
        "success": True,
        "message": "Job submitted for admin approval",
        "job_id": job.job_id,
        "status": "pending_approval"
    }

@router.get("/my-jobs", response_model=List[JobPublicResponse])
async def get_employer_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = None,
    session: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user),
    analytics = Depends(get_analytics_tracker)
):
    """Get all jobs posted by current employer (including drafts and pending approval)"""
    
    # Only employers and admins can access this
    if current_user.role not in [UserRole.EMPLOYER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employers can access their job listings"
        )
    
    # Build query for current user's jobs (using user_id string, not integer id)
    query = select(Job).where(Job.employer_id == current_user.user_id)
    
    # Optional status filter
    if status_filter:
        try:
            job_status = JobStatus(status_filter)
            query = query.where(Job.status == job_status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status filter: {status_filter}")
    
    # Apply pagination and ordering
    query = query.order_by(desc(Job.created_at)).offset(skip).limit(limit)
    
    # Execute query
    result = await session.execute(query)
    jobs = result.scalars().all()
    
    # Convert to response format
    job_responses = []
    for job in jobs:
        job_responses.append(_to_public_response(job))
    
    # Track analytics
    await analytics.track_event(
        user_id=current_user.user_id,
        event_name="employer_viewed_jobs",
        properties={
            "job_count": len(jobs),
            "status_filter": status_filter
        }
    )
    
    return job_responses

@router.get("/my-stats")
async def get_employer_job_stats(
    session: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """Get job statistics for current employer"""
    
    if current_user.role not in [UserRole.EMPLOYER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employers can access job statistics"
        )
    
    # Get counts by status
    stats = {}
    for job_status in JobStatus:
        count_result = await session.execute(
            select(func.count(Job.id)).where(
                and_(Job.employer_id == current_user.user_id, Job.status == job_status)
            )
        )
        stats[job_status.value] = count_result.scalar() or 0
    
    # Get total applications across all jobs
    total_apps_result = await session.execute(
        select(func.count(JobApplication.id))
        .join(Job, JobApplication.job_id == Job.job_id)
        .where(Job.employer_id == current_user.user_id)
    )
    total_applications = total_apps_result.scalar() or 0
    
    return {
        "job_stats": stats,
        "total_jobs": sum(stats.values()),
        "total_applications": total_applications,
        "active_jobs": stats.get("active", 0),
        "pending_approval": stats.get("pending_approval", 0),
        "draft_jobs": stats.get("draft", 0)
    }

@router.get("/", response_model=List[JobPublicResponse])
async def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    location_city: Optional[str] = None,
    job_type: Optional[str] = None,
    search: Optional[str] = None,
    employer_id: Optional[str] = None,  # Added: Filter by employer's user_id
    only_active: bool = True,
    session: AsyncSession = Depends(get_database),
    analytics = Depends(get_analytics_tracker),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """List all job postings with filters (role-based access)"""
    
    # Check user role for access control
    current_user = None
    if credentials:
        try:
            user_id = verify_token(credentials.credentials)
            user_result = await session.execute(select(User).where(User.user_id == user_id))
            current_user = user_result.scalar_one_or_none()
        except:
            pass  # Allow anonymous access but with restrictions
    
    # Role-based access control:
    # - Job seekers: Can browse all active jobs
    # - Employers: Can browse jobs for competitive analysis (but discouraged)
    # - Admins: Can browse for moderation purposes
    # - Anonymous: Limited access to active jobs only
    
    if current_user and current_user.role == UserRole.ADMIN:
        # Admins can see all jobs including pending for moderation
        pass  # No additional restrictions
    elif current_user and current_user.role == UserRole.EMPLOYER:
        # Employers should generally use their own dashboard, but allow limited browsing
        only_active = True  # Force to only show active jobs
    else:
        # Job seekers and anonymous users - only active jobs
        only_active = True

    # Build query
    query = select(Job)

    if only_active:
        query = query.where(Job.status == JobStatus.ACTIVE)
    
    # Filter by employer
    if employer_id:
        query = query.where(Job.employer_id == employer_id)

    if category:
        query = query.where(Job.category == category)

    if location_city:
        query = query.where(Job.location_city.ilike(f"%{location_city}%"))

    if job_type:
        try:
            jt = JobType(job_type.lower().replace('-', '_'))
            query = query.where(Job.job_type == jt)
        except ValueError:
            allowed = ", ".join([e.value for e in JobType])
            raise HTTPException(status_code=400, detail=f"Invalid job_type filter: '{job_type}'. Allowed: {allowed}")

    if search:
        search_filter = or_(
            Job.title.ilike(f"%{search}%"),
            Job.description.ilike(f"%{search}%"),
            Job.employer_name.ilike(f"%{search}%")
        )
        query = query.where(search_filter)

    # Not expired
    now = datetime.utcnow()
    query = query.where(
        and_(
            or_(Job.expires_at == None, Job.expires_at > now),
            or_(Job.application_deadline == None, Job.application_deadline > now)
        )
    )

    # Order by creation date (newest first)
    query = query.order_by(desc(Job.created_at)).offset(skip).limit(limit)

    result = await session.execute(query)
    jobs = result.scalars().all()

    # Track search analytics if search term provided
    if search:
        await analytics.track_event(
            event_name="job_search",
            properties={
                "search_term": search,
                "category": category,
                "location_city": location_city,
                "job_type": job_type,
                "results_count": len(jobs)
            }
        )

    return [_to_public_response(job) for job in jobs]

@router.get("/{job_id}", response_model=JobPublicResponse)
async def get_job(
    job_id: str,
    session: AsyncSession = Depends(get_database),
    analytics = Depends(get_analytics_tracker)
):
    """Get a specific job posting"""

    # Get job by public job_id
    result = await session.execute(select(Job).where(Job.job_id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Track analytics (anonymous view)
    await analytics.track_event(
        event_name="job_viewed",
        properties={
            "job_id": job.job_id,
            "job_title": job.title,
            "employer_name": job.employer_name,
            "category": job.category
        }
    )
    return _to_public_response(job)

# Note: Application-related endpoints are omitted here due to model schema
# mismatches. We'll add them once the JobApplication model is aligned.
