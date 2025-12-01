// Test job creation and retrieval APIs
async function testJobAPIs() {
    const baseUrl = 'https://punjab-rozgar-api.onrender.com/api/v1';
    
    try {
        // First login to get token
        console.log('=== LOGGING IN ===');
        const loginResponse = await fetch(`${baseUrl}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: 'employer@test.com',
                password: 'employer123'
            })
        });
        
        const loginData = await loginResponse.json();
        console.log('Login status:', loginResponse.status);
        
        if (!loginData.access_token) {
            console.error('No access token received');
            return;
        }
        
        const token = loginData.access_token;
        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
        
        // Test creating a job
        console.log('\n=== CREATING JOB ===');
        const jobData = {
            title: 'Test Job API',
            description: 'This is a test job created via API',
            category: 'Technology',
            location_city: 'Chandigarh',
            job_type: 'full_time',
            salary_min: 30000,
            salary_max: 50000,
            experience_min: 1,
            experience_max: 3
        };
        
        const createResponse = await fetch(`${baseUrl}/jobs/`, {
            method: 'POST',
            headers,
            body: JSON.stringify(jobData)
        });
        
        const createData = await createResponse.json();
        console.log('Create job status:', createResponse.status);
        console.log('Create job response:', JSON.stringify(createData, null, 2));
        
        // Test getting employer's jobs
        console.log('\n=== GETTING MY JOBS ===');
        const myJobsResponse = await fetch(`${baseUrl}/jobs/my-jobs`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        const myJobsData = await myJobsResponse.json();
        console.log('My jobs status:', myJobsResponse.status);
        console.log('My jobs count:', Array.isArray(myJobsData) ? myJobsData.length : 'Not array');
        console.log('My jobs response:', JSON.stringify(myJobsData, null, 2));
        
        // Test getting all jobs (public)
        console.log('\n=== GETTING ALL JOBS ===');
        const allJobsResponse = await fetch(`${baseUrl}/jobs/`);
        const allJobsData = await allJobsResponse.json();
        console.log('All jobs status:', allJobsResponse.status);
        console.log('All jobs count:', Array.isArray(allJobsData) ? allJobsData.length : 'Not array');
        console.log('All jobs response:', JSON.stringify(allJobsData, null, 2));
        // Test admin jobs endpoint
        console.log('\n=== TESTING ADMIN JOBS ENDPOINT ===');
        const adminJobsResponse = await fetch(`${baseUrl}/admin/jobs`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        const adminJobsData = await adminJobsResponse.json();
        console.log('Admin jobs status:', adminJobsResponse.status);
        console.log('Admin jobs count:', Array.isArray(adminJobsData) ? adminJobsData.length : 'Not array');
        console.log('Admin jobs response:', JSON.stringify(adminJobsData, null, 2));
        
    } catch (error) {
        console.error('API Test Error:', error);
    }
}

testJobAPIs();