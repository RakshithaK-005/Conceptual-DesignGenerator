@echo off
REM Architecture Design Generator - Startup Script for Windows

echo.
echo 🏗️  Starting AI Architectural Design Generator Backend...
echo.

REM Check if .env exists
if not exist .env (
    echo ⚠️  .env file not found. Copying from .env.example...
    copy .env.example .env
    echo 📝 Please edit .env with your configuration and run this script again.
    pause
    exit /b 1
)

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker.
    pause
    exit /b 1
)

echo 🐳 Using Docker Compose...

REM Build and start services
echo 🔨 Building Docker images...
docker-compose build

if errorlevel 1 (
    echo ❌ Build failed!
    pause
    exit /b 1
)

echo 🚀 Starting services...
docker-compose up -d

if errorlevel 1 (
    echo ❌ Failed to start services!
    pause
    exit /b 1
)

REM Wait for services
echo ⏳ Waiting for services to be healthy...
timeout /t 10

REM Check API health
echo 🏥 Checking API health...
setlocal enabledelayedexpansion
for /l %%i in (1,1,30) do (
    curl -f http://localhost:8000/health >nul 2>&1
    if errorlevel 0 (
        echo ✅ API is healthy!
        goto healthy
    )
    echo Attempt %%i/30 - Waiting for API...
    timeout /t 2 /nobreak
)

:healthy
echo.
echo ════════════════════════════════════════════════════════════
echo ✅ Services are running!
echo ════════════════════════════════════════════════════════════
echo.
echo 🌐 API Endpoints:
echo    - API: http://localhost:8000
echo    - API Docs: http://localhost:8000/docs
echo    - Database: localhost:5432
echo    - pgAdmin: http://localhost:5050
echo.
echo 🔧 Useful Commands:
echo    - View logs: docker-compose logs -f api
echo    - Stop services: docker-compose down
echo.
echo ════════════════════════════════════════════════════════════
echo.
pause
