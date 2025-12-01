"""
Hybrid Recommendation Service
Combines Genetic Algorithm (GA) and Collaborative Filtering (CF) for optimal job matching
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc

from app.core.database import get_database
from app.models.user import User, UserProfile, UserRole
from app.models.job import Job, JobApplication, JobStatus, JobType
from app.models.analytics import AnalyticsEvent
from app.ml.models.genetic_algorithm import (
    GeneticJobMatcher, Candidate, JobProfile, get_ga_recommendations
)
from app.ml.models.collaborative_filtering import (
    CollaborativeFilter, UserInteraction, get_cf_recommendations, fit_collaborative_filter
)
from app.analytics.tracker import get_analytics_tracker

logger = logging.getLogger(__name__)


@dataclass
class HybridRecommendation:
    """Combined recommendation from GA and CF"""
    job_id: str
    user_id: str
    ga_score: float
    cf_score: float
    hybrid_score: float
    ga_breakdown: Dict[str, float]
    recommendation_reason: str
    confidence_level: str  # 'high', 'medium', 'low'
    generated_at: datetime


class HybridRecommendationEngine:
    """
    Hybrid Recommendation Engine combining GA and CF approaches
    Implements weighted scoring system to balance profile relevance with behavioral insights
    """
    
    def __init__(
        self,
        ga_weight: float = 0.6,
        cf_weight: float = 0.4,
        min_cf_score: float = 0.1,
        min_ga_score: float = 0.2,
        cache_duration_hours: int = 6
    ):
        self.ga_weight = ga_weight
        self.cf_weight = cf_weight
        self.min_cf_score = min_cf_score
        self.min_ga_score = min_ga_score
        self.cache_duration = timedelta(hours=cache_duration_hours)
        
        # Initialize ML models
        self.ga_matcher = GeneticJobMatcher()
        self.cf_model = CollaborativeFilter()
        
        # Cache for performance
        self.recommendation_cache = {}
        self.cache_expiry = {}
        
        # Model training status
        self.cf_last_trained = None
        self.cf_training_interval = timedelta(hours=12)
    
    async def _fetch_user_data(self, session: AsyncSession, user_id: str) -> Optional[Candidate]:
        """Fetch user data and convert to Candidate profile"""
        try:
            # Get user and profile
            user_result = await session.execute(
                select(User).where(User.user_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                return None
            
            profile_result = await session.execute(
                select(UserProfile).where(UserProfile.user_id == user_id)
            )
            profile = profile_result.scalar_one_or_none()
            
            # Convert to Candidate object
            candidate = Candidate(
                user_id=user_id,
                skills=user.skills or [],
                experience_years=user.experience_years or 0,
                education_level=user.education_level or 'bachelors',
                preferred_locations=user.preferred_locations or [user.city or 'Lahore'],
                preferred_job_types=user.preferred_job_categories or ['full_time'],
                expected_salary_min=profile.expected_salary_min if profile else None,
                expected_salary_max=profile.expected_salary_max if profile else None
            )
            
            return candidate
            
        except Exception as e:
            logger.error(f"Error fetching user data for {user_id}: {str(e)}")
            return None
    
    async def _fetch_available_jobs(self, session: AsyncSession, limit: int = 100) -> List[JobProfile]:
        """Fetch available jobs and convert to JobProfile objects"""
        try:
            # Get active jobs
            jobs_result = await session.execute(
                select(Job)
                .where(Job.status == JobStatus.ACTIVE)
                .order_by(desc(Job.created_at))
                .limit(limit)
            )
            jobs = jobs_result.scalars().all()
            
            job_profiles = []
            for job in jobs:
                job_profile = JobProfile(
                    job_id=job.job_id,
                    required_skills=job.skills_required or [],
                    preferred_skills=job.skills_preferred or [],
                    experience_min=job.experience_min or 0,
                    experience_max=job.experience_max,
                    education_level=job.education_level or 'bachelors',
                    location_city=job.location_city or 'Lahore',
                    job_type=job.job_type.value if hasattr(job.job_type, 'value') else str(job.job_type),
                    salary_min=job.salary_min,
                    salary_max=job.salary_max,
                    category=job.category or ''
                )
                job_profiles.append(job_profile)
            
            return job_profiles
            
        except Exception as e:
            logger.error(f"Error fetching jobs: {str(e)}")
            return []
    
    async def _fetch_user_interactions(self, session: AsyncSession, days_back: int = 90) -> List[UserInteraction]:
        """Fetch user interaction data for CF model"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            # Get analytics events
            events_result = await session.execute(
                select(AnalyticsEvent)
                .where(
                    and_(
                        AnalyticsEvent.timestamp >= cutoff_date,
                        AnalyticsEvent.event_name.in_([
                            'job_view', 'job_click', 'job_apply', 'job_save'
                        ])
                    )
                )
                .order_by(desc(AnalyticsEvent.timestamp))
            )
            events = events_result.scalars().all()
            
            interactions = []
            for event in events:
                if event.user_id and event.properties and 'job_id' in event.properties:
                    interaction = UserInteraction(
                        user_id=event.user_id,
                        job_id=event.properties['job_id'],
                        interaction_type=event.event_name.replace('job_', ''),
                        timestamp=event.timestamp,
                        interaction_value=1.0
                    )
                    interactions.append(interaction)
            
            return interactions
            
        except Exception as e:
            logger.error(f"Error fetching user interactions: {str(e)}")
            return []
    
    async def _train_cf_model_if_needed(self, session: AsyncSession) -> None:
        """Train or retrain CF model if needed"""
        try:
            if (self.cf_last_trained is None or 
                datetime.utcnow() - self.cf_last_trained > self.cf_training_interval):
                
                logger.info("Training CF model...")
                interactions = await self._fetch_user_interactions(session)
                
                if len(interactions) >= 50:  # Minimum interactions for training
                    await fit_collaborative_filter(interactions)
                    self.cf_last_trained = datetime.utcnow()
                    logger.info(f"CF model trained with {len(interactions)} interactions")
                else:
                    logger.warning(f"Insufficient interactions ({len(interactions)}) for CF training")
        
        except Exception as e:
            logger.error(f"Error training CF model: {str(e)}")
    
    def _calculate_hybrid_score(
        self, 
        ga_score: float, 
        cf_score: float,
        user_interaction_count: int = 0
    ) -> Tuple[float, str]:
        """Calculate hybrid score combining GA and CF"""
        # Adjust weights based on user interaction history
        adjusted_ga_weight = self.ga_weight
        adjusted_cf_weight = self.cf_weight
        
        if user_interaction_count < 5:
            # New users: rely more on GA (profile matching)
            adjusted_ga_weight = 0.8
            adjusted_cf_weight = 0.2
        elif user_interaction_count > 20:
            # Active users: rely more on CF (behavioral patterns)
            adjusted_ga_weight = 0.4
            adjusted_cf_weight = 0.6
        
        # Apply minimum thresholds
        ga_score = max(ga_score, 0.0)
        cf_score = max(cf_score, 0.0)
        
        # Calculate weighted hybrid score
        hybrid_score = (ga_score * adjusted_ga_weight) + (cf_score * adjusted_cf_weight)
        
        # Determine confidence level
        if ga_score > 0.7 and cf_score > 0.5:
            confidence = 'high'
        elif ga_score > 0.5 or cf_score > 0.3:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        return hybrid_score, confidence
    
    def _generate_recommendation_reason(
        self, 
        ga_breakdown: Dict[str, float], 
        cf_score: float,
        confidence: str
    ) -> str:
        """Generate human-readable recommendation reason"""
        reasons = []
        
        # GA-based reasons
        if ga_breakdown.get('skills', 0) > 0.8:
            reasons.append("excellent skill match")
        elif ga_breakdown.get('skills', 0) > 0.6:
            reasons.append("good skill alignment")
        
        if ga_breakdown.get('experience', 0) > 0.8:
            reasons.append("perfect experience level")
        elif ga_breakdown.get('experience', 0) > 0.6:
            reasons.append("suitable experience")
        
        if ga_breakdown.get('location', 0) > 0.8:
            reasons.append("preferred location")
        
        if ga_breakdown.get('salary', 0) > 0.8:
            reasons.append("salary expectations met")
        
        # CF-based reasons
        if cf_score > 0.5:
            reasons.append("similar candidates showed interest")
        elif cf_score > 0.3:
            reasons.append("trending among similar profiles")
        
        if not reasons:
            reasons = ["potential career opportunity"]
        
        reason_text = ", ".join(reasons)
        
        if confidence == 'high':
            return f"Highly recommended due to {reason_text}"
        elif confidence == 'medium':
            return f"Good match based on {reason_text}"
        else:
            return f"Consider this opportunity for {reason_text}"
    
    async def get_recommendations(
        self, 
        session: AsyncSession,
        user_id: str, 
        max_recommendations: int = 10
    ) -> List[HybridRecommendation]:
        """Get hybrid job recommendations for a user"""
        try:
            # Check cache
            cache_key = f"{user_id}_{max_recommendations}"
            if (cache_key in self.recommendation_cache and
                self.cache_expiry.get(cache_key, datetime.min) > datetime.utcnow()):
                return self.recommendation_cache[cache_key]
            
            # Fetch user data
            candidate = await self._fetch_user_data(session, user_id)
            if not candidate:
                logger.warning(f"Could not fetch candidate data for user {user_id}")
                return []
            
            # Fetch available jobs
            jobs = await self._fetch_available_jobs(session, limit=200)
            if not jobs:
                logger.warning("No jobs available for recommendations")
                return []
            
            # Train CF model if needed
            await self._train_cf_model_if_needed(session)
            
            # Get user interaction count for weight adjustment
            interaction_count_result = await session.execute(
                select(func.count(AnalyticsEvent.id))
                .where(
                    and_(
                        AnalyticsEvent.user_id == user_id,
                        AnalyticsEvent.event_name.in_(['job_view', 'job_click', 'job_apply'])
                    )
                )
            )
            user_interaction_count = interaction_count_result.scalar() or 0
            
            # Get GA recommendations
            ga_recommendations = await get_ga_recommendations(
                candidate, jobs, max_recommendations * 2  # Get more for better selection
            )
            
            # Get CF recommendations
            cf_recommendations = await get_cf_recommendations(
                user_id, max_recommendations * 2, method='hybrid'
            )
            
            # Create lookup for CF scores
            cf_scores = {rec['job_id']: rec['cf_score'] for rec in cf_recommendations}
            
            # Combine recommendations
            hybrid_recommendations = []
            
            for ga_rec in ga_recommendations:
                job_id = ga_rec['job_id']
                ga_score = ga_rec['overall_score']
                cf_score = cf_scores.get(job_id, 0.0)
                
                # Calculate hybrid score
                hybrid_score, confidence = self._calculate_hybrid_score(
                    ga_score, cf_score, user_interaction_count
                )
                
                # Generate recommendation reason
                reason = self._generate_recommendation_reason(
                    ga_rec['match_breakdown'], cf_score, confidence
                )
                
                hybrid_rec = HybridRecommendation(
                    job_id=job_id,
                    user_id=user_id,
                    ga_score=ga_score,
                    cf_score=cf_score,
                    hybrid_score=hybrid_score,
                    ga_breakdown=ga_rec['match_breakdown'],
                    recommendation_reason=reason,
                    confidence_level=confidence,
                    generated_at=datetime.utcnow()
                )
                
                hybrid_recommendations.append(hybrid_rec)
            
            # Add pure CF recommendations that weren't in GA results
            ga_job_ids = {rec.job_id for rec in hybrid_recommendations}
            for cf_rec in cf_recommendations:
                if cf_rec['job_id'] not in ga_job_ids and cf_rec['cf_score'] > self.min_cf_score:
                    hybrid_score, confidence = self._calculate_hybrid_score(
                        0.0, cf_rec['cf_score'], user_interaction_count
                    )
                    
                    hybrid_rec = HybridRecommendation(
                        job_id=cf_rec['job_id'],
                        user_id=user_id,
                        ga_score=0.0,
                        cf_score=cf_rec['cf_score'],
                        hybrid_score=hybrid_score,
                        ga_breakdown={},
                        recommendation_reason=f"Trending among users with similar behavior (confidence: {confidence})",
                        confidence_level=confidence,
                        generated_at=datetime.utcnow()
                    )
                    
                    hybrid_recommendations.append(hybrid_rec)
            
            # Sort by hybrid score and return top recommendations
            hybrid_recommendations.sort(key=lambda x: x.hybrid_score, reverse=True)
            final_recommendations = hybrid_recommendations[:max_recommendations]
            
            # Cache results
            self.recommendation_cache[cache_key] = final_recommendations
            self.cache_expiry[cache_key] = datetime.utcnow() + self.cache_duration
            
            logger.info(f"Generated {len(final_recommendations)} hybrid recommendations for user {user_id}")
            return final_recommendations
            
        except Exception as e:
            logger.error(f"Error generating hybrid recommendations for user {user_id}: {str(e)}")
            return []
    
    async def get_recommendations_dict(
        self, 
        session: AsyncSession,
        user_id: str, 
        max_recommendations: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recommendations in dictionary format for API responses"""
        recommendations = await self.get_recommendations(session, user_id, max_recommendations)
        
        return [
            {
                'job_id': rec.job_id,
                'user_id': rec.user_id,
                'hybrid_score': round(rec.hybrid_score, 3),
                'ga_score': round(rec.ga_score, 3),
                'cf_score': round(rec.cf_score, 3),
                'match_breakdown': rec.ga_breakdown,
                'recommendation_reason': rec.recommendation_reason,
                'confidence_level': rec.confidence_level,
                'recommendation_source': 'hybrid_ga_cf',
                'generated_at': rec.generated_at.isoformat()
            }
            for rec in recommendations
        ]
    
    def clear_cache(self) -> None:
        """Clear recommendation cache"""
        self.recommendation_cache.clear()
        self.cache_expiry.clear()
        logger.info("Hybrid recommendation cache cleared")


# Global hybrid recommendation engine
hybrid_engine = HybridRecommendationEngine()


async def get_hybrid_job_recommendations(
    session: AsyncSession,
    user_id: str, 
    max_recommendations: int = 10
) -> List[Dict[str, Any]]:
    """Main function to get hybrid job recommendations"""
    return await hybrid_engine.get_recommendations_dict(
        session, user_id, max_recommendations
    )


async def refresh_recommendation_models(session: AsyncSession) -> Dict[str, str]:
    """Refresh both GA and CF models with latest data"""
    try:
        # Force CF model retraining
        hybrid_engine.cf_last_trained = None
        await hybrid_engine._train_cf_model_if_needed(session)
        
        # Clear caches
        hybrid_engine.clear_cache()
        
        return {
            'status': 'success',
            'message': 'Recommendation models refreshed successfully',
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error refreshing recommendation models: {str(e)}")
        return {
            'status': 'error',
            'message': f'Failed to refresh models: {str(e)}',
            'timestamp': datetime.utcnow().isoformat()
        }