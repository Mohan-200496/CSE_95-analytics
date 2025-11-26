#!/bin/bash
# Quick deployment script for Punjab Rozgar Portal

echo "🚀 Punjab Rozgar Portal - Quick Deploy"
echo "======================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "✅ Docker is running"

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found. Run this script from project root."
    exit 1
fi

echo "📦 Building and starting services..."
docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 10

# Check if backend is responding
echo "🔍 Checking backend health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "⚠️  Backend may still be starting..."
fi

echo ""
echo "🎉 Deployment Complete!"
echo "========================"
echo "📱 Frontend: http://localhost:8080"
echo "🚀 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "📊 View logs: docker-compose logs -f"
echo "🛑 Stop services: docker-compose down"