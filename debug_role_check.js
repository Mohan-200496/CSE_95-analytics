// Quick test to check current user data
const auth = window.AuthManager || new AuthManager();

console.log('=== DEBUGGING EMPLOYER ACCESS ===');
console.log('Current user:', auth.currentUser);
console.log('User role from storage:', localStorage.getItem('user'));
console.log('Has employer role?', auth.hasRole('employer'));
console.log('Is employer?', auth.isEmployer());

// Test with specific role check
if (auth.currentUser && auth.currentUser.role) {
    console.log('Raw role value:', auth.currentUser.role);
    console.log('Role type:', typeof auth.currentUser.role);
    console.log('Role length:', auth.currentUser.role.length);
    
    // Test direct role checks
    const testRoles = ['employer', 'EMPLOYER', 'Employer'];
    testRoles.forEach(role => {
        console.log(`Testing role "${role}":`, auth.hasRole(role));
    });
}