"""
Job Applications API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import uuid

from app.core.database import get_database
from app.core.security import verify_token
from app.models.user import User
from app.models.job import Job, JobApplication, ApplicationStatus
from app.schemas.application import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationUpdate,
    ApplicationListResponse
)

router = APIRouter()
security = HTTPBearer()


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


@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    application_data: ApplicationCreate,
    session: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """
    Apply for a job
    """
    # Check if job exists and is active
    job_result = await session.execute(
        select(Job).where(Job.job_id == application_data.job_id)
    )
    job = job_result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if not job.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job is not active"
        )
    
    # Check if user already applied for this job
    existing_app = await session.execute(
        select(JobApplication).where(
            and_(
                JobApplication.job_id == application_data.job_id,
                JobApplication.user_id == current_user.user_id
            )
        )
    )
    
    if existing_app.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied for this job"
        )
    
    # Create application
    application = JobApplication(
        application_id=f"APP-{uuid.uuid4().hex[:12].upper()}",
        job_id=application_data.job_id,
        user_id=current_user.user_id,
        status=ApplicationStatus.APPLIED,
        cover_letter=application_data.cover_letter,
        resume_url=application_data.resume_url,
        portfolio_url=application_data.portfolio_url,
        applicant_name=current_user.name,
        applicant_email=current_user.email,
        applicant_phone=getattr(current_user, 'phone', None),
        applicant_experience=application_data.years_of_experience,
        applicant_location=application_data.current_location,
        applicant_skills=application_data.skills or [],
        source=application_data.source,
        applied_at=datetime.utcnow()
    )
    
    session.add(application)
    await session.commit()
    await session.refresh(application)
    
    # Get job details for response
    return ApplicationResponse(
        application_id=application.application_id,
        job_id=application.job_id,
        job_title=job.title,
        company_name=job.employer_name,
        status=application.status.value,
        applied_at=application.applied_at,
        updated_at=application.updated_at,
        cover_letter=application.cover_letter,
        resume_url=application.resume_url,
        portfolio_url=application.portfolio_url
    )


@router.get("/", response_model=ApplicationListResponse)
async def list_my_applications(
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's applications
    """
    # Build query
    query = select(JobApplication, Job).join(
        Job, JobApplication.job_id == Job.job_id
    ).where(
        JobApplication.user_id == current_user.user_id
    )
    
    # Apply status filter
    if status_filter:
        try:
            status_enum = ApplicationStatus(status_filter)
            query = query.where(JobApplication.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )
    
    # Order by most recent first
    query = query.order_by(JobApplication.applied_at.desc())
    
    # Get total count
    count_query = select(func.count()).select_from(JobApplication).where(
        JobApplication.user_id == current_user.user_id
    )
    if status_filter:
        count_query = count_query.where(JobApplication.status == status_enum)
    
    total_result = await session.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    query = query.limit(limit).offset(offset)
    
    result = await session.execute(query)
    applications_with_jobs = result.all()
    
    # Build response
    applications = []
    for app, job in applications_with_jobs:
        applications.append(ApplicationResponse(
            application_id=app.application_id,
            job_id=app.job_id,
            job_title=job.title,
            company_name=job.employer_name,
            location=job.location_city,
            status=app.status.value,
            applied_at=app.applied_at,
            updated_at=app.updated_at,
            cover_letter=app.cover_letter,
            resume_url=app.resume_url,
            portfolio_url=app.portfolio_url,
            viewed_by_employer=app.viewed_by_employer,
            interview_scheduled=app.interview_scheduled,
            interview_date=app.interview_date
        ))
    
    return ApplicationListResponse(
        applications=applications,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: str,
    session: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """
    Get specific application details
    """
    result = await session.execute(
        select(JobApplication, Job).join(
            Job, JobApplication.job_id == Job.job_id
        ).where(
            and_(
                JobApplication.application_id == application_id,
                JobApplication.user_id == current_user.user_id
            )
        )
    )
    
    app_with_job = result.first()
    
    if not app_with_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    app, job = app_with_job
    
    return ApplicationResponse(
        application_id=app.application_id,
        job_id=app.job_id,
        job_title=job.title,
        company_name=job.employer_name,
        location=job.location_city,
        status=app.status.value,
        applied_at=app.applied_at,
        updated_at=app.updated_at,
        cover_letter=app.cover_letter,
        resume_url=app.resume_url,
        portfolio_url=app.portfolio_url,
        viewed_by_employer=app.viewed_by_employer,
        interview_scheduled=app.interview_scheduled,
        interview_date=app.interview_date,
        interview_mode=app.interview_mode,
        interview_location=app.interview_location,
        feedback=app.feedback
    )


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def withdraw_application(
    application_id: str,
    session: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """
    Withdraw an application
    """
    result = await session.execute(
        select(JobApplication).where(
            and_(
                JobApplication.application_id == application_id,
                JobApplication.user_id == current_user.user_id
            )
        )
    )
    
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Only allow withdrawal if not already selected or rejected
    if application.status in [ApplicationStatus.SELECTED, ApplicationStatus.REJECTED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot withdraw application with status: {application.status.value}"
        )
    
    application.status = ApplicationStatus.WITHDRAWN
    application.updated_at = datetime.utcnow()
    
    await session.commit()
