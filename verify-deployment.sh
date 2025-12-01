#!/bin/bash

# Punjab Rozgar Portal - Deployment Verification Script
# This script helps verify the backend deployment and CORS configuration

echo "🔍 Punjab Rozgar Portal - Deployment Verification"
echo "================================================"

BACKEND_URL="https://cse-95-analytics.onrender.com"
FRONTEND_ORIGIN="https://punjab-rozgar-portal1.onrender.com"

echo "📡 Testing backend availability..."

# Test 1: Health check
echo "1️⃣ Testing health endpoint..."
health_response=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/health")
if [ "$health_response" = "200" ]; then
    echo "✅ Backend is online and healthy"
else
    echo "❌ Backend health check failed (HTTP $health_response)"
    echo "   💡 The service might be sleeping (Render free tier) or there's a deployment issue"
fi

# Test 2: CORS preflight
echo "2️⃣ Testing CORS preflight..."
cors_response=$(curl -s -o /dev/null -w "%{http_code}" \
    -X OPTIONS \
    -H "Origin: $FRONTEND_ORIGIN" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: Content-Type" \
    "$BACKEND_URL/api/v1/auth/login")

if [ "$cors_response" = "200" ]; then
    echo "✅ CORS preflight successful"
else
    echo "❌ CORS preflight failed (HTTP $cors_response)"
fi

# Test 3: API docs accessibility
echo "3️⃣ Testing API documentation..."
docs_response=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/docs")
if [ "$docs_response" = "200" ]; then
    echo "✅ API docs accessible"
    echo "   🔗 Visit: $BACKEND_URL/docs"
else
    echo "❌ API docs not accessible (HTTP $docs_response)"
fi

# Test 4: Login endpoint test
echo "4️⃣ Testing login functionality..."
login_response=$(curl -s -w "%{http_code}" \
    -X POST \
    -H "Content-Type: application/json" \
    -H "Origin: $FRONTEND_ORIGIN" \
    -d '{"email":"jobseeker@test.com","password":"jobseeker123"}' \
    "$BACKEND_URL/api/v1/auth/login")

if echo "$login_response" | grep -q "200$"; then
    echo "✅ Login endpoint working"
else
    echo "❌ Login endpoint failed"
    echo "   Response: $login_response"
fi

echo ""
echo "🚀 Next Steps:"
echo "1. If backend is offline/sleeping: Visit $BACKEND_URL to wake it up"
echo "2. If CORS is failing: Check Render deployment logs"
echo "3. Test with: Open test-cors.html in a browser"
echo "4. Frontend test: https://punjab-rozgar-portal1.onrender.com"

echo ""
echo "📋 Test Credentials:"
echo "   Job Seeker: jobseeker@test.com / jobseeker123"
echo "   Employer: employer@test.com / employer123"
echo "   Admin: admin@test.com / admin123"