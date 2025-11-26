"""
Job Application schemas
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class ApplicationCreate(BaseModel):
    """Schema for creating a job application"""
    job_id: str = Field(..., description="Job ID to apply for")
    cover_letter: Optional[str] = Field(None, max_length=5000, description="Cover letter")
    resume_url: Optional[str] = Field(None, max_length=500, description="Resume URL")
    portfolio_url: Optional[str] = Field(None, max_length=500, description="Portfolio URL")
    years_of_experience: Optional[int] = Field(None, ge=0, description="Years of experience")
    current_location: Optional[str] = Field(None, max_length=100, description="Current location")
    skills: Optional[List[str]] = Field(default_factory=list, description="List of skills")
    source: Optional[str] = Field(None, max_length=100, description="How you found this job")

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "JOB123",
                "cover_letter": "I am interested in this position...",
                "resume_url": "https://example.com/resume.pdf",
                "years_of_experience": 3,
                "current_location": "Chandigarh",
                "skills": ["Python", "FastAPI", "SQL"]
            }
        }


class ApplicationUpdate(BaseModel):
    """Schema for updating application materials"""
    cover_letter: Optional[str] = Field(None, max_length=5000)
    resume_url: Optional[str] = Field(None, max_length=500)
    portfolio_url: Optional[str] = Field(None, max_length=500)


class ApplicationResponse(BaseModel):
    """Schema for application response"""
    application_id: str
    job_id: str
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    location: Optional[str] = None
    status: str
    applied_at: datetime
    updated_at: Optional[datetime] = None
    cover_letter: Optional[str] = None
    resume_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    viewed_by_employer: Optional[bool] = False
    interview_scheduled: Optional[bool] = False
    interview_date: Optional[datetime] = None
    interview_mode: Optional[str] = None
    interview_location: Optional[str] = None
    feedback: Optional[str] = None

    class Config:
        from_attributes = True


class ApplicationListResponse(BaseModel):
    """Schema for list of applications"""
    applications: List[ApplicationResponse]
    total: int
    limit: int
    offset: int
