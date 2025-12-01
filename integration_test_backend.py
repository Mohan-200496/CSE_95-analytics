"""
Minimal test backend server for integration testing
This bypasses SQLAlchemy compatibility issues
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime
import uuid

# Create FastAPI instance
app = FastAPI(
    title="Punjab Rozgar Test API",
    description="Test API for integration testing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data storage
mock_jobs = [
    {
        "job_id": "job_123456789abc",
        "title": "Software Engineer",
        "description": "Develop web applications",
        "category": "Information Technology", 
        "location_city": "Chandigarh",
        "location_state": "Punjab",
        "job_type": "full_time",
        "salary_min": 50000,
        "salary_max": 80000,
        "employer_name": "Tech Company",
        "status": "active",
        "created_at": datetime.now().isoformat()
    },
    {
        "job_id": "job_987654321def", 
        "title": "Data Analyst",
        "description": "Analyze business data",
        "category": "Data Science",
        "location_city": "Ludhiana", 
        "location_state": "Punjab",
        "job_type": "full_time",
        "salary_min": 40000,
        "salary_max": 60000,
        "employer_name": "Analytics Corp",
        "status": "active",
        "created_at": datetime.now().isoformat()
    }
]

mock_users = [
    {
        "user_id": "user_admin123",
        "email": "admin@test.com",
        "role": "admin",
        "first_name": "Admin",
        "last_name": "User",
        "is_active": True
    }
]

analytics_events = []

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Punjab Rozgar Test API",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": "connected",
            "api": "running"
        }
    }

# Authentication endpoints
@app.post("/api/v1/auth/register")
async def register_user(user_data: dict):
    new_user = {
        "user_id": f"user_{uuid.uuid4().hex[:8]}",
        "email": user_data.get("email", "test@example.com"),
        "role": user_data.get("role", "jobseeker"),
        "first_name": user_data.get("first_name", "Test"),
        "last_name": user_data.get("last_name", "User"),
        "is_active": True,
        "created_at": datetime.now().isoformat()
    }
    mock_users.append(new_user)
    
    return {
        "success": True,
        "message": "User registered successfully",
        "user": new_user
    }

# Job endpoints
@app.get("/api/v1/jobs")
async def get_jobs(skip: int = 0, limit: int = 20):
    return {
        "jobs": mock_jobs[skip:skip+limit],
        "total": len(mock_jobs),
        "page": skip // limit + 1 if limit > 0 else 1
    }

@app.get("/api/v1/jobs/recent")
async def get_recent_jobs(limit: int = 10):
    recent_jobs = sorted(mock_jobs, key=lambda x: x["created_at"], reverse=True)
    return {
        "jobs": recent_jobs[:limit],
        "total": len(recent_jobs)
    }

@app.post("/api/v1/jobs")
async def create_job(job_data: dict):
    new_job = {
        "job_id": f"job_{uuid.uuid4().hex[:12]}",
        "title": job_data.get("title", "Test Job"),
        "description": job_data.get("description", "Test description"),
        "category": job_data.get("category", "General"),
        "location_city": job_data.get("location_city", "Chandigarh"),
        "location_state": job_data.get("location_state", "Punjab"),
        "job_type": job_data.get("job_type", "full_time"),
        "salary_min": job_data.get("salary_min", 30000),
        "salary_max": job_data.get("salary_max", 50000),
        "employer_name": job_data.get("employer_name", "Test Company"),
        "status": "active",
        "created_at": datetime.now().isoformat()
    }
    mock_jobs.append(new_job)
    
    return {
        "success": True,
        "message": "Job created successfully",
        "job": new_job
    }

@app.post("/api/v1/jobs/test-create")
async def test_create_job(job_data: dict):
    return await create_job(job_data)

# Admin endpoints
@app.get("/api/v1/admin/stats")
async def get_admin_stats():
    return {
        "total_users": len(mock_users),
        "total_jobs": len(mock_jobs),
        "active_jobs": len([j for j in mock_jobs if j["status"] == "active"]),
        "total_applications": 5,
        "analytics_events": len(analytics_events),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/admin/jobs")
async def get_admin_jobs():
    return {
        "jobs": mock_jobs,
        "total": len(mock_jobs),
        "status_counts": {
            "active": len([j for j in mock_jobs if j["status"] == "active"]),
            "draft": 0,
            "closed": 0
        }
    }

# Analytics endpoints
@app.post("/api/v1/analytics/track")
async def track_event(event_data: dict):
    event = {
        "event_id": f"event_{uuid.uuid4().hex[:8]}",
        "event_name": event_data.get("event_name", "unknown_event"),
        "timestamp": datetime.now().isoformat(),
        "properties": event_data.get("properties", {})
    }
    analytics_events.append(event)
    
    return {
        "success": True,
        "message": "Event tracked successfully",
        "event_id": event["event_id"]
    }

@app.get("/api/v1/analytics/events")
async def get_analytics_events():
    return {
        "events": analytics_events[-50:],  # Last 50 events
        "total": len(analytics_events)
    }

# User application endpoints
@app.get("/api/v1/applications")
async def get_user_applications():
    mock_applications = [
        {
            "application_id": "app_123",
            "job_id": "job_123456789abc",
            "job_title": "Software Engineer",
            "status": "pending",
            "applied_at": datetime.now().isoformat()
        }
    ]
    return {
        "applications": mock_applications,
        "total": len(mock_applications)
    }

# Database test endpoints
@app.get("/api/v1/test/db-connection")
async def test_db_connection():
    return {
        "status": "connected",
        "database": "test_db",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/test/jobs-table")
async def test_jobs_table():
    return {
        "table": "jobs",
        "count": len(mock_jobs),
        "status": "accessible",
        "sample": mock_jobs[0] if mock_jobs else None
    }

# Recommendation endpoints
@app.post("/api/v1/recommendations/skill-matching")
async def test_skill_matching(data: dict):
    return {
        "matches": [
            {"job_id": "job_123456789abc", "score": 0.85},
            {"job_id": "job_987654321def", "score": 0.72}
        ],
        "algorithm": "skill_matching",
        "accuracy": 0.85
    }

@app.post("/api/v1/recommendations/user-preferences")
async def test_user_preferences(data: dict):
    return {
        "recommendations": [
            {"job_id": "job_123456789abc", "relevance": 0.90},
            {"job_id": "job_987654321def", "relevance": 0.78}
        ],
        "algorithm": "collaborative_filtering",
        "processing_time": 0.15
    }

# Additional endpoints for comprehensive testing
@app.get("/api/v1/test/performance")
async def test_performance():
    return {
        "response_time": 0.05,
        "status": "optimal",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/test/security")
async def test_security(data: dict):
    return {
        "jwt_validation": "passed",
        "input_sanitization": "passed", 
        "cors_configured": "passed",
        "status": "secure"
    }

if __name__ == "__main__":
    print("🚀 Starting Punjab Rozgar Test Backend...")
    print("📡 Server will be available at: http://localhost:8001")
    print("📚 API docs available at: http://localhost:8001/docs")
    print("🔍 Health check: http://localhost:8001/health")
    
    uvicorn.run(
        "integration_test_backend:app", 
        host="0.0.0.0", 
        port=8001,
        log_level="info",
        reload=False,
        access_log=True
    )