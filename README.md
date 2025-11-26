# CSE_95 Analytics - Punjab Rozgar Portal

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Node.js](https://img.shields.io/badge/Node.js-18+-339933.svg?style=flat&logo=Node.js&logoColor=white)](https://nodejs.org)

## 🎯 Project Overview

**CSE_95 Analytics** is a comprehensive employment analytics portal specifically designed for Punjab state, India. This full-stack web application bridges the gap between job seekers, employers, and government agencies while providing deep insights into employment trends, market demands, and user behavior patterns.

## 🚀 Live Demo

- **Frontend Demo**: [Open index.html](frontend/index.html)
- **API Server**: `http://localhost:3001` (after setup)
- **Backend API**: `http://localhost:8000` (after setup)
- **API Documentation**: `http://localhost:8000/docs`

## ✨ Key Features

### 🎨 For Job Seekers
- **Personalized Dashboard** with application tracking
- **Advanced Job Search** with 8 categories (1,200+ jobs)
- **Smart Recommendations** based on skills and preferences
- **Profile Management** with completion scoring
- **Real-time Analytics** of application success rates

### 🏢 For Employers
- **Company Dashboard** with candidate analytics
- **Job Posting Management** with performance metrics
- **Applicant Tracking System** with filtering
- **Analytics Insights** on job market trends

### 👨‍💼 For Administrators
- **System Overview Dashboard** with real-time metrics
- **User Management** with role-based access
- **Advanced Analytics** with Chart.js visualizations
- **Content Moderation** tools

### 📊 Analytics Engine
- **Real-time Event Tracking** (page views, clicks, applications)
- **User Journey Mapping** and behavior analysis
- **Performance Monitoring** with response time tracking
- **Business Intelligence** dashboards

## 🛠️ Technology Stack

### Frontend
- **Vanilla JavaScript ES6+** - No framework dependencies
- **HTML5 & CSS3** - Modern responsive design
- **Chart.js v3.9.1** - Data visualization
- **Font Awesome 6.0** - Icon library
- **Node.js API Server** - Job data serving

### Backend
- **FastAPI** - High-performance Python API framework
- **SQLAlchemy** - Async ORM for database operations
- **SQLite + AsyncIO** - Database with async support
- **JWT Authentication** - Secure user sessions
- **Pydantic** - Data validation and serialization

### DevOps & Deployment
- **Docker** - Containerized deployment
- **Docker Compose** - Multi-service orchestration
- **GitHub Actions Ready** - CI/CD pipeline support

## 📋 Prerequisites

- **Python 3.9+**
- **Node.js 18+**
- **Git**
- **Docker** (optional, for containerized deployment)

## ⚡ Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/CSE_95-analytics.git
cd CSE_95-analytics
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3. Frontend API Server
```bash
cd frontend/api
node server.js
```

### 4. Access the Application
- **Frontend**: Open `frontend/index.html` in your browser
- **Backend API**: http://localhost:8000
- **Node.js API**: http://localhost:3001
- **API Documentation**: http://localhost:8000/docs

### 5. Alternative: Docker Setup
```bash
docker-compose up -d
```

## 📁 Project Structure

```
CSE_95-analytics/
├── 📂 backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── core/              # Core configurations
│   │   ├── models/            # Database models
│   │   ├── api/v1/            # API endpoints
│   │   ├── analytics/         # Analytics engine
│   │   └── middleware/        # Custom middleware
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile            # Backend container config
├── 📂 frontend/               # Frontend Application
│   ├── index.html            # Landing page
│   ├── pages/                # Application pages
│   ├── js/
│   │   ├── auth.js           # Authentication system
│   │   └── punjab-analytics.js # Analytics engine
│   ├── api/
│   │   ├── server.js         # Node.js API server
│   │   ├── jobs.json         # Job database (1,200+ jobs)
│   │   └── companies.json    # Company profiles
│   └── assets/               # Static resources
├── docker-compose.yml        # Multi-service deployment
├── start-api-server.bat     # Quick server start (Windows)
└── README.md                 # This file
```

## 🎯 Core Features Demonstration

### Job Categories (1,200+ Jobs)
- 🏛️ **Government Jobs**: 150+ positions
- 🏢 **Private Sector**: 300+ opportunities
- 🏦 **Banking & Finance**: 80+ roles
- 🏥 **Healthcare**: 120+ positions
- 🎓 **Education**: 90+ openings
- 💻 **Technology**: 200+ tech jobs
- 🏭 **Manufacturing**: 110+ industrial roles
- 🛒 **Retail**: 75+ customer-facing positions

### Real-time Analytics
```javascript
// Example: Track job application
punjabAnalytics.track('job_application', {
    job_id: 'gov_001',
    job_title: 'Deputy Collector',
    category: 'government',
    location: 'Chandigarh',
    user_role: 'job_seeker'
});
```

### Advanced Search & Filtering
```javascript
// Intelligent job search with multiple filters
const searchResults = await fetch('/api/jobs', {
    method: 'POST',
    body: JSON.stringify({
        category: 'technology',
        location: 'chandigarh',
        experience: { min: 2, max: 5 },
        salary: { min: 50000, max: 120000 }
    })
});
```

## 📊 Database Schema

### Key Models
- **User Model**: Authentication, profiles, analytics tracking
- **Job Model**: Postings, requirements, employer information
- **Analytics Event**: Real-time event tracking
- **Application Model**: Job applications with status tracking

### Performance Optimizations
- Strategic indexing for complex queries
- JSON field optimization for skills and preferences
- Async queries with connection pooling

## 🔐 Security Features

- **JWT Authentication** with role-based access
- **CORS Protection** with configurable origins
- **SQL Injection Prevention** through parameterized queries
- **XSS Protection** with input sanitization
- **Rate Limiting** on API endpoints

## 📈 Analytics & Monitoring

### Event Tracking
- Page views and user interactions
- Job search patterns and preferences
- Application success rates
- User journey mapping

### Performance Metrics
- API response times
- Database query performance
- User engagement analytics
- Conversion funnel analysis

## 🚀 Deployment

### Production Deployment
```bash
# Build and deploy with Docker
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables
```env
# .env file
DATABASE_URL=sqlite:///./data/punjab_rozgar.db
SECRET_KEY=your-secret-key-here
ANALYTICS_ENABLED=true
DEBUG=false
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests (if implemented)
cd frontend
npm test
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 API Documentation

### Authentication Endpoints
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/me` - Current user profile

### Job Endpoints
- `GET /jobs` - List jobs with filtering
- `GET /jobs/{id}` - Job details
- `POST /jobs/{id}/apply` - Apply for job
- `GET /jobs/recommended` - Personalized recommendations

### Analytics Endpoints
- `POST /analytics/track` - Track events
- `GET /analytics/dashboard` - Dashboard data
- `GET /analytics/reports` - Generate reports

## 🔍 Performance

- **Backend**: FastAPI with async support (faster than Django/Flask)
- **Database**: Optimized SQLite with strategic indexing
- **Frontend**: Vanilla JS with lazy loading and caching
- **Real-time**: Sub-second event tracking and processing

## 📱 Mobile Support

- **Responsive Design**: Mobile-first approach
- **Touch-friendly UI**: Optimized for mobile interactions
- **Progressive Web App**: Offline capabilities
- **Cross-device Sync**: Session management across devices

## 🌟 Punjab-Specific Features

- **PGRKAM Portal Integration Ready**
- **Punjab Cities**: Chandigarh, Ludhiana, Amritsar, Mohali
- **Government Job Categories**: Specialized for Punjab employment
- **Local Industry Focus**: Agriculture, manufacturing, IT, textiles

## 📞 Support

For support and questions:
- Open an issue on GitHub
- Check the documentation at `/docs`
- Review the API documentation at `http://localhost:8000/docs`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**CSE_95 Team**
- Specialized in employment analytics and web development
- Focus on government portal integration and data analytics

## 🙏 Acknowledgments

- Punjab Government for employment data insights
- FastAPI community for excellent documentation
- Chart.js for powerful data visualization tools
- Open source contributors who made this project possible

---

**⭐ Star this repository if you find it helpful!**
