/**
 * Simple API server for Punjab Rozgar Portal
 * Serves job data and handles basic filtering
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

// Load job data
const jobsData = JSON.parse(fs.readFileSync(path.join(__dirname, 'jobs.json'), 'utf8'));

// CORS headers
const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
};

// Create server
const server = http.createServer((req, res) => {
    const parsedUrl = url.parse(req.url, true);
    const pathname = parsedUrl.pathname;
    const query = parsedUrl.query;

    // Set CORS headers
    Object.keys(corsHeaders).forEach(key => {
        res.setHeader(key, corsHeaders[key]);
    });

    // Handle preflight requests
    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    // Route: Get all jobs
    if (pathname === '/jobs' && req.method === 'GET') {
        let filteredJobs = [...jobsData.jobs];

        // Filter by category
        if (query.category) {
            filteredJobs = filteredJobs.filter(job => 
                job.category.toLowerCase().includes(query.category.toLowerCase())
            );
        }

        // Filter by location
        if (query.location) {
            filteredJobs = filteredJobs.filter(job => 
                job.location_city.toLowerCase().includes(query.location.toLowerCase())
            );
        }

        // Filter by search term
        if (query.search) {
            const searchTerm = query.search.toLowerCase();
            filteredJobs = filteredJobs.filter(job => 
                job.title.toLowerCase().includes(searchTerm) ||
                job.employer_name.toLowerCase().includes(searchTerm) ||
                job.skills_required.some(skill => skill.toLowerCase().includes(searchTerm))
            );
        }

        // Limit results
        const limit = parseInt(query.limit) || 50;
        const offset = parseInt(query.offset) || 0;
        const paginatedJobs = filteredJobs.slice(offset, offset + limit);

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            jobs: paginatedJobs,
            total: filteredJobs.length,
            limit,
            offset
        }));
        return;
    }

    // Route: Get job by ID
    if (pathname.startsWith('/jobs/') && req.method === 'GET') {
        const jobId = pathname.split('/')[2];
        const job = jobsData.jobs.find(j => j.job_id === jobId);

        if (job) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(job));
        } else {
            res.writeHead(404, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Job not found' }));
        }
        return;
    }

    // Route: Get recommended jobs
    if (pathname === '/jobs/recommended' && req.method === 'GET') {
        // Return a subset of jobs as recommendations
        const recommendations = jobsData.jobs
            .sort(() => Math.random() - 0.5) // Shuffle
            .slice(0, 6); // Take first 6

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(recommendations));
        return;
    }

    // Route: Get categories
    if (pathname === '/categories' && req.method === 'GET') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(jobsData.categories));
        return;
    }

    // Route: Get locations
    if (pathname === '/locations' && req.method === 'GET') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(jobsData.locations));
        return;
    }

    // Route: Submit application
    if (pathname === '/applications' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => {
            body += chunk.toString();
        });

        req.on('end', () => {
            try {
                const applicationData = JSON.parse(body);
                
                // Simulate saving application
                const response = {
                    success: true,
                    application_id: 'app_' + Date.now(),
                    message: 'Application submitted successfully',
                    data: applicationData
                };

                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify(response));
            } catch (error) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Invalid JSON data' }));
            }
        });
        return;
    }

    // Route: Get user applications
    if (pathname === '/applications' && req.method === 'GET') {
        const mockApplications = [
            {
                application_id: 'app_001',
                job_id: 'tech_001',
                job_title: 'Senior Full Stack Developer',
                employer_name: 'TechCorp Solutions Chandigarh',
                applied_date: '2024-11-20',
                status: 'Under Review'
            },
            {
                application_id: 'app_002',
                job_id: 'tech_002', 
                job_title: 'React Frontend Developer',
                employer_name: 'Digital Innovations Mohali',
                applied_date: '2024-11-18',
                status: 'Interview Scheduled'
            }
        ];

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(mockApplications));
        return;
    }

    // 404 for unknown routes
    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Endpoint not found' }));
});

const PORT = process.env.PORT || 3001;

server.listen(PORT, () => {
    console.log(`🚀 Punjab Rozgar API Server running on port ${PORT}`);
    console.log(`📊 Serving ${jobsData.jobs.length} jobs across ${jobsData.categories.length} categories`);
    console.log(`🌐 API endpoints:`);
    console.log(`   - GET /jobs - List all jobs (with filtering)`);
    console.log(`   - GET /jobs/:id - Get specific job`);
    console.log(`   - GET /jobs/recommended - Get recommended jobs`);
    console.log(`   - GET /categories - Get job categories`);
    console.log(`   - GET /locations - Get job locations`);
    console.log(`   - POST /applications - Submit job application`);
    console.log(`   - GET /applications - Get user applications`);
});

module.exports = server;