// Create admin user and test admin endpoints
async function testAdminFlow() {
    const baseUrl = 'https://punjab-rozgar-api.onrender.com/api/v1';
    
    try {
        // Create admin account
        console.log('=== CREATING ADMIN ACCOUNT ===');
        const registerResponse = await fetch(`${baseUrl}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: 'admin@test.com',
                password: 'admin123',
                first_name: 'Test',
                last_name: 'Admin',
                phone: '+1234567892',
                role: 'admin',  // Try to register as admin
                city: 'Amritsar'
            })
        });
        
        const registerData = await registerResponse.json();
        console.log('Register Status:', registerResponse.status);
        console.log('Register Data:', JSON.stringify(registerData, null, 2));
        
        // Try login
        console.log('\n=== ADMIN LOGIN ===');
        const loginResponse = await fetch(`${baseUrl}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: 'admin@test.com',
                password: 'admin123'
            })
        });
        
        const loginData = await loginResponse.json();
        console.log('Login Status:', loginResponse.status);
        console.log('Login Data:', JSON.stringify(loginData, null, 2));
        
        if (loginData.access_token) {
            // Test admin jobs endpoint
            console.log('\n=== TESTING ADMIN JOBS ===');
            const adminJobsResponse = await fetch(`${baseUrl}/admin/jobs`, {
                headers: { 'Authorization': `Bearer ${loginData.access_token}` }
            });
            
            const adminJobsData = await adminJobsResponse.json();
            console.log('Admin jobs status:', adminJobsResponse.status);
            console.log('Admin jobs response:', JSON.stringify(adminJobsData, null, 2));
        }
        
    } catch (error) {
        console.error('Admin Test Error:', error);
    }
}

testAdminFlow();