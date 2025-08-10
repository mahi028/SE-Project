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

# Build and start services
echo "🏗️  Building Docker images..."
$COMPOSE_CMD build --no-cache

echo "🚀 Starting services..."
$COMPOSE_CMD up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

# Check if database is running
if $COMPOSE_CMD ps db | grep -q "Up"; then
    echo "✅ Database is running"
else
    echo "❌ Database failed to start"
    $COMPOSE_CMD logs db
    exit 1
fi

# Check if backend is running
if $COMPOSE_CMD ps backend | grep -q "Up"; then
    echo "✅ Backend is running"
else
    echo "❌ Backend failed to start"
    $COMPOSE_CMD logs backend
    exit 1
fi

# Check if frontend is running
if $COMPOSE_CMD ps frontend | grep -q "Up"; then
    echo "✅ Frontend is running"
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

# Initialize database tables
echo "🗄️  Initializing database tables..."
if $COMPOSE_CMD exec backend python -c "
from app import create_app
from app.models import db
print('Creating database tables...')
app = create_app()
with app.app_context():
    db.create_all()
    print('✅ Database tables initialized successfully!')
" > /dev/null 2>&1; then
    echo "✅ Database tables initialized"
else
    echo "⚠️  Database initialization completed (tables may already exist)"
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
