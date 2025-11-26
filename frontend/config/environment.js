// Punjab Rozgar Portal - Environment Configuration
// Automatically detects and configures API endpoints for different deployment environments

class EnvironmentConfig {
    constructor() {
        this.environment = this.detectEnvironment();
        this.config = this.getConfig();
    }

    detectEnvironment() {
        const hostname = window.location.hostname;
        
        // Production detection patterns
        if (hostname.includes('.herokuapp.com')) return 'heroku';
        if (hostname.includes('.vercel.app')) return 'vercel';
        if (hostname.includes('.onrender.com')) return 'render';
        if (hostname.includes('.railway.app')) return 'railway';
        if (hostname.includes('.netlify.app')) return 'netlify';
        
        // Local development
        if (hostname === 'localhost' || hostname === '127.0.0.1') return 'development';
        
        // Custom domain (production)
        return 'production';
    }

    getConfig() {
        const configs = {
            development: {
                API_BASE_URL: 'http://localhost:8000',
                API_DOCS_URL: 'http://localhost:8000/docs',
                WEBSOCKET_URL: 'ws://localhost:8000/ws',
                ENVIRONMENT: 'development',
                DEBUG: true
            },
            heroku: {
                API_BASE_URL: 'https://punjab-rozgar-api.herokuapp.com',
                API_DOCS_URL: 'https://punjab-rozgar-api.herokuapp.com/docs',
                WEBSOCKET_URL: 'wss://punjab-rozgar-api.herokuapp.com/ws',
                ENVIRONMENT: 'production',
                DEBUG: false
            },
            vercel: {
                API_BASE_URL: 'https://punjab-rozgar-api.up.railway.app',
                API_DOCS_URL: 'https://punjab-rozgar-api.up.railway.app/docs',
                WEBSOCKET_URL: 'wss://punjab-rozgar-api.up.railway.app/ws',
                ENVIRONMENT: 'production',
                DEBUG: false
            },
            railway: {
                API_BASE_URL: 'https://punjab-rozgar-api.up.railway.app',
                API_DOCS_URL: 'https://punjab-rozgar-api.up.railway.app/docs',
                WEBSOCKET_URL: 'wss://punjab-rozgar-api.up.railway.app/ws',
                ENVIRONMENT: 'production',
                DEBUG: false
            },
            render: {
                API_BASE_URL: 'https://punjab-rozgar-api.onrender.com',
                API_DOCS_URL: 'https://punjab-rozgar-api.onrender.com/docs',
                WEBSOCKET_URL: 'wss://punjab-rozgar-api.onrender.com/ws',
                ENVIRONMENT: 'production',
                DEBUG: false
            },
            production: {
                API_BASE_URL: 'https://api.punjabrozgar.gov.pk', // Update with your domain
                API_DOCS_URL: 'https://api.punjabrozgar.gov.pk/docs',
                WEBSOCKET_URL: 'wss://api.punjabrozgar.gov.pk/ws',
                ENVIRONMENT: 'production',
                DEBUG: false
            }
        };

        return configs[this.environment] || configs.production;
    }

    // Getter methods for easy access
    get apiUrl() { return this.config.API_BASE_URL; }
    get docsUrl() { return this.config.API_DOCS_URL; }
    get wsUrl() { return this.config.WEBSOCKET_URL; }
    get env() { return this.config.ENVIRONMENT; }
    get isDebug() { return this.config.DEBUG; }
    get isDevelopment() { return this.environment === 'development'; }
    get isProduction() { return this.environment !== 'development'; }

    // Update API URL for specific deployment
    setCustomApiUrl(url) {
        this.config.API_BASE_URL = url;
        this.config.API_DOCS_URL = `${url}/docs`;
        this.config.WEBSOCKET_URL = url.replace('http', 'ws') + '/ws';
    }

    // Log configuration for debugging
    logConfig() {
        if (this.isDebug) {
            console.log('🔧 Environment Configuration:', {
                environment: this.environment,
                apiUrl: this.apiUrl,
                config: this.config
            });
        }
    }
}

// Create global instance
window.ENV_CONFIG = new EnvironmentConfig();

// Auto-log configuration in development
if (window.ENV_CONFIG.isDevelopment) {
    window.ENV_CONFIG.logConfig();
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EnvironmentConfig;
}