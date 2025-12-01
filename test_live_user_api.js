// Test creating employer account on live API
async function createAndTestEmployer() {
    const baseUrl = 'https://punjab-rozgar-api.onrender.com/api/v1';
    
    try {
        // Create employer account
        console.log('=== CREATING EMPLOYER ACCOUNT ===');
        const registerResponse = await fetch(`${baseUrl}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: 'employer@test.com',
                password: 'password123',
                first_name: 'Test',
                last_name: 'Employer',
                phone: '+1234567890',
                role: 'employer',
                city: 'Chandigarh'
            })
        });
        
        const registerData = await registerResponse.json();
        console.log('Register Status:', registerResponse.status);
        console.log('Register Data:', JSON.stringify(registerData, null, 2));
        
        // Now try login
        console.log('\n=== TESTING LOGIN ===');
        const loginResponse = await fetch(`${baseUrl}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: 'employer@test.com',
                password: 'employer123'
            })
        });
        
        const loginData = await loginResponse.json();
        console.log('Login Status:', loginResponse.status);
        console.log('Login Data:', JSON.stringify(loginData, null, 2));
        
        // Check user role specifically
        if (loginData.user) {
            console.log('\n=== ROLE CHECK ===');
            console.log('User role value:', loginData.user.role);
            console.log('Role type:', typeof loginData.user.role);
            console.log('Role length:', loginData.user.role?.length);
        }
        
    } catch (error) {
        console.error('API Test Error:', error);
    }
}

createAndTestEmployer();