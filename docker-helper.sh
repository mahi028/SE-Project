#!/bin/bash

# Docker Helper Script for EZCare
# This script helps users who need to run Docker with sudo

echo "🐳 EZCare Docker Helper"
echo "======================="

# Check if we need sudo for Docker commands
DOCKER_CMD="docker"
COMPOSE_CMD=""

# Detect which Docker Compose version is available
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ Docker Compose is not available"
    exit 1
fi

if ! docker ps &> /dev/null; then
    if sudo docker ps &> /dev/null; then
        echo "ℹ️  Note: Using sudo for Docker commands"
        DOCKER_CMD="sudo docker"
        # Update compose command with sudo
        if [[ $COMPOSE_CMD == "docker-compose" ]]; then
            COMPOSE_CMD="sudo docker-compose"
        else
            COMPOSE_CMD="sudo docker compose"
        fi
    else
        echo "❌ Cannot access Docker daemon. Please ensure:"
        echo "   1. Docker is installed and running"
        echo "   2. Your user has Docker permissions, or"
        echo "   3. You can run Docker with sudo"
        echo ""
        echo "To add your user to the docker group:"
        echo "   sudo usermod -aG docker $USER"
        echo "   newgrp docker  # or log out and back in"
        exit 1
    fi
fi

# Function to show available commands
show_commands() {
    echo ""
    echo "📋 Available commands:"
    echo "   up        - Start all services"
    echo "   down      - Stop all services"
    echo "   restart   - Restart all services"
    echo "   logs      - View logs (add service name for specific service)"
    echo "   ps        - Show running containers"
    echo "   build     - Build all images"
    echo "   shell     - Open shell in backend container"
    echo "   dbshell   - Open database shell"
    echo "   health    - Run health check"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo "Example: $0 logs backend"
}

case "${1:-help}" in
    "up")
        echo "🚀 Starting services..."
        $COMPOSE_CMD up -d
        ;;
    "down")
        echo "🛑 Stopping services..."
        $COMPOSE_CMD down
        ;;
    "restart")
        echo "🔄 Restarting services..."
        $COMPOSE_CMD restart ${2:-}
        ;;
    "logs")
        if [ -n "$2" ]; then
            echo "📋 Showing logs for $2..."
            $COMPOSE_CMD logs -f "$2"
        else
            echo "📋 Showing all logs..."
            $COMPOSE_CMD logs -f
        fi
        ;;
    "ps")
        echo "📊 Container status:"
        $COMPOSE_CMD ps
        ;;
    "build")
        echo "🏗️  Building images..."
        $COMPOSE_CMD build ${2:-}
        ;;
    "shell")
        echo "💻 Opening backend shell..."
        $COMPOSE_CMD exec backend bash
        ;;
    "dbshell")
        echo "🗄️  Opening database shell..."
        $COMPOSE_CMD exec db psql -U ezcare_user -d ezcare
        ;;
    "health")
        echo "🏥 Running health check..."
        ./health-check.sh
        ;;
    "help"|*)
        show_commands
        ;;
esac
