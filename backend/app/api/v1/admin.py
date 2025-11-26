"""
Admin management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, or_, update, delete
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
import json

from app.core.database import get_database
from app.models.user import User, UserProfile, UserRole
from app.models.job import Job, JobApplication, JobStatus
from app.models.admin import AdminAction, SystemConfig
from app.models.analytics import AnalyticsEvent
from app.core.security import verify_token
from app.analytics.tracker import get_analytics_tracker
from pydantic import BaseModel

router = APIRouter(tags=["admin"])
security = HTTPBearer()

# Pydantic schemas
class AdminStatsResponse(BaseModel):
    total_users: int
    active_users: int
    total_jobs: int
    active_jobs: int
    total_applications: int
    pending_applications: int
    recent_signups: int
    recent_job_posts: int

class UserManagementResponse(BaseModel):
    id: str
    email: str
    user_type: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]
    total_applications: Optional[int] = None
    total_jobs_posted: Optional[int] = None
    # Real-time analytics data
    profile_views: int = 0
    recent_activity_count: int = 0
    last_seen: Optional[datetime] = None
    is_online: bool = False
    session_count_today: int = 0
    profile_completion: float = 0.0
    engagement_score: float = 0.0

class JobManagementResponse(BaseModel):
    job_id: str
    title: str
    employer_name: str
    location_city: str
    job_type: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    salary_period: Optional[str] = None
    status: str
    created_at: datetime
    employer_id: str
    application_count: int

class AdminActionResponse(BaseModel):
    id: str
    admin_id: str
    action_type: str
    target_type: str
    target_id: str
    description: str
    created_at: datetime

class SystemConfigUpdate(BaseModel):
    key: str
    value: str
    description: Optional[str] = None

class UserStatusUpdate(BaseModel):
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_database)
):
    """Get current authenticated admin user via Bearer token"""
    user_id = verify_token(credentials.credentials)
    user_result = await session.execute(select(User).where(User.user_id == user_id))
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role not in [UserRole.ADMIN, UserRole.MODERATOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return user

async def log_admin_action(
    session: AsyncSession,
    admin_id: str,
    action_type: str,
    target_type: str,
    target_id: str,
    description: str
):
    """Log admin action"""
    # Align with AdminAction model field names
    admin_action = AdminAction(
        admin_id=admin_id,
        action_type=action_type,
        action_description=description,
        target_type=target_type,
        target_id=target_id
    )
    session.add(admin_action)
    await session.commit()

@router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(
    session: AsyncSession = Depends(get_database),
    current_admin: User = Depends(get_current_admin)
):
    """Get system statistics for admin dashboard"""
    
    # Total users
    total_users_result = await session.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar() or 0
    
    # Active users
    active_users_result = await session.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )
    active_users = active_users_result.scalar() or 0
    
    # Total jobs
    total_jobs_result = await session.execute(select(func.count(Job.id)))
    total_jobs = total_jobs_result.scalar() or 0
    
    # Active jobs
    active_jobs_result = await session.execute(
        select(func.count(Job.id)).where(Job.is_active == True)
    )
    active_jobs = active_jobs_result.scalar() or 0
    
    # Total applications
    total_applications_result = await session.execute(select(func.count(JobApplication.id)))
    total_applications = total_applications_result.scalar() or 0
    
    # Pending applications
    pending_applications_result = await session.execute(
        select(func.count(JobApplication.id)).where(JobApplication.status == "pending")
    )
    pending_applications = pending_applications_result.scalar() or 0
    
    # Recent signups (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_signups_result = await session.execute(
        select(func.count(User.id)).where(User.created_at >= seven_days_ago)
    )
    recent_signups = recent_signups_result.scalar() or 0
    
    # Recent job posts (last 7 days)
    recent_jobs_result = await session.execute(
        select(func.count(Job.id)).where(Job.created_at >= seven_days_ago)
    )
    recent_job_posts = recent_jobs_result.scalar() or 0
    
    return AdminStatsResponse(
        total_users=total_users,
        active_users=active_users,
        total_jobs=total_jobs,
        active_jobs=active_jobs,
        total_applications=total_applications,
        pending_applications=pending_applications,
        recent_signups=recent_signups,
        recent_job_posts=recent_job_posts
    )

@router.get("/users", response_model=List[UserManagementResponse])
async def list_users_for_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_verified: Optional[bool] = None,
    search: Optional[str] = None,
    session: AsyncSession = Depends(get_database),
    current_admin: User = Depends(get_current_admin)
):
    """List all users for admin management"""
    
    # Build query
    query = select(User)
    
    if user_type:
        query = query.where(User.user_type == user_type)
    
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    if is_verified is not None:
        query = query.where(User.is_verified == is_verified)
    
    if search:
        search_filter = or_(
            User.email.ilike(f"%{search}%"),
            User.id.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
    
    # Order by creation date (newest first)
    query = query.order_by(desc(User.created_at))
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    result = await session.execute(query)
    users = result.scalars().all()
    
    # Get additional stats for each user
    user_responses = []
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    for user in users:
        user_response = UserManagementResponse(
            id=user.id,
            email=user.email,
            user_type=user.user_type,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            last_login=user.last_login
        )
        
        # Get user-specific stats
        if user.user_type == "job_seeker":
            apps_result = await session.execute(
                select(func.count(JobApplication.id)).where(JobApplication.applicant_id == user.id)
            )
            user_response.total_applications = apps_result.scalar() or 0
        
        elif user.user_type == "employer":
            jobs_result = await session.execute(
                select(func.count(Job.id)).where(Job.posted_by == user.id)
            )
            user_response.total_jobs_posted = jobs_result.scalar() or 0
        
        # Get real-time analytics data
        try:
            # Profile views from analytics events
            profile_views_result = await session.execute(
                select(func.count(AnalyticsEvent.id)).where(
                    and_(
                        AnalyticsEvent.event_name == "user_profile_viewed",
                        AnalyticsEvent.properties.like(f'%"viewed_user_id":"{user.id}"%')
                    )
                )
            )
            user_response.profile_views = profile_views_result.scalar() or 0
            
            # Recent activity count (last 24 hours)
            recent_activity_result = await session.execute(
                select(func.count(AnalyticsEvent.id)).where(
                    and_(
                        AnalyticsEvent.user_id == user.id,
                        AnalyticsEvent.timestamp >= now - timedelta(hours=24)
                    )
                )
            )
            user_response.recent_activity_count = recent_activity_result.scalar() or 0
            
            # Last seen (most recent analytics event)
            last_activity_result = await session.execute(
                select(AnalyticsEvent.timestamp).where(
                    AnalyticsEvent.user_id == user.id
                ).order_by(desc(AnalyticsEvent.timestamp)).limit(1)
            )
            last_activity = last_activity_result.scalar()
            user_response.last_seen = last_activity
            
            # Is online (activity within last 5 minutes)
            if last_activity:
                user_response.is_online = (now - last_activity).total_seconds() < 300
            
            # Session count today
            session_count_result = await session.execute(
                select(func.count(func.distinct(AnalyticsEvent.session_id))).where(
                    and_(
                        AnalyticsEvent.user_id == user.id,
                        AnalyticsEvent.timestamp >= today_start
                    )
                )
            )
            user_response.session_count_today = session_count_result.scalar() or 0
            
            # Calculate engagement score (events per day since joining)
            days_since_joined = max(1, (now - user.created_at).days)
            total_events_result = await session.execute(
                select(func.count(AnalyticsEvent.id)).where(AnalyticsEvent.user_id == user.id)
            )
            total_events = total_events_result.scalar() or 0
            user_response.engagement_score = round(total_events / days_since_joined, 2)
            
            # Get profile completion from user profile
            profile_result = await session.execute(
                select(UserProfile).where(UserProfile.user_id == user.id)
            )
            profile = profile_result.scalar_one_or_none()
            
            # Calculate profile completion
            if profile:
                total_fields = 9
                completed_fields = sum([
                    bool(profile.full_name),
                    bool(profile.phone),
                    bool(profile.location),
                    bool(profile.bio),
                    bool(profile.skills),
                    bool(profile.experience_years is not None),
                    bool(profile.education),
                    bool(profile.resume_url),
                    bool(profile.portfolio_url)
                ])
                user_response.profile_completion = round((completed_fields / total_fields) * 100, 1)
            
        except Exception as e:
            print(f"Error getting analytics for user {user.id}: {e}")
            # Continue with default values if analytics query fails
        
        user_responses.append(user_response)
    
    return user_responses

# Special endpoint for initial admin setup (no auth required for first admin)
@router.post("/initial-admin-setup")
async def initial_admin_setup(
    email: str,
    session: AsyncSession = Depends(get_database)
):
    """
    Promote first user to admin (for initial setup only)
    This endpoint works only if no admin users exist
    """
    # Check if any admin users already exist
    existing_admin_result = await session.execute(
        select(User).where(User.role == UserRole.ADMIN)
    )
    existing_admin = existing_admin_result.scalar_one_or_none()
    
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin users already exist. Use regular promotion endpoint."
        )
    
    # Find user by email
    user_result = await session.execute(select(User).where(User.email == email))
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found: {email}"
        )
    
    # Promote to admin
    user.role = UserRole.ADMIN
    user.updated_at = datetime.utcnow()
    await session.commit()
    
    return {
        "success": True,
        "message": f"User {email} promoted to admin",
        "user_id": user.user_id,
        "role": user.role.value
    }

@router.post("/users/{user_id}/promote")
async def promote_user_to_admin(
    user_id: str,
    session: AsyncSession = Depends(get_database),
    current_admin: User = Depends(get_current_admin)
):
    """Promote a user to admin role (requires admin auth)"""
    
    # Find user
    user_result = await session.execute(select(User).where(User.user_id == user_id))
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.role == UserRole.ADMIN:
        return {
            "success": True,
            "message": f"User is already an admin",
            "user_id": user.user_id,
            "role": user.role.value
        }
    
    # Promote to admin
    user.role = UserRole.ADMIN
    user.updated_at = datetime.utcnow()
    await session.commit()
    
    # Log admin action
    await log_admin_action(
        session=session,
        admin_id=current_admin.user_id,
        action_type="PROMOTE_USER",
        target_type="user",
        target_id=user.user_id,
        description=f"Promoted {user.email} to admin role"
    )
    
    return {
        "success": True,
        "message": f"User {user.email} promoted to admin",
        "user_id": user.user_id,
        "role": user.role.value
    }

@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    status_update: UserStatusUpdate,
    session: AsyncSession = Depends(get_database),
    current_admin: User = Depends(get_current_admin),
    analytics = Depends(get_analytics_tracker)
):
    """Update user status (activate/deactivate, verify/unverify)"""
    
    # Get user
    user_result = await session.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user status
    update_data = status_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    
    await session.commit()
    await session.refresh(user)
    
    # Log admin action
    await log_admin_action(
        session=session,
        admin_id=current_admin.id,
        action_type="user_status_update",
        target_type="user",
        target_id=user_id,
        description=f"Updated user status: {update_data}"
    )
    
    # Track analytics
    await analytics.track_event(
        user_id=current_admin.id,
        event_name="admin_user_status_updated",
        properties={
            "target_user_id": user_id,
            "changes": update_data
        }
    )
    
    return {"message": "User status updated successfully"}

@router.put("/users/{user_id}/promote-admin")
async def promote_user_to_admin(
    user_id: str,
    session: AsyncSession = Depends(get_database),
    current_admin: User = Depends(get_current_admin)
):
    """Promote a user to admin role (requires admin access)"""
    analytics = get_analytics_tracker()
    
    # Get target user
    user_result = await session.execute(select(User).where(User.user_id == user_id))
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role == UserRole.ADMIN:
        return {"message": "User is already an admin", "user_id": user_id, "role": "admin"}
    
    # Update user role to admin
    previous_role = user.role.value
    user.role = UserRole.ADMIN
    user.updated_at = datetime.utcnow()
    await session.commit()
    
    # Log admin action
    await log_admin_action(
        session=session,
        admin_id=current_admin.user_id,
        action_type="user_promote",
        target_type="user",
        target_id=user_id,
        description=f"Promoted user from {previous_role} to admin"
    )
    
    # Track analytics
    await analytics.track_event(
        user_id=current_admin.id,
        event_name="admin_user_promoted",
        properties={
            "target_user_id": user_id,
            "previous_role": previous_role,
            "new_role": "admin"
        }
    )
    
    return {
        "message": f"User promoted to admin successfully",
        "user_id": user_id,
        "previous_role": previous_role,
        "new_role": "admin"
    }

@router.post("/setup/initial-admin")
async def create_initial_admin(
    session: AsyncSession = Depends(get_database)
):
    """Special endpoint to promote the first admin - no auth required for initial setup"""
    
    # Check if any admin exists
    admin_result = await session.execute(
        select(User).where(User.role == UserRole.ADMIN)
    )
    existing_admin = admin_result.scalar_one_or_none()
    
    if existing_admin:
        raise HTTPException(
            status_code=400, 
            detail="Admin already exists. Use the regular promotion endpoint."
        )
    
    # Find the admin@punjabrozgar.gov.pk user
    user_result = await session.execute(
        select(User).where(User.email == "admin@punjabrozgar.gov.pk")
    )
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=404, 
            detail="Admin user admin@punjabrozgar.gov.pk not found"
        )
    
    if user.role == UserRole.ADMIN:
        return {"message": "User is already an admin", "email": user.email, "role": "admin"}
    
    # Update user role to admin
    previous_role = user.role.value
    user.role = UserRole.ADMIN
    user.updated_at = datetime.utcnow()
    await session.commit()
    
    return {
        "message": f"Initial admin promoted successfully",
        "email": user.email,
        "user_id": user.user_id,
        "previous_role": previous_role,
        "new_role": "admin"
    }

@router.get("/jobs", response_model=List[JobManagementResponse])
async def list_jobs_for_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = None,
    job_type: Optional[str] = None,
    search: Optional[str] = None,
    session: AsyncSession = Depends(get_database),
    current_admin: User = Depends(get_current_admin)
):
    """List all jobs for admin management"""
    
    # Build query
    query = select(Job)
    
    if status_filter:
        try:
            js = JobStatus(status_filter)
            query = query.where(Job.status == js)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid job status filter")
    
    if job_type:
        try:
            from app.models.job import JobType
            jt = JobType(job_type)
            query = query.where(Job.job_type == jt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid job type filter")
    
    if search:
        search_filter = or_(
            Job.title.ilike(f"%{search}%"),
            Job.employer_name.ilike(f"%{search}%"),
            Job.location_city.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
    
    # Order by creation date (newest first)
    query = query.order_by(desc(Job.created_at))
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    result = await session.execute(query)
    jobs = result.scalars().all()
    
    # Get stats for each job
    job_responses = []
    for job in jobs:
        # Get application count
        app_count_result = await session.execute(
            select(func.count(JobApplication.id)).where(JobApplication.job_id == job.job_id)
        )
        application_count = app_count_result.scalar() or 0
        
        job_responses.append(JobManagementResponse(
            job_id=job.job_id,
            title=job.title,
            employer_name=job.employer_name,
            location_city=job.location_city,
            job_type=job.job_type.value if job.job_type else None,
            salary_min=job.salary_min,
            salary_max=job.salary_max,
            salary_currency=job.salary_currency,
            salary_period=job.salary_period,
            status=job.status.value if job.status else "draft",
            created_at=job.created_at,
            employer_id=job.employer_id,
            application_count=application_count
        ))
    
    return job_responses

class UpdateJobStatus(BaseModel):
    status: str

@router.put("/jobs/{job_id}/status")
async def update_job_status(
    job_id: str,
    payload: UpdateJobStatus,
    session: AsyncSession = Depends(get_database),
    current_admin: User = Depends(get_current_admin),
    analytics = Depends(get_analytics_tracker)
):
    """Update job status (approve/pause/close). Uses public job_id."""

    # Get job by public job_id
    job_result = await session.execute(select(Job).where(Job.job_id == job_id))
    job = job_result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Validate and set status
    try:
        new_status = JobStatus(payload.status)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job status")

    job.status = new_status
    if new_status == JobStatus.ACTIVE and not job.published_at:
        job.published_at = datetime.utcnow()
    job.updated_at = datetime.utcnow()

    await session.commit()

    # Log admin action
    await log_admin_action(
        session=session,
        admin_id=current_admin.id,
        action_type="job_status_update",
        target_type="job",
        target_id=job.job_id,
        description=f"Set job status to: {new_status.value}"
    )

    # Track analytics
    await analytics.track_event(
        user_id=current_admin.id,
        event_name="admin_job_status_updated",
        properties={
            "job_id": job.job_id,
            "status": new_status.value,
            "job_title": job.title
        }
    )

    return {"message": "Job status updated successfully", "job_id": job.job_id, "status": new_status.value}

@router.post("/jobs/{job_id}/approve")
async def approve_job(
    job_id: str,
    session: AsyncSession = Depends(get_database),
    current_admin: User = Depends(get_current_admin),
    analytics = Depends(get_analytics_tracker)
):
    """Approve a pending job and make it active"""
    
    # Get job by public job_id
    job_result = await session.execute(select(Job).where(Job.job_id == job_id))
    job = job_result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status == JobStatus.ACTIVE:
        return {"message": "Job is already approved and active", "job_id": job.job_id, "status": "active"}

    # Update job to active status
    job.status = JobStatus.ACTIVE
    if not job.published_at:
        job.published_at = datetime.utcnow()
    job.updated_at = datetime.utcnow()

    await session.commit()

    # Log admin action
    await log_admin_action(
        session=session,
        admin_id=current_admin.user_id,
        action_type="JOB_APPROVED",
        target_type="job",
        target_id=job.job_id,
        description=f"Approved job: {job.title}"
    )

    # Track analytics
    await analytics.track_event(
        user_id=current_admin.id,
        event_name="admin_job_approved",
        properties={
            "job_id": job.job_id,
            "job_title": job.title,
            "employer_id": job.employer_id
        }
    )

    return {
        "success": True,
        "message": "Job approved successfully",
        "job_id": job.job_id,
        "status": "active"
    }

@router.post("/jobs/{job_id}/reject")
async def reject_job(
    job_id: str,
    reason: str = "Does not meet platform guidelines",
    session: AsyncSession = Depends(get_database),
    current_admin: User = Depends(get_current_admin),
    analytics = Depends(get_analytics_tracker)
):
    """Reject a pending job and set to draft status"""
    
    # Get job by public job_id
    job_result = await session.execute(select(Job).where(Job.job_id == job_id))
    job = job_result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status == JobStatus.DRAFT:
        return {"message": "Job is already in draft status", "job_id": job.job_id, "status": "draft"}

    # Update job to draft status (rejected)
    job.status = JobStatus.DRAFT
    job.updated_at = datetime.utcnow()
    
    # Add rejection reason to job metadata if it exists
    if hasattr(job, 'admin_notes') or 'admin_notes' in job.__dict__:
        job.admin_notes = reason

    await session.commit()

    # Log admin action
    await log_admin_action(
        session=session,
        admin_id=current_admin.user_id,
        action_type="JOB_REJECTED",
        target_type="job",
        target_id=job.job_id,
        description=f"Rejected job: {job.title}. Reason: {reason}"
    )

    # Track analytics
    await analytics.track_event(
        user_id=current_admin.id,
        event_name="admin_job_rejected",
        properties={
            "job_id": job.job_id,
            "job_title": job.title,
            "rejection_reason": reason,
            "employer_id": job.employer_id
        }
    )

    return {
        "success": True,
        "message": "Job rejected successfully",
        "job_id": job.job_id,
        "status": "draft",
        "reason": reason
    }

@router.get("/jobs/pending-approval")
async def get_pending_jobs(
    session: AsyncSession = Depends(get_database),
    current_admin: User = Depends(get_current_admin),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get all jobs pending admin approval"""
    
    # Get jobs with pending approval status
    jobs_result = await session.execute(
        select(Job)
        .where(Job.status == JobStatus.PENDING_APPROVAL)
        .order_by(desc(Job.created_at))
        .limit(limit)
        .offset(offset)
    )
    jobs = jobs_result.scalars().all()
    
    # Get total count
    count_result = await session.execute(
        select(func.count(Job.id))
        .where(Job.status == JobStatus.PENDING_APPROVAL)
    )
    total_count = count_result.scalar() or 0
    
    job_list = []
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
            "location": job.location,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "job_type": job.job_type.value if job.job_type else None,
            "experience_level": job.experience_level,
            "created_at": job.created_at.isoformat(),
            "employer": {
                "name": f"{employer.first_name} {employer.last_name}" if employer else "Unknown",
                "email": employer.email if employer else None,
                "company": employer.company_name if employer and hasattr(employer, 'company_name') else None
            }
        }
        job_list.append(job_data)
    
    return {
        "jobs": job_list,
        "total_count": total_count,
        "showing": len(job_list),
        "offset": offset,
        "limit": limit
    }

@router.delete("/jobs/{job_id}")
async def delete_job_admin(
    job_id: str,
    session: AsyncSession = Depends(get_database),
    current_admin: User = Depends(get_current_admin),
    analytics = Depends(get_analytics_tracker)
):
    """Delete a job (admin only)"""
    
    # Get job by public job_id
    job_result = await session.execute(select(Job).where(Job.job_id == job_id))
    job = job_result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_title = job.title
    
    # Delete job (cascade will handle applications)
    await session.delete(job)
    await session.commit()
    
    # Log admin action
    await log_admin_action(
        session=session,
        admin_id=current_admin.id,
        action_type="job_delete",
        target_type="job",
        target_id=job_id,
        description=f"Deleted job: {job_title}"
    )
    
    # Track analytics
    await analytics.track_event(
        user_id=current_admin.id,
        event_name="admin_job_deleted",
        properties={
            "job_id": job_id,
            "job_title": job_title
        }
    )
    
    return {"message": "Job deleted successfully"}

@router.get("/actions", response_model=List[AdminActionResponse])
async def get_admin_actions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    action_type: Optional[str] = None,
    target_type: Optional[str] = None,
    session: AsyncSession = Depends(get_database),
    current_admin: User = Depends(get_current_admin)
):
    """Get admin action log"""
    
    query = select(AdminAction)
    
    if action_type:
        query = query.where(AdminAction.action_type == action_type)
    
    if target_type:
        query = query.where(AdminAction.target_type == target_type)
    
    query = query.order_by(desc(AdminAction.created_at)).offset(skip).limit(limit)
    
    result = await session.execute(query)
    actions = result.scalars().all()
    
    return [
        AdminActionResponse(
            id=action.id,
            admin_id=action.admin_id,
            action_type=action.action_type,
            target_type=action.target_type,
            target_id=action.target_id,
            description=action.description,
            created_at=action.created_at
        )
        for action in actions
    ]

@router.get("/system/config")
async def get_system_config(
    session: AsyncSession = Depends(get_database),
    current_admin: User = Depends(get_current_admin)
):
    """Get system configuration"""
    
    result = await session.execute(select(SystemConfig))
    configs = result.scalars().all()
    
    return {config.key: {"value": config.value, "description": config.description} for config in configs}

@router.put("/system/config")
async def update_system_config(
    config_update: SystemConfigUpdate,
    session: AsyncSession = Depends(get_database),
    current_admin: User = Depends(get_current_admin),
    analytics = Depends(get_analytics_tracker)
):
    """Update system configuration"""
    
    # Get or create config
    config_result = await session.execute(
        select(SystemConfig).where(SystemConfig.key == config_update.key)
    )
    config = config_result.scalar_one_or_none()
    
    if not config:
        config = SystemConfig(
            key=config_update.key,
            value=config_update.value,
            description=config_update.description
        )
        session.add(config)
    else:
        config.value = config_update.value
        if config_update.description:
            config.description = config_update.description
        config.updated_at = datetime.utcnow()
    
    await session.commit()
    
    # Log admin action
    await log_admin_action(
        session=session,
        admin_id=current_admin.id,
        action_type="system_config_update",
        target_type="config",
        target_id=config_update.key,
        description=f"Updated config {config_update.key} to {config_update.value}"
    )
    
    # Track analytics
    await analytics.track_event(
        user_id=current_admin.id,
        event_name="admin_config_updated",
        properties={
            "config_key": config_update.key,
            "config_value": config_update.value
        }
    )
    
    return {"message": "Configuration updated successfully"}

@router.get("/live-stats")
async def live_stats_stream(
    session: AsyncSession = Depends(get_database),
    current_admin: User = Depends(get_current_admin)
):
    """Server-Sent Events endpoint for real-time admin dashboard updates"""
    
    async def generate_stats():
        while True:
            try:
                # Get real-time stats
                now = datetime.utcnow()
                
                # Basic user counts
                total_users_result = await session.execute(select(func.count(User.id)))
                total_users = total_users_result.scalar() or 0
                
                active_users_result = await session.execute(
                    select(func.count(User.id)).where(User.is_active == True)
                )
                active_users = active_users_result.scalar() or 0
                
                # Online users (activity in last 5 minutes)
                online_users_result = await session.execute(
                    select(func.count(func.distinct(AnalyticsEvent.user_id))).where(
                        AnalyticsEvent.timestamp >= now - timedelta(minutes=5)
                    )
                )
                online_users = online_users_result.scalar() or 0
                
                # Recent activity (last hour)
                recent_activity_result = await session.execute(
                    select(func.count(AnalyticsEvent.id)).where(
                        AnalyticsEvent.timestamp >= now - timedelta(hours=1)
                    )
                )
                recent_activity = recent_activity_result.scalar() or 0
                
                # Create SSE data
                stats = {
                    "timestamp": now.isoformat(),
                    "total_users": total_users,
                    "active_users": active_users,
                    "online_users": online_users,
                    "recent_activity": recent_activity
                }
                
                # Format as SSE
                yield f"data: {json.dumps(stats)}\n\n"
                
                # Wait 10 seconds before next update
                await asyncio.sleep(10)
                
            except Exception as e:
                # Send error as SSE event
                error_data = {
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
                yield f"data: {json.dumps(error_data)}\n\n"
                await asyncio.sleep(30)  # Wait longer on error
    
    return StreamingResponse(
        generate_stats(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )
