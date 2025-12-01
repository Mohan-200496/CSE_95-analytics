/**
 * Local Job Storage System
 * Temporary solution for storing jobs locally until backend enum issues are resolved
 */

class LocalJobStorage {
    constructor() {
        this.storageKey = 'punjab_rozgar_jobs';
        this.init();
    }

    init() {
        // Ensure localStorage exists
        if (!this.getJobs()) {
            this.saveJobs([]);
        }
    }

    // Get all jobs from localStorage
    getJobs() {
        try {
            const jobs = localStorage.getItem(this.storageKey);
            return jobs ? JSON.parse(jobs) : [];
        } catch (error) {
            console.error('Error reading jobs from localStorage:', error);
            return [];
        }
    }

    // Save jobs to localStorage
    saveJobs(jobs) {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(jobs));
            return true;
        } catch (error) {
            console.error('Error saving jobs to localStorage:', error);
            return false;
        }
    }

    // Add a new job
    addJob(jobData) {
        try {
            const jobs = this.getJobs();
            const newJob = {
                job_id: `job_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
                ...jobData,
                status: 'ACTIVE',
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
                published_at: new Date().toISOString(),
                employer_name: jobData.employer_name || 'Local Employer',
                employer_id: `local_${Date.now()}`,
                remote_allowed: jobData.remote_allowed || false,
                resume_required: jobData.resume_required !== undefined ? jobData.resume_required : true,
                salary_currency: 'INR',
                salary_period: 'monthly',
                experience_min: jobData.experience_min || 0
            };

            jobs.push(newJob);
            
            if (this.saveJobs(jobs)) {
                console.log('✅ Job saved locally:', newJob);
                return { success: true, job_id: newJob.job_id, job: newJob };
            } else {
                return { success: false, error: 'Failed to save job locally' };
            }
        } catch (error) {
            console.error('Error adding job:', error);
            return { success: false, error: error.message };
        }
    }

    // Get jobs by filters
    getFilteredJobs(filters = {}) {
        const jobs = this.getJobs();
        
        return jobs.filter(job => {
            // Filter by category
            if (filters.category && job.category !== filters.category) {
                return false;
            }
            
            // Filter by job type
            if (filters.job_type && job.job_type !== filters.job_type) {
                return false;
            }
            
            // Filter by location
            if (filters.location && !job.location_city.toLowerCase().includes(filters.location.toLowerCase())) {
                return false;
            }
            
            // Filter by remote work
            if (filters.remote_only && !job.remote_allowed) {
                return false;
            }
            
            // Filter by salary range
            if (filters.min_salary && job.salary_max && job.salary_max < filters.min_salary) {
                return false;
            }
            if (filters.max_salary && job.salary_min && job.salary_min > filters.max_salary) {
                return false;
            }
            
            return true;
        });
    }

    // Get recent jobs
    getRecentJobs(limit = 10) {
        const jobs = this.getJobs();
        return jobs
            .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
            .slice(0, limit);
    }

    // Get job by ID
    getJobById(jobId) {
        const jobs = this.getJobs();
        return jobs.find(job => job.job_id === jobId);
    }

    // Update job
    updateJob(jobId, updates) {
        try {
            const jobs = this.getJobs();
            const jobIndex = jobs.findIndex(job => job.job_id === jobId);
            
            if (jobIndex === -1) {
                return { success: false, error: 'Job not found' };
            }
            
            jobs[jobIndex] = {
                ...jobs[jobIndex],
                ...updates,
                updated_at: new Date().toISOString()
            };
            
            if (this.saveJobs(jobs)) {
                return { success: true, job: jobs[jobIndex] };
            } else {
                return { success: false, error: 'Failed to update job' };
            }
        } catch (error) {
            console.error('Error updating job:', error);
            return { success: false, error: error.message };
        }
    }

    // Delete job
    deleteJob(jobId) {
        try {
            const jobs = this.getJobs();
            const filteredJobs = jobs.filter(job => job.job_id !== jobId);
            
            if (filteredJobs.length === jobs.length) {
                return { success: false, error: 'Job not found' };
            }
            
            if (this.saveJobs(filteredJobs)) {
                return { success: true };
            } else {
                return { success: false, error: 'Failed to delete job' };
            }
        } catch (error) {
            console.error('Error deleting job:', error);
            return { success: false, error: error.message };
        }
    }

    // Clear all jobs (for testing)
    clearAllJobs() {
        localStorage.removeItem(this.storageKey);
        console.log('🗑️ All local jobs cleared');
    }

    // Export jobs to JSON (for backup)
    exportJobs() {
        const jobs = this.getJobs();
        const dataStr = JSON.stringify(jobs, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = 'punjab_rozgar_jobs_backup.json';
        link.click();
    }

    // Get storage statistics
    getStats() {
        const jobs = this.getJobs();
        const stats = {
            total_jobs: jobs.length,
            active_jobs: jobs.filter(job => job.status === 'ACTIVE').length,
            categories: [...new Set(jobs.map(job => job.category))],
            job_types: [...new Set(jobs.map(job => job.job_type))],
            locations: [...new Set(jobs.map(job => job.location_city))],
            storage_size: new Blob([localStorage.getItem(this.storageKey) || '']).size
        };
        return stats;
    }

    // Sync with backend (future implementation)
    async syncWithBackend() {
        // This will be implemented when backend issues are resolved
        console.log('🔄 Backend sync not yet implemented');
        return { success: false, message: 'Backend sync coming soon' };
    }
}

// Global instance
window.localJobStorage = new LocalJobStorage();

// Console helper functions for testing
window.jobStorageHelpers = {
    stats: () => window.localJobStorage.getStats(),
    export: () => window.localJobStorage.exportJobs(),
    clear: () => window.localJobStorage.clearAllJobs(),
    recent: (limit) => window.localJobStorage.getRecentJobs(limit),
    all: () => window.localJobStorage.getJobs()
};

console.log('📦 Local Job Storage initialized. Use jobStorageHelpers for testing.');