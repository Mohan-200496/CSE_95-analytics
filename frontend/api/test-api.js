/**
 * Test script to verify Punjab Rozgar API functionality
 */

const http = require('http');

const API_BASE = 'http://localhost:3001';

async function testAPI() {
    console.log('🧪 Testing Punjab Rozgar API...\n');

    const tests = [
        { name: 'Get All Jobs', endpoint: '/jobs' },
        { name: 'Get Government Jobs', endpoint: '/jobs?category=Government%20Jobs' },
        { name: 'Get Recommended Jobs', endpoint: '/jobs/recommended' },
        { name: 'Get Categories', endpoint: '/categories' },
        { name: 'Get Locations', endpoint: '/locations' },
        { name: 'Search Jobs', endpoint: '/jobs?search=developer' }
    ];

    for (const test of tests) {
        try {
            const response = await fetch(API_BASE + test.endpoint);
            const data = await response.json();
            
            if (response.ok) {
                console.log(`✅ ${test.name}: OK (${Array.isArray(data) ? data.length : (data.jobs ? data.jobs.length : 'N/A')} items)`);
            } else {
                console.log(`❌ ${test.name}: FAILED - ${data.error || 'Unknown error'}`);
            }
        } catch (error) {
            console.log(`❌ ${test.name}: ERROR - ${error.message}`);
        }
    }

    console.log('\n🎯 API testing completed!');
}

// Simple fetch polyfill for Node.js
if (typeof fetch === 'undefined') {
    global.fetch = function(url) {
        return new Promise((resolve, reject) => {
            const req = http.get(url, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                    resolve({
                        ok: res.statusCode >= 200 && res.statusCode < 300,
                        status: res.statusCode,
                        json: () => Promise.resolve(JSON.parse(data))
                    });
                });
            });
            req.on('error', reject);
        });
    };
}

// Run tests
testAPI().catch(console.error);