// Working Jobs Data for Browse Page
const punjabJobs = [
    {
        job_id: "job_1",
        title: "Software Developer - Python/FastAPI", 
        description: "Join our dynamic team as a Python developer! We're looking for someone skilled in FastAPI, SQLAlchemy, and async programming. You'll work on building scalable web applications and APIs for our Punjab-based clients.",
        company_name: "TechSoft Solutions Pvt Ltd",
        location: { city: "Chandigarh", state: "Punjab" },
        job_type: "full_time",
        category: "Technology",
        salary: { min: 50000, max: 80000, currency: "INR" },
        experience: { min: 2, max: 5 },
        skills_required: ["Python", "FastAPI", "SQL", "Git", "PostgreSQL"],
        remote_allowed: true,
        created_at: "2024-11-28T10:00:00",
        application_deadline: "2024-12-28T23:59:59",
        status: "active"
    },
    {
        job_id: "job_2",
        title: "Digital Marketing Manager",
        description: "Lead our digital marketing initiatives and help grow Punjab-based businesses. Experience in social media marketing, SEO, content strategy, and performance analytics required. Great opportunity for career growth.",
        company_name: "Creative Agency Punjab",
        location: { city: "Ludhiana", state: "Punjab" },
        job_type: "full_time",
        category: "Marketing",
        salary: { min: 40000, max: 60000, currency: "INR" },
        experience: { min: 3, max: 7 },
        skills_required: ["Digital Marketing", "Social Media", "SEO", "Google Analytics", "Content Marketing"],
        remote_allowed: true,
        created_at: "2024-11-27T15:30:00",
        application_deadline: "2024-12-27T23:59:59",
        status: "active"
    },
    {
        job_id: "job_3", 
        title: "Data Analyst - Government Sector",
        description: "Analyze large datasets to provide insights for policy decisions in Punjab Government. Work with census data, economic indicators, and social metrics. Experience with Python, SQL, and data visualization tools required.",
        company_name: "Government of Punjab",
        location: { city: "Amritsar", state: "Punjab" },
        job_type: "full_time",
        category: "Government",
        salary: { min: 35000, max: 55000, currency: "INR" },
        experience: { min: 1, max: 4 },
        skills_required: ["Python", "SQL", "Excel", "Statistics", "Tableau"],
        remote_allowed: false,
        created_at: "2024-11-26T09:15:00", 
        application_deadline: "2024-12-26T23:59:59",
        status: "active"
    },
    {
        job_id: "job_4",
        title: "Frontend Developer - React Specialist",
        description: "Build beautiful, responsive web applications using React and modern JavaScript. Work with a talented team to create user-friendly interfaces for Punjab's growing tech ecosystem. Strong CSS and design skills required.",
        company_name: "Digital Innovations Pvt Ltd",
        location: { city: "Jalandhar", state: "Punjab" },
        job_type: "full_time",
        category: "Technology",
        salary: { min: 45000, max: 70000, currency: "INR" },
        experience: { min: 2, max: 6 },
        skills_required: ["React", "JavaScript", "CSS3", "HTML5", "Redux"],
        remote_allowed: true,
        created_at: "2024-11-25T14:20:00",
        application_deadline: "2024-12-25T23:59:59",
        status: "active"
    },
    {
        job_id: "job_5",
        title: "Customer Support Executive",
        description: "Provide excellent customer service for our clients across Punjab. Handle inquiries, resolve issues, and maintain customer satisfaction. Good communication skills in Hindi, Punjabi, and English required.",
        company_name: "Punjab Customer Care Services",
        location: { city: "Patiala", state: "Punjab" },
        job_type: "full_time",
        category: "Customer Service",
        salary: { min: 25000, max: 35000, currency: "INR" },
        experience: { min: 0, max: 3 },
        skills_required: ["Communication", "Hindi", "Punjabi", "Customer Service", "MS Office"],
        remote_allowed: false,
        created_at: "2024-11-24T11:45:00",
        application_deadline: "2024-12-24T23:59:59", 
        status: "active"
    },
    {
        job_id: "job_6",
        title: "Graphic Designer",
        description: "Create visual content for digital and print media. Design logos, brochures, social media graphics, and marketing materials for Punjab-based businesses. Adobe Creative Suite expertise required.",
        company_name: "Creative Studio Punjab",
        location: { city: "Mohali", state: "Punjab" },
        job_type: "full_time",
        category: "Design",
        salary: { min: 30000, max: 50000, currency: "INR" },
        experience: { min: 1, max: 4 },
        skills_required: ["Adobe Photoshop", "Adobe Illustrator", "CorelDRAW", "Creative Design", "Brand Identity"],
        remote_allowed: true,
        created_at: "2024-11-23T16:00:00",
        application_deadline: "2024-12-23T23:59:59",
        status: "active"
    },
    {
        job_id: "job_7",
        title: "HR Assistant", 
        description: "Support HR operations including recruitment, employee onboarding, and administrative tasks. Assist with maintaining employee records and coordinating training programs. Good organizational and interpersonal skills required.",
        company_name: "Punjab HR Solutions",
        location: { city: "Chandigarh", state: "Punjab" },
        job_type: "full_time",
        category: "Human Resources",
        salary: { min: 28000, max: 40000, currency: "INR" },
        experience: { min: 1, max: 3 },
        skills_required: ["HR Operations", "MS Office", "Communication", "Record Keeping"],
        remote_allowed: false,
        created_at: "2024-11-22T10:30:00",
        application_deadline: "2024-12-22T23:59:59",
        status: "active"
    },
    {
        job_id: "job_8",
        title: "Sales Executive",
        description: "Drive sales growth by identifying new business opportunities and maintaining client relationships. Experience in B2B sales and knowledge of Punjab market preferred. Meet sales targets and provide excellent customer service.",
        company_name: "Punjab Sales Corp",
        location: { city: "Ludhiana", state: "Punjab" },
        job_type: "full_time",
        category: "Sales",
        salary: { min: 30000, max: 50000, currency: "INR" },
        experience: { min: 2, max: 5 },
        skills_required: ["Sales", "Business Development", "Client Relationship", "Communication"],
        remote_allowed: false,
        created_at: "2024-11-21T14:15:00",
        application_deadline: "2024-12-21T23:59:59", 
        status: "active"
    }
];

// Function to get jobs with filters
function getJobs(filters = {}) {
    let filteredJobs = [...punjabJobs];
    
    if (filters.category) {
        filteredJobs = filteredJobs.filter(job => 
            job.category.toLowerCase() === filters.category.toLowerCase()
        );
    }
    
    if (filters.location) {
        filteredJobs = filteredJobs.filter(job =>
            job.location.city.toLowerCase().includes(filters.location.toLowerCase()) ||
            job.location.state.toLowerCase().includes(filters.location.toLowerCase())
        );
    }
    
    if (filters.job_type) {
        filteredJobs = filteredJobs.filter(job =>
            job.job_type === filters.job_type
        );
    }
    
    if (filters.remote_allowed !== undefined) {
        filteredJobs = filteredJobs.filter(job =>
            job.remote_allowed === filters.remote_allowed
        );
    }
    
    if (filters.search) {
        const searchTerm = filters.search.toLowerCase();
        filteredJobs = filteredJobs.filter(job =>
            job.title.toLowerCase().includes(searchTerm) ||
            job.description.toLowerCase().includes(searchTerm) ||
            job.company_name.toLowerCase().includes(searchTerm) ||
            job.skills_required.some(skill => skill.toLowerCase().includes(searchTerm))
        );
    }
    
    return filteredJobs;
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { punjabJobs, getJobs };
}