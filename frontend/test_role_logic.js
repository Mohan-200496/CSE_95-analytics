// Quick frontend test to verify role checking logic
console.log('=== FRONTEND ROLE TEST ===');

// Simulate the correct user data from API
const testUser = {
    "id": 3,
    "user_id": "user_3c50c0cc478f", 
    "email": "employer@test.com",
    "role": "employer",
    "status": "PENDING_VERIFICATION",
    "first_name": "Test",
    "last_name": "Employer",
    "name": "Test Employer"
};

// Test role checking logic
function hasRole(user, role) {
    if (!user || !user.role) return false;
    
    const userRole = user.role.toLowerCase().trim();
    const requiredRole = role.toLowerCase().trim();
    
    console.log('🔍 Role check:', { userRole, requiredRole });
    
    if (userRole === requiredRole) {
        console.log('✅ Role match found');
        return true;
    }
    
    const roleVariations = {
        'job_seeker': userRole === 'job_seeker' || userRole === 'jobseeker',
        'jobseeker': userRole === 'job_seeker' || userRole === 'jobseeker', 
        'employer': userRole === 'employer',
        'admin': userRole === 'admin' || userRole === 'administrator'
    };
    
    const hasAccess = roleVariations[requiredRole] || false;
    console.log(hasAccess ? '✅ Role variation match' : '❌ No role match');
    return hasAccess;
}

// Test the role function
console.log('Test user:', testUser);
console.log('Has employer role?', hasRole(testUser, 'employer'));
console.log('Has admin role?', hasRole(testUser, 'admin'));

// Test if localStorage has old data
console.log('\nLocalStorage check:');
console.log('user:', localStorage.getItem('user'));
console.log('access_token:', localStorage.getItem('access_token'));

// Clear localStorage and set correct data
localStorage.removeItem('user');
localStorage.removeItem('access_token');
localStorage.setItem('user', JSON.stringify(testUser));
localStorage.setItem('access_token', 'test_token');

console.log('✅ Updated localStorage with correct user data');