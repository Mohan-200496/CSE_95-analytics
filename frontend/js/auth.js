/**
 * Punjab Rozgar Authentication System
 * Handles user authentication, role management, and session persistence
 */

(function() {
    'use strict';
    
    // Only define if not already defined
    if (window.AuthManager) return;
    
    class AuthManager {
    constructor() {
        this.currentUser = null;
        this.userRoles = {
            ADMIN: 'admin',
            EMPLOYER: 'employer', 
            JOB_SEEKER: 'job_seeker'
        };
        
        // Use environment configuration for API base URL
        this.apiBaseUrl = this.getApiBaseUrl();
        this.accessToken = null;
        this.init();
    }

    getApiBaseUrl() {
        // Check if environment config is available
        if (window.ENV_CONFIG && window.ENV_CONFIG.apiUrl) {
            console.log('🌐 Using environment API URL:', window.ENV_CONFIG.apiUrl);
            return window.ENV_CONFIG.apiUrl + '/api/v1';
        }
        
        // Check alternative environment config
        if (window.EnvironmentConfig) {
            try {
                const envConfig = new window.EnvironmentConfig();
                console.log('🌐 Using EnvironmentConfig API URL:', envConfig.config.API_BASE_URL);
                return envConfig.config.API_BASE_URL + '/api/v1';
            } catch (e) {
                console.warn('Failed to create EnvironmentConfig:', e);
            }
        }
        
        // Fallback - try to detect environment manually
        const hostname = window.location.hostname;
        if (hostname.includes('onrender.com')) {
            console.log('🌐 Detected Render environment, using live API');
            return 'https://cse-95-analytics.onrender.com/api/v1';
        }
        
        // Development fallback
        console.log('🌐 Using development API URL');
        return 'http://localhost:8000/api/v1';
    }

    init() {
        // Load user from localStorage on page load
        this.loadUserFromStorage();
        this.loadTokenFromStorage();
        this.setupAuthUI();
        
        // Ensure UI updates once DOM is ready (in case script loads in <head>)
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupAuthUI());
        }
        
        // Setup test users if no user is logged in
        this.setupTestUsers();
    }

    // Authentication Methods
    async login(email, password, rememberMe = false) {
        try {
            console.log('Attempting login with:', { 
                email, 
                apiUrl: `${this.apiBaseUrl}/auth/login`,
                userAgent: navigator.userAgent,
                timestamp: new Date().toISOString()
            });
            
            // Mobile-friendly fetch with additional options
            const fetchOptions = {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Cache-Control': 'no-cache'
                },
                body: JSON.stringify({ email, password }),
                mode: 'cors'
                // Removed credentials: 'include' to avoid CORS wildcard issue
            };

            console.log('Fetch options:', fetchOptions);
            
            const response = await fetch(`${this.apiBaseUrl}/auth/login`, fetchOptions);

            console.log('Login response status:', response.status);
            console.log('Login response headers:', Object.fromEntries(response.headers.entries()));
            
            let data;
            try {
                data = await response.json();
                console.log('Login response data:', data);
            } catch (parseError) {
                console.error('Failed to parse JSON response:', parseError);
                const textResponse = await response.text();
                console.log('Raw response text:', textResponse);
                throw new Error(`Invalid JSON response: ${textResponse}`);
            }
            
            if (response.ok && data.success) {
                this.accessToken = data.access_token;
                this.setCurrentUser(data.user, rememberMe);
                this.setAccessToken(data.access_token, rememberMe);
                
                console.log('🎉 Login successful! User data:', data.user);
                console.log('🎭 User role from API:', data.user.role);
                console.log('🎯 About to redirect with role:', data.user.role);
                
                // Don't redirect in test mode
                if (!window.location.pathname.includes('test-auth')) {
                    this.redirectAfterLogin(data.user.role);
                }
                return { success: true, user: data.user };
            } else {
                return { success: false, error: data.message || 'Login failed' };
            }
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, error: 'Network error. Please try again.' };
        }
    }

    async register(userData) {
        try {
            console.log('Attempting registration with:', { userData, apiUrl: `${this.apiBaseUrl}/auth/register` });
            
            // Normalize role to allowed values
            const allowedRoles = ['job_seeker', 'employer'];
            const normalizedRole = allowedRoles.includes(userData.role) ? userData.role : 'job_seeker';

            const response = await fetch(`${this.apiBaseUrl}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: userData.email,
                    password: userData.password,
                    first_name: userData.firstName,
                    last_name: userData.lastName,
                    phone: userData.phone,
                    role: normalizedRole,
                    city: userData.city
                })
            });

            console.log('Registration response status:', response.status);
            const data = await response.json();
            console.log('Registration response data:', data);
            
            if (response.ok && data.success) {
                this.accessToken = data.access_token;
                this.setCurrentUser(data.user, false);
                this.setAccessToken(data.access_token, false);
                // Don't redirect in test mode
                if (!window.location.pathname.includes('test-auth')) {
                    this.redirectAfterLogin(data.user.role);
                }
                return { success: true, user: data.user };
            } else {
                const backendMsg = data?.detail || data?.message;
                // Friendly error for role mismatch
                const friendly = (backendMsg && backendMsg.toLowerCase().includes('role must be'))
                    ? 'Please choose Job Seeker or Employer as your role.'
                    : (backendMsg || 'Registration failed');
                return { success: false, error: friendly };
            }
        } catch (error) {
            console.error('Registration error:', error);
            return { success: false, error: 'Network error. Please try again.' };
        }
    }

    logout() {
        console.log('🚪 Logging out user...');
        this.currentUser = null;
        this.accessToken = null;
        localStorage.removeItem('user');
        localStorage.removeItem('access_token');
        sessionStorage.removeItem('user');
        sessionStorage.removeItem('access_token');
        
        // Update UI to show logged out state
        this.setupAuthUI();
        
        // Show logout success message
        console.log('✅ User logged out successfully');
        
        // Only redirect if we're in a protected area (not on public pages)
        const currentPath = window.location.pathname;
        const publicPages = ['/index.html', '/', '/pages/auth/login.html', '/pages/auth/register.html'];
        const isOnPublicPage = publicPages.some(page => currentPath.endsWith(page) || currentPath === page);
        
        if (!isOnPublicPage && (currentPath.includes('/admin/') || currentPath.includes('/employer/') || currentPath.includes('/jobseeker/') || currentPath.includes('/profile/'))) {
            console.log('🔄 Redirecting from protected area to home page');
            window.location.href = '/index.html';
        } else {
            console.log('✅ Staying on current public page, no redirect needed');
            // Reload the page to refresh the UI if we're on a public page
            if (currentPath.includes('index.html') || currentPath === '/') {
                window.location.reload();
            }
        }
    }

    // User Management
    setCurrentUser(user, persistent = false) {
        this.currentUser = user;
        
        const userData = {
            id: user.id,
            user_id: user.user_id, // Add user_id for API calls
            email: user.email,
            name: user.name,
            role: user.role,
            profile: user.profile || {},
            loginTime: new Date().toISOString()
        };

        if (persistent) {
            localStorage.setItem('user', JSON.stringify(userData));
        } else {
            sessionStorage.setItem('user', JSON.stringify(userData));
        }
        
        this.setupAuthUI();
    }

    loadUserFromStorage() {
        const userData = localStorage.getItem('user') || sessionStorage.getItem('user');
        if (userData) {
            try {
                this.currentUser = JSON.parse(userData);
                this.setupAuthUI();
            } catch (error) {
                console.error('Error loading user data:', error);
                this.logout();
            }
        }
    }

    loadTokenFromStorage() {
        this.accessToken = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
        
        // Validate token if it exists
        if (this.accessToken) {
            if (!this.validateToken()) {
                this.accessToken = null;
            }
        }
    }
    
    validateToken() {
        if (!this.accessToken) return false;
        
        try {
            // Parse JWT token to check expiration
            const tokenParts = this.accessToken.split('.');
            if (tokenParts.length !== 3) {
                console.log('🚫 Invalid token format');
                return false;
            }
            
            const payload = JSON.parse(atob(tokenParts[1]));
            const currentTime = Math.floor(Date.now() / 1000);
            
            if (payload.exp && payload.exp < currentTime) {
                console.log('🕐 Token has expired');
                return false;
            }
            
            // Check if token expires in next 5 minutes (warn user)
            if (payload.exp && (payload.exp - currentTime) < 300) {
                console.log('⚠️ Token expires soon');
                if (window.showMessage) {
                    window.showMessage('Your session will expire soon. Please save your work.', 'warning');
                }
            }
            
            return true;
        } catch (error) {
            console.error('Error validating token:', error);
            return false;
        }
    }

    setAccessToken(token, persistent = false) {
        this.accessToken = token;
        if (persistent) {
            localStorage.setItem('access_token', token);
        } else {
            sessionStorage.setItem('access_token', token);
        }
    }

    getAuthHeaders() {
        return {
            'Content-Type': 'application/json',
            ...(this.accessToken && { 'Authorization': `Bearer ${this.accessToken}` })
        };
    }

    getCurrentUser() {
        return this.currentUser;
    }

    isLoggedIn() {
        // Check current user, but also check storage as backup
        if (this.currentUser !== null) {
            return true;
        }
        
        // Check if user data exists in storage
        const storedUser = localStorage.getItem('user') || sessionStorage.getItem('user');
        if (storedUser) {
            try {
                this.currentUser = JSON.parse(storedUser);
                console.log('🔄 Session restored from storage');
                return true;
            } catch (error) {
                console.error('❌ Error restoring session:', error);
                return false;
            }
        }
        
        return false;
    }

    hasRole(role) {
        return this.currentUser && this.currentUser.role === role;
    }

    isAdmin() {
        return this.hasRole(this.userRoles.ADMIN);
    }

    isEmployer() {
        return this.hasRole(this.userRoles.EMPLOYER);
    }

    isJobSeeker() {
        return this.hasRole(this.userRoles.JOB_SEEKER);
    }

    // API Helper Methods
    async makeApiCall(endpoint, options = {}) {
        try {
            // Validate token before making request
            if (this.accessToken && !this.validateToken()) {
                console.log('🚫 Token validation failed, logging out');
                this.logout();
                throw new Error('Session expired');
            }
            
            const response = await fetch(`${this.apiBaseUrl}${endpoint}`, {
                headers: this.getAuthHeaders(),
                ...options
            });

            if (response.status === 401) {
                // Token expired or invalid
                console.log('🔄 Received 401, handling token expiration');
                
                // Try to get the error message
                const errorData = await response.json().catch(() => ({}));
                
                if (errorData.message && errorData.message.includes('expired')) {
                    console.log('🕐 Token has expired, logging out user');
                    this.logout();
                    
                    // Show user-friendly message
                    if (window.showMessage) {
                        window.showMessage('Your session has expired. Please log in again.', 'warning');
                    } else {
                        alert('Your session has expired. Please log in again.');
                    }
                    
                    // Redirect to login page after a short delay
                    setTimeout(() => {
                        window.location.href = '/frontend/pages/auth/login.html';
                    }, 2000);
                }
                
                return null;
            }

            return await response.json();
        } catch (error) {
            console.error('API call error:', error);
            throw error;
        }
    }

    async getCurrentUserProfile() {
        if (!this.isLoggedIn()) return null;
        
        try {
            const data = await this.makeApiCall('/users/profile');
            return data;
        } catch (error) {
            console.error('Error fetching user profile:', error);
            return null;
        }
    }

    async updateUserProfile(profileData) {
        if (!this.isLoggedIn()) return { success: false, error: 'Not logged in' };
        
        try {
            const data = await this.makeApiCall('/users/profile', {
                method: 'PUT',
                body: JSON.stringify(profileData)
            });
            return data;
        } catch (error) {
            console.error('Error updating user profile:', error);
            return { success: false, error: 'Failed to update profile' };
        }
    }

    // Redirect Logic
    redirectAfterLogin(role) {
        console.log('🔄 redirectAfterLogin called with role:', role);
        console.log('🎭 Available userRoles:', this.userRoles);
        console.log('🔍 Role type:', typeof role);
        
        // Normalize role (handle both string and object cases)
        const normalizedRole = typeof role === 'string' ? role.toLowerCase().trim() : 
                              (role?.value || role?.name || String(role)).toLowerCase().trim();
        console.log('🔧 Normalized role:', normalizedRole);
        
        // Enhanced role mapping - handle all possible variations
        let redirectUrl = '/index.html'; // default fallback
        
        if (normalizedRole === 'admin' || normalizedRole === 'administrator') {
            redirectUrl = '/pages/admin/dashboard.html';
            console.log('✅ Redirecting to ADMIN dashboard');
        } else if (normalizedRole === 'employer' || normalizedRole === 'recruiter') {
            redirectUrl = '/pages/employer/dashboard.html';
            console.log('✅ Redirecting to EMPLOYER dashboard');
        } else if (normalizedRole === 'job_seeker' || normalizedRole === 'jobseeker' || normalizedRole === 'seeker') {
            redirectUrl = '/pages/jobseeker/dashboard.html';
            console.log('✅ Redirecting to JOB_SEEKER dashboard');
        } else {
            // If role is unclear, check user email to determine correct role
            const user = this.getCurrentUser();
            if (user && user.email) {
                if (user.email.includes('admin')) {
                    redirectUrl = '/pages/admin/dashboard.html';
                    console.log('🔄 Email-based redirect: ADMIN dashboard');
                } else if (user.email.includes('employer')) {
                    redirectUrl = '/pages/employer/dashboard.html';
                    console.log('🔄 Email-based redirect: EMPLOYER dashboard');
                } else {
                    redirectUrl = '/pages/jobseeker/dashboard.html';
                    console.log('🔄 Email-based redirect: JOB_SEEKER dashboard (default)');
                }
            } else {
                console.log('⚠️ Unknown role and no user email, defaulting to job seeker');
                redirectUrl = '/pages/jobseeker/dashboard.html';
            }
        }
        
        console.log(`🚀 Final redirect URL: ${redirectUrl}`);
        window.location.href = redirectUrl;
    }

    // UI Management
    setupAuthUI() {
        this.updateNavigation();
        this.updateUserProfile();
        this.enforceRoleBasedAccess();
    }

    updateNavigation() {
        const authButtons = document.querySelector('.auth-buttons');
        const userMenu = document.querySelector('.user-menu');
        
        console.log('🎨 Updating navigation, logged in:', this.isLoggedIn());
        
        if (this.isLoggedIn()) {
            // Hide login/register buttons
            if (authButtons) {
                authButtons.style.display = 'none';
            }
            
            // Show user menu
            if (userMenu) {
                userMenu.style.display = 'flex';
                this.populateUserMenu();
                console.log('👤 User menu displayed');
            } else {
                console.log('🏗️ Creating new user menu');
                this.createUserMenu();
            }
        } else {
            // Show login/register buttons
            if (authButtons) {
                authButtons.style.display = 'flex';
            }
            
            // Hide user menu
            if (userMenu) {
                userMenu.style.display = 'none';
            }
        }
    }

    createUserMenu() {
        const nav = document.querySelector('.nav') || document.querySelector('.navbar');
        if (!nav) return;

        const userMenuHTML = `
            <div class="user-menu" style="display: flex; align-items: center; gap: 1rem;">
                <span class="user-greeting">Hello, ${this.currentUser?.name || this.currentUser?.email || 'User'}</span>
                <div class="user-dropdown">
                    <button class="user-avatar" onclick="toggleUserDropdown()">
                        <i class="fas fa-user-circle"></i>
                    </button>
                    <div class="dropdown-menu" id="userDropdownMenu">
                        <a href="${this.getDashboardUrl()}" class="dropdown-item">
                            <i class="fas fa-tachometer-alt"></i> Dashboard
                        </a>
                        <a href="pages/profile/profile.html" class="dropdown-item">
                            <i class="fas fa-user"></i> Profile
                        </a>
                        <div class="dropdown-divider"></div>
                        <button onclick="authManager.logout()" class="dropdown-item logout-btn">
                            <i class="fas fa-sign-out-alt"></i> Logout
                        </button>
                    </div>
                </div>
            </div>
        `;

        nav.insertAdjacentHTML('beforeend', userMenuHTML);
    }

    getUserInitials() {
        if (!this.currentUser) return 'U';
        
        const firstName = this.currentUser.first_name || this.currentUser.name?.split(' ')[0] || '';
        const lastName = this.currentUser.last_name || this.currentUser.name?.split(' ')[1] || '';
        
        const first = firstName.charAt(0).toUpperCase();
        const last = lastName.charAt(0).toUpperCase();
        
        return first + last || first || 'U';
    }

    populateUserMenu() {
        const userGreeting = document.querySelector('.user-greeting');
        const userAvatar = document.querySelector('.user-avatar');
        const userName = document.querySelector('.user-name');
        
        console.log('👤 Populating user menu with current user:', this.currentUser);
        
        if (this.currentUser) {
            const firstName = this.currentUser.first_name || this.currentUser.name?.split(' ')[0] || 'User';
            const fullName = this.currentUser.name || `${this.currentUser.first_name || ''} ${this.currentUser.last_name || ''}`.trim() || 'User';
            const role = this.currentUser.role || 'user';
            
            if (userGreeting) {
                userGreeting.textContent = `Hello, ${firstName}!`;
                console.log('✅ Updated user greeting:', userGreeting.textContent);
            }
            
            if (userName) {
                userName.textContent = fullName;
                console.log('✅ Updated user name:', userName.textContent);
            }
            
            if (userAvatar) {
                const initials = this.getUserInitials();
                userAvatar.innerHTML = initials;
                userAvatar.title = `${fullName} (${role})`;
                console.log('✅ Updated user avatar:', initials);
            }
            
            console.log('👤 User menu populated:', { firstName, fullName, role });
        } else {
            console.log('⚠️ No current user found for menu population');
        }
    }

    getDashboardUrl() {
        switch (this.currentUser.role) {
            case this.userRoles.ADMIN:
                return '/pages/admin/dashboard.html';
            case this.userRoles.EMPLOYER:
                return '/pages/employer/dashboard.html';
            case this.userRoles.JOB_SEEKER:
                return '/pages/jobseeker/dashboard.html';
            default:
                return '/index.html';
        }
    }

    updateUserProfile() {
        const profileElements = document.querySelectorAll('[data-user-name]');
        const roleElements = document.querySelectorAll('[data-user-role]');
        
        if (this.isLoggedIn()) {
            profileElements.forEach(el => el.textContent = this.currentUser.name);
            roleElements.forEach(el => el.textContent = this.currentUser.role);
        }
    }

    enforceRoleBasedAccess() {
        // Hide/show elements based on user role
        const adminOnly = document.querySelectorAll('[data-role="admin"]');
        const employerOnly = document.querySelectorAll('[data-role="employer"]');
        const jobSeekerOnly = document.querySelectorAll('[data-role="job_seeker"]');
        const loggedInOnly = document.querySelectorAll('[data-auth="required"]');
        const loggedOutOnly = document.querySelectorAll('[data-auth="guest"]');

        // Show/hide based on authentication status
        loggedInOnly.forEach(el => {
            el.style.display = this.isLoggedIn() ? 'block' : 'none';
        });
        
        loggedOutOnly.forEach(el => {
            el.style.display = this.isLoggedIn() ? 'none' : 'block';
        });

        if (this.isLoggedIn()) {
            // Show/hide based on role
            adminOnly.forEach(el => {
                el.style.display = this.isAdmin() ? 'block' : 'none';
            });
            
            employerOnly.forEach(el => {
                el.style.display = this.isEmployer() ? 'block' : 'none';
            });
            
            jobSeekerOnly.forEach(el => {
                el.style.display = this.isJobSeeker() ? 'block' : 'none';
            });
        }
    }

    // Page Protection
    requireAuth(redirectUrl = '/pages/auth/login.html') {
        if (!this.isLoggedIn()) {
            window.location.href = redirectUrl;
            return false;
        }
        return true;
    }

    requireRole(requiredRole, redirectUrl = '/index.html') {
        if (!this.isLoggedIn() || !this.hasRole(requiredRole)) {
            window.location.href = redirectUrl;
            return false;
        }
        return true;
    }

    requireRoles(requiredRoles, redirectUrl = '/index.html') {
        if (!this.isLoggedIn() || !requiredRoles.includes(this.currentUser.role)) {
            window.location.href = redirectUrl;
            return false;
        }
        return true;
    }

    // Testing/Development Methods (remove in production)
    setTestAdminUser() {
        const testAdmin = {
            id: 1,
            user_id: 'admin_test_user',
            email: 'admin@punjab.gov.in',
            name: 'Test Admin',
            role: 'admin',
            profile: {}
        };
        this.setCurrentUser(testAdmin, false);
        console.log('Test admin user set:', testAdmin);
    }

    // Setup test users for different roles - DISABLED for role-based dashboard testing
    setupTestUsers() {
        // Disabled automatic test user setup to prevent interference with real authentication
        // Users should manually login with: admin@test.com, employer@test.com, jobseeker@test.com
        return;
    }

    setTestJobSeeker() {
        const testJobSeeker = {
            id: 3,
            user_id: 'jobseeker_test_user', 
            email: 'seeker@test.com',
            name: 'Test Job Seeker',
            role: 'job_seeker',
            profile: {
                skills: ['JavaScript', 'React', 'Node.js'],
                experience_years: 3,
                location: 'Chandigarh, Punjab'
            }
        };
        this.setCurrentUser(testJobSeeker, false);
        console.log('Test job seeker user set:', testJobSeeker);
    }

    setTestEmployer() {
        const testEmployer = {
            id: 2,
            user_id: 'employer_test_user',
            email: 'employer@test.com', 
            name: 'Test Employer',
            role: 'employer',
            profile: {}
        };
        this.setCurrentUser(testEmployer, false);
        console.log('Test employer user set:', testEmployer);
    }
}

// Global functions for dropdown
function toggleUserDropdown() {
    const dropdown = document.getElementById('userDropdownMenu');
    if (dropdown) {
        dropdown.classList.toggle('show');
    }
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const dropdown = document.getElementById('userDropdownMenu');
    const userAvatar = document.querySelector('.user-avatar');
    
    if (dropdown && (!userAvatar || !userAvatar.contains(event.target))) {
        dropdown.classList.remove('show');
    }
});

// Initialize global auth manager
// Initialize global instance
window.AuthManager = AuthManager;
const authManager = new AuthManager();

// Make authManager globally available
window.authManager = authManager;

})(); // End IIFE

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = window.AuthManager;
}