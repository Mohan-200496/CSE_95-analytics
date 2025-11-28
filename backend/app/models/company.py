"""
Company models for Punjab Rozgar Portal
Employer organization management
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Index, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any, Optional

from app.core.database import Base


class Company(Base):
    """
    Company/Organization model for employers
    """
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Company Information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    industry = Column(String(100), index=True)
    company_size = Column(String(50))  # e.g., "1-10", "11-50", "51-200", etc.
    
    # Location
    location = Column(String(255))
    address = Column(Text)
    city = Column(String(100), index=True)
    state = Column(String(100), default="Punjab", index=True)
    postal_code = Column(String(20))
    country = Column(String(100), default="India")
    
    # Contact Information
    website = Column(String(255))
    email = Column(String(255))
    phone = Column(String(20))
    
    # Social Media
    linkedin_url = Column(String(255))
    twitter_url = Column(String(255))
    facebook_url = Column(String(255))
    
    # Verification & Status
    is_verified = Column(Boolean, default=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    verification_date = Column(DateTime(timezone=True))
    
    # Employer Association
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Additional Info
    logo_url = Column(String(500))
    banner_url = Column(String(500))
    employee_benefits = Column(JSON)  # List of benefits offered
    company_culture = Column(Text)
    founded_year = Column(Integer)
    revenue_range = Column(String(50))
    
    # Relationships
    user = relationship("User", back_populates="company")
    jobs = relationship("Job", back_populates="company")
    
    def __repr__(self):
        return f"<Company {self.name}>"

    @property
    def employee_count_range(self) -> Optional[str]:
        """Get employee count as a readable range"""
        return self.company_size

    @property
    def location_display(self) -> str:
        """Get formatted location for display"""
        parts = [self.city, self.state, self.country]
        return ", ".join(filter(None, parts))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "company_id": self.company_id,
            "name": self.name,
            "description": self.description,
            "industry": self.industry,
            "company_size": self.company_size,
            "location": self.location_display,
            "website": self.website,
            "email": self.email,
            "phone": self.phone,
            "is_verified": self.is_verified,
            "is_active": self.is_active,
            "logo_url": self.logo_url,
            "banner_url": self.banner_url,
            "founded_year": self.founded_year,
            "linkedin_url": self.linkedin_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class CompanyReview(Base):
    """
    Company reviews from employees/job seekers
    """
    __tablename__ = "company_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Review Content
    rating = Column(Integer, nullable=False)  # 1-5 scale
    title = Column(String(255))
    review_text = Column(Text)
    
    # Review Categories
    work_life_balance = Column(Integer)  # 1-5 scale
    career_opportunities = Column(Integer)  # 1-5 scale
    compensation = Column(Integer)  # 1-5 scale
    management = Column(Integer)  # 1-5 scale
    culture = Column(Integer)  # 1-5 scale
    
    # Reviewer Info (anonymous)
    reviewer_role = Column(String(100))  # "Software Engineer", "Marketing Manager", etc.
    employment_status = Column(String(50))  # "Current Employee", "Former Employee"
    employment_duration = Column(String(50))  # "1-2 years", "3-5 years", etc.
    
    # Status
    is_approved = Column(Boolean, default=False, index=True)
    is_verified = Column(Boolean, default=False)
    
    # Associations
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reviewer_user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    company = relationship("Company")
    reviewer = relationship("User")
    
    def __repr__(self):
        return f"<CompanyReview {self.review_id} for {self.company.name if self.company else 'Unknown'}>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "review_id": self.review_id,
            "rating": self.rating,
            "title": self.title,
            "review_text": self.review_text,
            "work_life_balance": self.work_life_balance,
            "career_opportunities": self.career_opportunities,
            "compensation": self.compensation,
            "management": self.management,
            "culture": self.culture,
            "reviewer_role": self.reviewer_role,
            "employment_status": self.employment_status,
            "employment_duration": self.employment_duration,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


# Database indexes for performance
Index('idx_company_location_search', Company.city, Company.state, Company.industry)
Index('idx_company_verification', Company.is_verified, Company.is_active)
Index('idx_review_company_rating', CompanyReview.company_id, CompanyReview.rating, CompanyReview.is_approved)