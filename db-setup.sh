#!/bin/bash

# Database initialization and migration script

set -e

echo "🗄️  EZCare Database Setup"
echo "========================"

# Check which Docker Compose version is available
COMPOSE_CMD=""
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
        echo "⚠️  Using sudo for Docker commands"
        # Update compose command with sudo
        if [[ $COMPOSE_CMD == "docker-compose" ]]; then
            COMPOSE_CMD="sudo docker-compose"
        else
            COMPOSE_CMD="sudo docker compose"
        fi
    else
        echo "❌ Cannot access Docker daemon"
        exit 1
    fi
fi

# Function to wait for database to be ready
wait_for_db() {
    echo "⏳ Waiting for database to be ready..."
    until $COMPOSE_CMD exec db pg_isready -U ezcare_user -d ezcare; do
        echo "Waiting for database..."
        sleep 2
    done
    echo "✅ Database is ready!"
}

# Function to run database migrations
run_migrations() {
    echo "🔄 Running database migrations..."
    $COMPOSE_CMD exec backend flask db upgrade
    echo "✅ Migrations completed!"
}

# Function to initialize database
init_database() {
    echo "🏗️  Initializing database schema..."
    $COMPOSE_CMD exec backend python -c "
from app import create_app
from app.models import db

app = create_app()
with app.app_context():
    db.create_all()
    print('Database initialized successfully!')
"
    echo "✅ Database initialization completed!"
}

# Main execution
if [ "$1" = "init" ]; then
    wait_for_db
    init_database
elif [ "$1" = "migrate" ]; then
    wait_for_db
    run_migrations
elif [ "$1" = "reset" ]; then
    echo "⚠️  This will destroy all data! Are you sure? (y/N)"
    read -r response
    if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
        echo "🗑️  Resetting database..."
        $COMPOSE_CMD down
        sudo docker volume rm se-project_postgres_data 2>/dev/null || true
        $COMPOSE_CMD up -d db
        wait_for_db
        init_database
        echo "✅ Database reset completed!"
    else
        echo "❌ Database reset cancelled."
    fi
else
    echo "Usage: $0 {init|migrate|reset}"
    echo ""
    echo "Commands:"
    echo "  init    - Initialize database schema"
    echo "  migrate - Run database migrations"
    echo "  reset   - Reset database (destroys all data)"
    exit 1
fi
