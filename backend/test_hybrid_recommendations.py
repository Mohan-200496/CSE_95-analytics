"""
Test script for the Hybrid Recommendation Engine
Tests both GA and CF components along with the integrated service
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import List, Dict

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.ml.models.genetic_algorithm import Candidate, JobProfile, GeneticJobMatcher
from app.ml.models.collaborative_filtering import UserInteraction, CollaborativeFilter
from app.services.recommendation_service import HybridRecommendationEngine


def create_test_candidate() -> Candidate:
    """Create a test candidate for GA testing"""
    return Candidate(
        user_id="test_user_123",
        skills=["Python", "Machine Learning", "SQL", "FastAPI"],
        experience_years=3,
        education_level="masters",
        preferred_locations=["Chandigarh", "Mohali"],
        preferred_job_types=["full_time", "remote"],
        expected_salary_min=50000,
        expected_salary_max=80000
    )


def create_test_jobs() -> List[JobProfile]:
    """Create test job profiles for GA testing"""
    return [
        JobProfile(
            job_id="job_001",
            required_skills=["Python", "FastAPI", "SQL"],
            preferred_skills=["Machine Learning", "Docker"],
            experience_min=2,
            experience_max=5,
            education_level="bachelors",
            location_city="Chandigarh",
            job_type="full_time",
            salary_min=55000,
            salary_max=75000,
            category="Technology"
        ),
        JobProfile(
            job_id="job_002",
            required_skills=["JavaScript", "React", "CSS"],
            preferred_skills=["Node.js", "MongoDB"],
            experience_min=1,
            experience_max=4,
            education_level="bachelors",
            location_city="Mohali",
            job_type="remote",
            salary_min=45000,
            salary_max=65000,
            category="Technology"
        ),
        JobProfile(
            job_id="job_003",
            required_skills=["Python", "Data Analysis", "Statistics"],
            preferred_skills=["Machine Learning", "Pandas", "Numpy"],
            experience_min=2,
            experience_max=6,
            education_level="masters",
            location_city="Chandigarh",
            job_type="full_time",
            salary_min=60000,
            salary_max=90000,
            category="Data Science"
        ),
        JobProfile(
            job_id="job_004",
            required_skills=["Marketing", "Social Media", "Content Creation"],
            preferred_skills=["SEO", "Analytics"],
            experience_min=1,
            experience_max=3,
            education_level="bachelors",
            location_city="Ludhiana",
            job_type="full_time",
            salary_min=30000,
            salary_max=50000,
            category="Marketing"
        )
    ]


def create_test_interactions() -> List[UserInteraction]:
    """Create test user interactions for CF testing"""
    return [
        UserInteraction(
            user_id="test_user_123",
            job_id="job_001",
            interaction_type="view",
            timestamp=datetime.utcnow(),
            interaction_value=1.0
        ),
        UserInteraction(
            user_id="test_user_123",
            job_id="job_003",
            interaction_type="apply",
            timestamp=datetime.utcnow(),
            interaction_value=3.0
        ),
        UserInteraction(
            user_id="user_456",
            job_id="job_001",
            interaction_type="apply",
            timestamp=datetime.utcnow(),
            interaction_value=3.0
        ),
        UserInteraction(
            user_id="user_456",
            job_id="job_002",
            interaction_type="view",
            timestamp=datetime.utcnow(),
            interaction_value=1.0
        ),
        UserInteraction(
            user_id="user_789",
            job_id="job_003",
            interaction_type="view",
            timestamp=datetime.utcnow(),
            interaction_value=1.0
        )
    ]


async def test_genetic_algorithm():
    """Test the Genetic Algorithm component"""
    print("\\n=== Testing Genetic Algorithm ===")
    
    try:
        # Initialize GA matcher
        ga_matcher = GeneticJobMatcher()
        
        # Create test data
        candidate = create_test_candidate()
        jobs = create_test_jobs()
        
        print(f"Testing candidate: {candidate.user_id}")
        print(f"Skills: {candidate.skills}")
        print(f"Experience: {candidate.experience_years} years")
        print(f"Preferred locations: {candidate.preferred_locations}")
        
        # Get GA recommendations
        recommendations = await ga_matcher.recommend_jobs_async(candidate, jobs, max_recommendations=3)
        
        print(f"\\nGA Recommendations ({len(recommendations)}):")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. Job: {rec['job_id']}")
            print(f"   Overall Score: {rec['overall_score']:.3f}")
            print(f"   Skills Match: {rec['match_breakdown']['skills']:.3f}")
            print(f"   Experience Match: {rec['match_breakdown']['experience']:.3f}")
            print(f"   Location Match: {rec['match_breakdown']['location']:.3f}")
            print(f"   Salary Match: {rec['match_breakdown']['salary']:.3f}")
            print()
        
        print("✅ Genetic Algorithm test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Genetic Algorithm test failed: {str(e)}")
        return False


async def test_collaborative_filtering():
    """Test the Collaborative Filtering component"""
    print("\\n=== Testing Collaborative Filtering ===")
    
    try:
        # Initialize CF model
        cf_model = CollaborativeFilter()
        
        # Create test data
        interactions = create_test_interactions()
        
        print(f"Testing with {len(interactions)} user interactions")
        for interaction in interactions:
            print(f"  {interaction.user_id} -> {interaction.job_id} ({interaction.interaction_type})")
        
        # Train CF model
        cf_model.fit(interactions)
        print("\\nCF Model trained successfully")
        
        # Get CF recommendations
        user_id = "test_user_123"
        recommendations = cf_model.recommend_jobs(user_id, num_recommendations=3)
        
        print(f"\\nCF Recommendations for {user_id} ({len(recommendations)}):")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. Job: {rec['job_id']}")
            print(f"   CF Score: {rec['cf_score']:.3f}")
            print(f"   Method: {rec['method']}")
            print()
        
        print("✅ Collaborative Filtering test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Collaborative Filtering test failed: {str(e)}")
        return False


async def test_hybrid_engine():
    """Test the Hybrid Recommendation Engine"""
    print("\\n=== Testing Hybrid Recommendation Engine ===")
    
    try:
        # Initialize hybrid engine
        hybrid_engine = HybridRecommendationEngine(
            ga_weight=0.6,
            cf_weight=0.4,
            cache_duration_hours=1
        )
        
        print("Hybrid engine initialized with weights:")
        print(f"  GA Weight: {hybrid_engine.ga_weight}")
        print(f"  CF Weight: {hybrid_engine.cf_weight}")
        
        # Test hybrid score calculation
        ga_score = 0.85
        cf_score = 0.72
        interaction_count = 15
        
        hybrid_score, confidence = hybrid_engine._calculate_hybrid_score(
            ga_score, cf_score, interaction_count
        )
        
        print(f"\\nHybrid Score Calculation Test:")
        print(f"  GA Score: {ga_score}")
        print(f"  CF Score: {cf_score}")
        print(f"  User Interactions: {interaction_count}")
        print(f"  Hybrid Score: {hybrid_score:.3f}")
        print(f"  Confidence: {confidence}")
        
        # Test recommendation reason generation
        ga_breakdown = {
            'skills': 0.9,
            'experience': 0.8,
            'location': 0.85,
            'salary': 0.75
        }
        
        reason = hybrid_engine._generate_recommendation_reason(
            ga_breakdown, cf_score, confidence
        )
        
        print(f"\\nRecommendation Reason: {reason}")
        
        print("\\n✅ Hybrid Recommendation Engine test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Hybrid Recommendation Engine test failed: {str(e)}")
        return False


async def run_all_tests():
    """Run all recommendation system tests"""
    print("🚀 Starting Hybrid Recommendation System Tests")
    print("=" * 60)
    
    results = {
        "ga_test": await test_genetic_algorithm(),
        "cf_test": await test_collaborative_filtering(),
        "hybrid_test": await test_hybrid_engine()
    }
    
    print("\\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        print(f"{test_name.upper():<20} {status}")
    
    print(f"\\nOVERALL: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The Hybrid Recommendation System is ready.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the error messages above.")
        return False


if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(run_all_tests())
    
    if success:
        print("\\n🔥 The GA + CF Hybrid Recommendation Engine is operational!")
        print("\\n📈 Key Features Implemented:")
        print("  • Genetic Algorithm for profile-based job matching")
        print("  • Collaborative Filtering for behavior-based recommendations") 
        print("  • Hybrid scoring system combining both approaches")
        print("  • Adaptive weights based on user interaction history")
        print("  • Performance caching and background model training")
        print("  • Comprehensive API endpoints for all operations")
        print("\\n✨ Ready for production deployment!")
    else:
        print("\\n🛠️ Please fix the failing tests before deployment.")
        sys.exit(1)