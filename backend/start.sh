#!/bin/bash

# Architecture Design Generator - Startup Script

set -e

echo "🏗️  Starting AI Architectural Design Generator Backend..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env with your configuration and run this script again."
    exit 1
fi

# Load environment variables
export $(cat .env | xargs)

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker."
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "⚠️  Docker Compose v1 not found. Checking for Docker Compose v2..."
    if ! docker compose version &> /dev/null; then
        echo "❌ Docker Compose is not installed."
        exit 1
    fi
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

echo "🐳 Using: $DOCKER_COMPOSE"

# Build and start services
echo "🔨 Building Docker images..."
$DOCKER_COMPOSE build

echo "🚀 Starting services..."
$DOCKER_COMPOSE up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check API health
echo "🏥 Checking API health..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health 2>/dev/null; then
        echo "✅ API is healthy!"
        break
    fi
    echo "Attempt $i/30 - Waiting for API..."
    sleep 2
done

# Display service information
echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ Services are running!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "🌐 API Endpoints:"
echo "   - API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Database: localhost:5432"
echo "   - pgAdmin: http://localhost:5050"
echo ""
echo "📊 Default Credentials (for pgAdmin):"
echo "   - Email: $PGADMIN_EMAIL"
echo "   - Password: $PGADMIN_PASSWORD"
echo ""
echo "💾 Database:"
echo "   - User: $DB_USER"
echo "   - Database: $DB_NAME"
echo ""
echo "🔧 Useful Commands:"
echo "   - View logs: docker-compose logs -f api"
echo "   - Stop services: docker-compose down"
echo "   - Database shell: docker-compose exec postgres psql -U $DB_USER -d $DB_NAME"
echo ""
echo "════════════════════════════════════════════════════════════"
