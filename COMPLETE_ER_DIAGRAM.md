# PUNJAB ROZGAR PORTAL - COMPREHENSIVE ER DIAGRAM & SYSTEM ARCHITECTURE

## 🗄️ **DATABASE SCHEMA & ENTITY RELATIONSHIPS**

### **CORE ENTITIES**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            USERS (Central Entity)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: id (Integer)                                                            │
│ UK: user_id (String) - Public ID                                           │
│ UK: email (String)                                                          │
│ Fields: phone, hashed_password, role (ENUM), status (ENUM)                 │
│ Personal: first_name, last_name, date_of_birth, gender                     │
│ Location: address, city, state, pincode                                    │
│ Professional: education_level, experience_years, skills (JSON)             │
│ Preferences: preferred_job_categories (JSON), preferred_locations (JSON)   │
│ Analytics: signup_source, utm_*, profile_completion_score                  │
│ Employer: company_name, company_size, industry, company_description        │
│ Tracking: total_applications, total_job_views, total_searches              │
│ Timestamps: created_at, updated_at, last_login                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
┌─────────────────────────────┐ ┌─────────────────────────────┐ ┌─────────────────────────────┐
│       USER_PROFILES         │ │    USER_PREFERENCES         │ │    USER_VERIFICATION        │
├─────────────────────────────┤ ├─────────────────────────────┤ ├─────────────────────────────┤
│ PK: id                      │ │ PK: id                      │ │ PK: id                      │
│ FK: user_id → users.user_id │ │ FK: user_id → users.user_id │ │ FK: user_id → users.user_id │
│ about, resume_url           │ │ job_alerts_enabled          │ │ verification_type           │
│ portfolio_url, linkedin_url │ │ alert_frequency             │ │ verification_token          │
│ work_experience (JSON)      │ │ email_*, sms_*              │ │ verified, expires_at        │
│ education_details (JSON)    │ │ profile_searchable          │ │ verification_data (JSON)    │
│ expected_salary_min/max     │ │ preferred_language          │ └─────────────────────────────┘
│ willing_to_relocate         │ │ timezone, currency          │
│ profile_visibility          │ └─────────────────────────────┘
└─────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              JOBS (Main Entity)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: id (Integer)                                                            │
│ UK: job_id (String) - Public ID                                            │
│ Basic: title, description, requirements, responsibilities                  │
│ Details: job_type (ENUM), category, subcategory                           │
│ Location: location_city, location_state, location_area, remote_allowed    │
│ Compensation: salary_min/max, salary_currency, salary_period              │
│ Experience: experience_min/max, education_level                           │
│ Skills: skills_required (JSON), skills_preferred (JSON)                   │
│ Employer: employer_id → users.user_id, employer_name, employer_type       │
│ Application: application_deadline, application_method, contact_*          │
│ Status: status (ENUM), created_at, updated_at, published_at, expires_at   │
│ Analytics: views_count, applications_count, shares_count, saves_count     │
│ SEO: slug, meta_description, featured, urgent                             │
│ Government: government_scheme, reservation_category (JSON), age_limit_*   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   JOB_APPLICATIONS  │    │    SAVED_JOBS       │    │     JOB_VIEWS       │
├─────────────────────┤    ├─────────────────────┤    ├─────────────────────┤
│ PK: id              │    │ PK: id              │    │ PK: id              │
│ UK: application_id  │    │ FK: user_id         │    │ FK: job_id          │
│ FK: job_id          │    │ FK: job_id          │    │ FK: user_id (opt)   │
│ FK: user_id         │    │ saved_at            │    │ session_id          │
│ status (ENUM)       │    │ notes               │    │ viewed_at           │
│ resume_url          │    │ applied             │    │ time_spent          │
│ cover_letter        │    └─────────────────────┘    │ referrer            │
│ applicant_* fields  │                               │ search_query        │
│ interview_* fields  │                               │ device_type         │
│ employer_notes      │                               └─────────────────────┘
│ selected, feedback  │
└─────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           ANALYTICS ENTITIES                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────┐  ┌─────────────────────────────┐           │
│  │    ANALYTICS_EVENTS         │  │      PAGE_VIEWS             │           │
│  ├─────────────────────────────┤  ├─────────────────────────────┤           │
│  │ PK: id                      │  │ PK: id                      │           │
│  │ event_name                  │  │ session_id                  │           │
│  │ user_id, session_id         │  │ user_id                     │           │
│  │ timestamp                   │  │ page_path, page_title       │           │
│  │ properties (JSON)           │  │ timestamp, load_time        │           │
│  │ page_url, referrer          │  │ time_on_page                │           │
│  │ user_agent, ip_address      │  │ referrer, utm_*             │           │
│  └─────────────────────────────┘  │ device_type, browser        │           │
│                                   │ country, region, city       │           │
│  ┌─────────────────────────────┐  └─────────────────────────────┘           │
│  │      USER_SESSIONS          │                                            │
│  ├─────────────────────────────┤  ┌─────────────────────────────┐           │
│  │ PK: id                      │  │    JOB_INTERACTIONS         │           │
│  │ UK: session_id              │  ├─────────────────────────────┤           │
│  │ user_id                     │  │ PK: id                      │           │
│  │ started_at, ended_at        │  │ user_id, session_id         │           │
│  │ duration, page_views        │  │ job_id                      │           │
│  │ events_count                │  │ interaction_type            │           │
│  │ landing_page, exit_page     │  │ job_title, job_category     │           │
│  │ referrer, user_agent        │  │ job_location, job_type      │           │
│  │ converted, conversion_type  │  │ user_context fields         │           │
│  └─────────────────────────────┘  │ funnel_stage                │           │
│                                   │ conversion_path (JSON)      │           │
└───────────────────────────────────┴─────────────────────────────────────────┘
```

### **RELATIONSHIP MAPPINGS**

```
USERS (1) ←→ (0..1) USER_PROFILES        [One-to-One Optional]
USERS (1) ←→ (0..1) USER_PREFERENCES     [One-to-One Optional]  
USERS (1) ←→ (0..*) USER_VERIFICATION    [One-to-Many]
USERS (1) ←→ (0..*) USER_ACTIVITY        [One-to-Many]

USERS (1) ←→ (0..*) JOBS                 [Employer creates Jobs]
JOBS (1) ←→ (0..*) JOB_APPLICATIONS      [Jobs receive Applications]
USERS (1) ←→ (0..*) JOB_APPLICATIONS     [Users apply to Jobs]
JOBS (1) ←→ (0..*) SAVED_JOBS            [Users save Jobs]
USERS (1) ←→ (0..*) SAVED_JOBS           [Users save Jobs]
JOBS (1) ←→ (0..*) JOB_VIEWS             [Jobs get Views]
USERS (1) ←→ (0..*) JOB_VIEWS            [Users view Jobs]

USERS (1) ←→ (0..*) JOB_ALERTS           [Users create Alerts]
JOB_CATEGORIES (1) ←→ (0..*) JOBS        [Category classifies Jobs]

USERS (1) ←→ (0..*) ANALYTICS_EVENTS     [User generates Events]
USERS (1) ←→ (0..*) PAGE_VIEWS           [User views Pages]
USERS (1) ←→ (0..*) USER_SESSIONS        [User has Sessions]
```

---

## 🖼️ **FRONTEND PAGE ARCHITECTURE**

### **AUTHENTICATION PAGES**
```
/auth/
├── login.html           → User Login (All Roles)
├── register.html        → New User Registration  
├── register-clean.html  → Simplified Registration
├── forgot-password.html → Password Reset
└── verify-email.html    → Email Verification
```

### **ROLE-BASED DASHBOARDS**

#### **📊 ADMIN DASHBOARD**
```
/admin/ & /dashboard/admin/
├── dashboard.html       → Admin Overview & System Stats
├── users.html          → User Management (View/Edit/Suspend Users)
├── jobs.html           → Job Approval & Management  
├── companies.html      → Company/Employer Management
├── applications.html   → Application Monitoring
├── reports.html        → System Reports & Analytics
├── settings.html       → System Configuration
└── analytics.html      → Advanced Analytics Dashboard
```

#### **🏢 EMPLOYER DASHBOARD**  
```
/employer/ & /dashboard/employer/
├── dashboard.html       → Employer Overview & Stats
├── add-job.html        → Create New Job Posting
├── jobs.html           → Manage Posted Jobs
├── manage-jobs.html    → Job Management Interface
├── job-details.html    → Individual Job Details & Stats
├── applications.html   → View Job Applications
├── candidates.html     → Candidate Management
├── company.html        → Company Profile Management
├── company-profile.html → Enhanced Company Profile
├── analytics.html      → Employer Analytics
└── post-job.html       → Job Posting Interface
```

#### **👨‍💼 JOB SEEKER DASHBOARD**
```
/jobseeker/ & /dashboard/job-seeker/
├── dashboard.html           → Job Seeker Overview
├── temp_dashboard_part1.html → Dashboard Components
├── browse-jobs.html         → Browse Job Listings
├── professional-browse-jobs.html → Advanced Job Browse
├── job-search.html          → Job Search Interface  
├── applications.html        → Track Applications
├── saved-jobs.html          → Saved/Bookmarked Jobs
├── profile.html             → Profile Management
├── resume.html              → Resume Builder/Upload
├── job-alerts.html          → Job Alert Settings
└── recommendations.html     → AI Job Recommendations
```

#### **📋 COUNSELOR DASHBOARD**
```
/dashboard/counselor/
├── dashboard.html       → Counselor Overview
├── candidates.html      → Candidate Management
└── guidance.html        → Career Guidance Tools
```

### **PUBLIC PAGES**

#### **💼 JOB PAGES**
```
/jobs/
├── search.html          → Job Search Interface
├── browse.html          → Browse All Jobs
├── detail.html          → Individual Job Details
└── apply.html           → Job Application Form
```

#### **🏢 COMPANY PAGES**  
```
/companies/
└── list.html            → Company Directory
```

#### **👤 PROFILE PAGES**
```
/profile/
├── view.html            → View User Profile
├── edit.html            → Edit Profile Information
├── skills.html          → Skills Management
└── experience.html      → Experience Management
```

#### **📊 ANALYTICS PAGES**
```
/analytics/
├── reports.html         → Analytics Reports
├── job-trends.html      → Job Market Trends
├── user-behavior.html   → User Behavior Analytics
└── conversion.html      → Conversion Analytics
```

#### **🏛️ PGRKAM (Government Scheme)**
```
/pgrkam/
├── index.html           → PGRKAM Overview
└── exact.html           → Detailed PGRKAM Information
```

#### **📄 STATIC/LEGAL PAGES**
```
/static/
├── about.html           → About Punjab Rozgar Portal
├── contact.html         → Contact Information
├── help.html            → Help & FAQ
├── privacy.html         → Privacy Policy
└── terms.html           → Terms of Service
```

---

## 🔗 **SYSTEM RELATIONSHIPS & DATA FLOW**

### **USER ROLES & PERMISSIONS**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   JOB_SEEKER    │    │    EMPLOYER     │    │     ADMIN       │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Browse Jobs   │    │ • Post Jobs     │    │ • User Mgmt     │
│ • Apply to Jobs │    │ • View Apps     │    │ • Job Approval  │
│ • Save Jobs     │    │ • Manage Posts  │    │ • Analytics     │
│ • Get Alerts    │    │ • Company Prof  │    │ • System Config │
│ • Track Apps    │    │ • Analytics     │    │ • Reports       │
│ • Profile Mgmt  │    │ • Candidates    │    │ • Content Mgmt  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **KEY BUSINESS PROCESSES**

#### **🔄 JOB APPLICATION WORKFLOW**
```
Job Posting → Admin Approval → Published → User Views → Application → 
Employer Review → Interview → Selection/Rejection
```

#### **📊 ANALYTICS DATA FLOW**
```
User Action → Event Tracking → Analytics Storage → Real-time Dashboards → 
Insights Generation → Recommendations
```

#### **🎯 RECOMMENDATION ENGINE**  
```
User Profile + Job History + Analytics → ML Algorithm → 
Personalized Job Recommendations → User Dashboard
```

---

## 🗂️ **DATABASE INDEXING STRATEGY**

### **PRIMARY INDEXES**
- **Users**: `email`, `user_id`, `role`, `status`, `city`, `experience_years`
- **Jobs**: `job_id`, `employer_id`, `status`, `category`, `location_city`, `published_at`
- **Applications**: `job_id`, `user_id`, `status`, `applied_at`
- **Analytics**: `event_name + timestamp`, `user_id + timestamp`, `session_id`

### **COMPOSITE INDEXES**
- **Jobs**: `(category, status)`, `(location_city, job_type)`, `(employer_id, status)`
- **Applications**: `(job_id, status)`, `(user_id, status)`  
- **Analytics**: `(user_id, activity_type, timestamp)`

---

## 📈 **ANALYTICS TRACKING POINTS**

### **USER BEHAVIOR**
- Page views, session duration, bounce rate
- Job search queries, filters used
- Application completion rates
- Profile completion tracking

### **JOB PERFORMANCE**  
- Job view counts, application rates
- Employer engagement metrics
- Category popularity trends
- Location-based job demand

### **SYSTEM METRICS**
- User registration funnel
- Authentication success rates
- API response times
- Error rates and debugging

---

## 🔧 **TECHNICAL ARCHITECTURE**

### **BACKEND STACK**
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT with role-based access
- **Analytics**: Real-time event tracking
- **Deployment**: Render.com

### **FRONTEND STACK**
- **Technology**: Vanilla HTML5, CSS3, JavaScript
- **Responsive**: Mobile-first design
- **Analytics**: Custom Punjab Analytics integration
- **Authentication**: JWT-based session management
- **Deployment**: Static hosting with CDN

This comprehensive ER diagram and system architecture provides a complete view of your Punjab Rozgar Portal, showing all entities, relationships, user roles, page structures, and data flows. The system is designed for scalability, analytics tracking, and government employment portal requirements.
