@echo off
echo 🚀 Starting Contract Intelligence Parser System
echo ==============================================

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ docker-compose is not installed. Please install docker-compose first.
    pause
    exit /b 1
)

echo 📦 Building and starting services...
docker-compose up --build -d

echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

echo 🔍 Checking service health...

REM Check if backend is responding
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend is running on http://localhost:8000
) else (
    echo ❌ Backend is not responding
)

REM Check if frontend is responding
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Frontend is running on http://localhost:3000
) else (
    echo ❌ Frontend is not responding
)

echo.
echo 🎉 System is ready!
echo.
echo 📱 Web Interface: http://localhost:3000
echo 🔧 API Documentation: http://localhost:8000/docs
echo 🗄️  MongoDB: localhost:27017
echo.
echo To run tests: python test_system.py
echo To stop services: docker-compose down
echo To view logs: docker-compose logs -f
echo.
pause
