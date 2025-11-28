// Quick fix for browse page - add this to make trackEvent available
window.trackEvent = function(event, data) {
    try {
        console.log('Analytics event tracked:', event, data);
        // Send to backend analytics if available
        if (typeof window.analyticsManager !== 'undefined') {
            window.analyticsManager.track(event, data);
        }
    } catch (error) {
        console.warn('Analytics tracking failed:', error);
    }
};

// Fix the jobs API loading function
window.loadJobsFromApiFixed = async function(params = {}) {
    try {
        const query = new URLSearchParams();
        query.set('only_active', 'true');
        if (params.search && params.search.trim()) query.set('search', params.search.trim());
        if (params.location_city && params.location_city.trim()) query.set('location_city', params.location_city.trim());
        if (params.job_type && params.job_type.trim()) query.set('job_type', params.job_type.trim());

        const url = `http://localhost:8000/api/v1/jobs/${query.toString() ? `?${query.toString()}` : ''}`;
        
        const response = await fetch(url, { 
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`Failed to load jobs (${response.status})`);
        }
        
        const jobs = await response.json();
        console.log('✅ Jobs loaded successfully:', jobs.length);
        
        // Update job count
        const jobCountEl = document.getElementById('job-count');
        if (jobCountEl) jobCountEl.textContent = jobs.length;

        // Render jobs (simplified)
        const jobsGrid = document.getElementById('jobs-grid');
        if (jobsGrid) {
            if (!jobs.length) {
                jobsGrid.innerHTML = '<p>No jobs found matching your criteria.</p>';
            } else {
                jobsGrid.innerHTML = jobs.map(job => `
                    <div class="job-card">
                        <h3>${job.title}</h3>
                        <p><strong>Company:</strong> ${job.company_name || 'Unknown Company'}</p>
                        <p><strong>Location:</strong> ${job.location_city || 'Not specified'}</p>
                        <p><strong>Type:</strong> ${job.job_type || 'Not specified'}</p>
                        <p>${job.description ? job.description.substring(0, 150) + '...' : 'No description available'}</p>
                    </div>
                `).join('');
            }
        }
        
        return jobs;
    } catch (error) {
        console.error('Error loading jobs:', error);
        const jobsGrid = document.getElementById('jobs-grid');
        if (jobsGrid) {
            jobsGrid.innerHTML = `<p style="color: red;">Error loading jobs: ${error.message}</p>`;
        }
        return [];
    }
};

console.log('✅ Browse page fixes loaded - call loadJobsFromApiFixed() to test');