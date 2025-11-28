#!/bin/bash

echo "🔧 Punjab Rozgar Portal - Permanent Fixes"
echo "=========================================="

# Fix 1: Start both servers permanently
echo "Starting backend server..."
cd "$(dirname "$0")/backend"
nohup "D:/cap pro/last/capstone-analytics/.venv/Scripts/python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!

echo "Starting frontend server..."
cd ../frontend
nohup "D:/cap pro/last/capstone-analytics/.venv/Scripts/python.exe" -m http.server 3000 > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

# Save PIDs for later management
echo $BACKEND_PID > ../logs/backend.pid
echo $FRONTEND_PID > ../logs/frontend.pid

echo "✅ Backend started on port 8000 (PID: $BACKEND_PID)"
echo "✅ Frontend started on port 3000 (PID: $FRONTEND_PID)"

# Wait for servers to start
sleep 5

# Test the system
echo ""
echo "🧪 Testing system..."

# Test backend
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ Backend: ONLINE"
else
    echo "❌ Backend: OFFLINE"
fi

# Test frontend
if curl -s http://localhost:3000/ > /dev/null; then
    echo "✅ Frontend: ONLINE"
else
    echo "❌ Frontend: OFFLINE"
fi

echo ""
echo "🌐 Punjab Rozgar Portal is now running!"
echo "=================================="
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "🔑 Test Accounts:"
echo "Job Seeker: jobseeker@test.com / jobseeker123"
echo "Admin: admin@test.com / admin123"
echo "Employer: employer@test.com / test123"
echo ""
echo "📊 Logs:"
echo "Backend: logs/backend.log"
echo "Frontend: logs/frontend.log"
echo ""
echo "🛑 To stop servers:"
echo "kill $(cat logs/backend.pid) $(cat logs/frontend.pid)"

# Open browser
if command -v start >/dev/null 2>&1; then
    start http://localhost:3000
elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open http://localhost:3000
fi