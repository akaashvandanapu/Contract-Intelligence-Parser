#!/bin/bash

echo "🚀 Starting Contract Intelligence Parser System"
echo "=============================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

echo "📦 Building and starting services..."
docker-compose up --build -d

echo "⏳ Waiting for services to start..."
sleep 10

echo "🔍 Checking service health..."

# Check if backend is responding
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running on http://localhost:8000"
else
    echo "❌ Backend is not responding"
fi

# Check if frontend is responding
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is running on http://localhost:3000"
else
    echo "❌ Frontend is not responding"
fi

echo ""
echo "🎉 System is ready!"
echo ""
echo "📱 Web Interface: http://localhost:3000"
echo "🔧 API Documentation: http://localhost:8000/docs"
echo "🗄️  MongoDB: localhost:27017"
echo ""
echo "To run tests: python test_system.py"
echo "To stop services: docker-compose down"
echo "To view logs: docker-compose logs -f"
