#!/bin/bash

# EZCare Production Deployment Script

set -e

echo "🚀 EZCare Production Deployment"
echo "================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check which Docker Compose version is available
COMPOSE_CMD=""
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ Docker Compose is not available. Please install Docker Compose."
    echo "   You can use either:"
    echo "   - docker-compose (standalone)"
    echo "   - docker compose (built into Docker)"
    exit 1
fi

echo "ℹ️  Using Docker Compose command: $COMPOSE_CMD"

# Check if we need sudo for Docker commands
DOCKER_CMD="docker"

if ! docker ps &> /dev/null; then
    if sudo docker ps &> /dev/null; then
        echo "⚠️  Docker requires sudo privileges. Using sudo for Docker commands."
        DOCKER_CMD="sudo docker"
        # Update compose command with sudo
        if [[ $COMPOSE_CMD == "docker-compose" ]]; then
            COMPOSE_CMD="sudo docker-compose"
        else
            COMPOSE_CMD="sudo docker compose"
        fi
    else
        echo "❌ Cannot access Docker daemon. Please ensure Docker is running and you have proper permissions."
        echo "   Try: sudo usermod -aG docker $USER"
        echo "   Then log out and log back in, or run: newgrp docker"
        exit 1
    fi
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env file with your production values before continuing."
    echo "   Important: Update database passwords, secret keys, and API keys."
    read -p "Press Enter to continue after editing .env file..."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p backend/static/uploads
mkdir -p backend/chroma_db

# Clean up any existing containers and volumes for fresh start
echo "🧹 Cleaning up existing deployment..."
$COMPOSE_CMD down --volumes --remove-orphans > /dev/null 2>&1 || true

# Build and start services
echo "🏗️  Building Docker images..."
$COMPOSE_CMD build --no-cache

echo "🚀 Starting services..."
$COMPOSE_CMD up -d

# Wait for database to be ready first
echo "⏳ Waiting for database to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if $COMPOSE_CMD exec db pg_isready -U ezcare_user -d ezcare -h localhost > /dev/null 2>&1; then
        echo "✅ Database is ready"
        break
    fi
    echo "⏳ Database not ready yet, waiting... ($((RETRY_COUNT + 1))/$MAX_RETRIES)"
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ Database failed to become ready after $MAX_RETRIES attempts"
    $COMPOSE_CMD logs db
    exit 1
fi

# Wait a bit more for backend to initialize
echo "⏳ Waiting for backend to initialize..."
sleep 10

# Check service health with proper health endpoints
echo "🔍 Checking service health..."

# Check database connection
if $COMPOSE_CMD ps db | grep -q "Up"; then
    echo "✅ Database container is running"
else
    echo "❌ Database container failed to start"
    $COMPOSE_CMD logs db
    exit 1
fi

# Check backend health endpoint
MAX_RETRIES=15
RETRY_COUNT=0
echo "⏳ Waiting for backend to be healthy..."

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:5000/health | grep -q "healthy" > /dev/null 2>&1; then
        echo "✅ Backend is healthy"
        break
    fi
    echo "⏳ Backend not healthy yet, waiting... ($((RETRY_COUNT + 1))/$MAX_RETRIES)"
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ Backend failed to become healthy"
    $COMPOSE_CMD logs backend
    exit 1
fi

# Check frontend
if $COMPOSE_CMD ps frontend | grep -q "Up"; then
    echo "✅ Frontend container is running"
else
    echo "❌ Frontend failed to start"
    $COMPOSE_CMD logs frontend
    exit 1
fi

# Check if Caddy is running
if $COMPOSE_CMD ps caddy | grep -q "Up"; then
    echo "✅ Caddy proxy is running"
else
    echo "❌ Caddy proxy failed to start"
    $COMPOSE_CMD logs caddy
    exit 1
fi

# Initialize database tables with better error handling
echo "🗄️  Initializing database tables..."
if $COMPOSE_CMD exec backend python -c "
from app import create_app
from app.models import db
import sys

try:
    print('Creating database tables...')
    app = create_app()
    with app.app_context():
        db.create_all()
        print('✅ Database tables initialized successfully!')
        sys.exit(0)
except Exception as e:
    print(f'❌ Error initializing database: {e}')
    sys.exit(1)
"; then
    echo "✅ Database tables initialized successfully"
else
    echo "❌ Database initialization failed, restarting backend..."
    $COMPOSE_CMD restart backend
    sleep 5
    
    # Retry database initialization after restart
    if $COMPOSE_CMD exec backend python -c "
from app import create_app
from app.models import db
print('Retrying database table creation...')
app = create_app()
with app.app_context():
    db.create_all()
    print('✅ Database tables initialized successfully!')
"; then
        echo "✅ Database tables initialized successfully after restart"
    else
        echo "❌ Database initialization failed even after restart"
        $COMPOSE_CMD logs backend
        exit 1
    fi
fi

# Final health check to ensure everything is working
echo "🔍 Final health verification..."
if curl -s http://localhost:5000/health | grep -q "healthy"; then
    echo "✅ Final backend health check passed"
else
    echo "⚠️  Backend health check failed, restarting backend once more..."
    $COMPOSE_CMD restart backend
    sleep 10
    if curl -s http://localhost:5000/health | grep -q "healthy"; then
        echo "✅ Backend healthy after final restart"
    else
        echo "❌ Backend still not healthy"
        exit 1
    fi
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📍 Access your application:"
echo "   Frontend: http://localhost:8080"
echo "   Backend API: http://localhost:5000"
echo "   GraphQL Playground: http://localhost:5000/graphql"
echo ""
echo "🔧 Management commands:"
echo "   View logs: $COMPOSE_CMD logs -f [service_name]"
echo "   Stop services: $COMPOSE_CMD down"
echo "   Restart services: $COMPOSE_CMD restart"
echo "   Update services: ./deploy.sh"
echo ""
echo "📊 Monitor your services with:"
echo "   $COMPOSE_CMD ps"
